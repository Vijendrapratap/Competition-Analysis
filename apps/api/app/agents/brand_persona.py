import structlog
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brands import BrandProfile
from app.utils.llm import call_openrouter
from app.utils.firecrawl import crawl_url

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are a brand strategist analyzing a company's market positioning. Based on the provided information, generate a structured brand persona.

Respond in this exact JSON structure:
{
  "brand_voice": "2-3 word descriptor + one sentence explanation",
  "core_audience": "Demographics + psychographics in one sentence",
  "value_propositions": ["prop1", "prop2", "prop3"],
  "market_positioning": "One sentence positioning statement",
  "key_channels": ["channel1", "channel2", "channel3"],
  "content_style": "2-3 sentence description of likely content approach"
}"""


async def generate_brand_persona(brand_id: UUID, db: AsyncSession) -> dict:
    """Generate a brand persona using website crawl + LLM analysis."""
    stmt = select(BrandProfile).where(BrandProfile.id == brand_id)
    result = await db.execute(stmt)
    brand = result.scalar_one_or_none()
    if not brand:
        raise ValueError(f"Brand {brand_id} not found")

    logger.info("persona_generation_start", brand_id=str(brand_id), brand_name=brand.name)

    # Step 1: Crawl website if available
    website_content = ""
    if brand.website:
        pages = await crawl_url(brand.website, max_pages=3)
        if pages:
            website_content = "\n\n".join(
                f"[Page: {p['url']}]\n{p['markdown'][:3000]}" for p in pages
            )

    # Step 2: Build context
    social_info = ""
    if brand.social_profiles:
        sp = brand.social_profiles
        parts = []
        if sp.get("facebook_url"):
            parts.append(f"Facebook: {sp['facebook_url']}")
        if sp.get("instagram_handle"):
            parts.append(f"Instagram: {sp['instagram_handle']}")
        if sp.get("linkedin_url"):
            parts.append(f"LinkedIn: {sp['linkedin_url']}")
        if sp.get("youtube_url"):
            parts.append(f"YouTube: {sp['youtube_url']}")
        social_info = "\n".join(parts)

    user_prompt = f"""Brand Name: {brand.name}
Industry: {brand.industry}
Target Region: {brand.target_region}
Target Audience Description: {brand.target_audience or 'Not specified'}

Social Profiles:
{social_info or 'None provided'}

Website Content:
{website_content or 'Not available — generate persona based on other available information'}"""

    # Step 3: Call LLM
    try:
        persona = await call_openrouter(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model="google/gemini-2.5-pro",
        )

        # Validate structure
        required_keys = ["brand_voice", "core_audience", "value_propositions",
                         "market_positioning", "key_channels", "content_style"]
        for key in required_keys:
            if key not in persona:
                raise ValueError(f"Missing key in persona: {key}")

        # Save to brand
        brand.persona = persona
        await db.flush()

        logger.info("persona_generation_complete", brand_id=str(brand_id))
        return persona

    except Exception as e:
        logger.error("persona_generation_failed", brand_id=str(brand_id), error=str(e))
        raise
