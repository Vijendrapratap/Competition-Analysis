import structlog
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brands import BrandProfile
from app.models.competitors import Competitor
from app.utils.llm import call_openrouter
from app.utils.apify import run_apify_actor

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are a competitive intelligence analyst. Given a brand's profile and search results, identify and classify potential competitors.

For each competitor found, classify as:
- direct: Head-to-head competitor in the same market
- indirect: Different product/service targeting the same audience
- aspirational: Market leader or admired brand to benchmark against
- regional: Competitor specific to the geographic region

Respond as JSON:
{
  "suggestions": [
    {
      "name": "Brand Name",
      "website": "https://example.com",
      "suggested_tier": "direct",
      "reason": "One-line explanation of why this is a competitor",
      "relevance_score": 85
    }
  ]
}

Return up to 10 suggestions, ranked by relevance_score (highest first).
Deduplicate by domain name. Exclude the user's own brand."""


async def discover_competitors(brand_id: UUID, db: AsyncSession) -> list[dict]:
    """Discover competitors using search + LLM classification."""
    stmt = select(BrandProfile).where(BrandProfile.id == brand_id)
    result = await db.execute(stmt)
    brand = result.scalar_one_or_none()
    if not brand:
        raise ValueError(f"Brand {brand_id} not found")

    # Get existing competitors as seed context
    stmt = select(Competitor).where(Competitor.brand_profile_id == brand_id)
    result = await db.execute(stmt)
    existing = result.scalars().all()
    existing_names = [c.name for c in existing]
    existing_websites = [c.website for c in existing if c.website]

    logger.info("competitor_discovery_start", brand_id=str(brand_id), existing_count=len(existing))

    # Build search queries
    queries = [
        f"{brand.industry} {brand.target_region} companies",
        f"competitors of {brand.name}",
        f"{brand.industry} brands {brand.target_region}",
    ]

    # Run Google searches via Apify
    search_results = []
    for query in queries:
        results = await run_apify_actor(
            "apify/google-search-scraper",
            {"queries": query, "maxPagesPerQuery": 1, "resultsPerPage": 10},
            timeout=60.0,
        )
        search_results.extend(results)

    # Build context for LLM
    search_context = ""
    if search_results:
        seen_urls = set()
        for r in search_results:
            url = r.get("url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            search_context += f"- {r.get('title', 'No title')} | {url} | {r.get('description', '')}\n"
    else:
        search_context = "No search results available. Use your knowledge of the industry to suggest competitors."

    seed_context = ""
    if existing_names:
        seed_context = f"\n\nAlready known competitors (use as reference points): {', '.join(existing_names)}"

    persona_context = ""
    if brand.persona:
        persona_context = f"\nBrand positioning: {brand.persona.get('market_positioning', '')}"

    user_prompt = f"""Brand: {brand.name}
Industry: {brand.industry}
Region: {brand.target_region}
Website: {brand.website}
{persona_context}
{seed_context}

Search results:
{search_context}

Identify up to 10 competitors. Exclude these already-added brands: {', '.join(existing_names) if existing_names else 'none'}.
Exclude domains: {', '.join(existing_websites) if existing_websites else 'none'} and {brand.website}."""

    try:
        response = await call_openrouter(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model="google/gemini-2.5-pro",
        )

        suggestions = response.get("suggestions", [])
        # Sort by relevance_score
        suggestions.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        logger.info("competitor_discovery_complete", brand_id=str(brand_id), count=len(suggestions))
        return suggestions[:10]

    except Exception as e:
        logger.error("competitor_discovery_failed", brand_id=str(brand_id), error=str(e))
        return []
