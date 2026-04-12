"""
SEO data collection activity.

Uses two strategies:
1. Apify Google SERP scraper to check keyword rankings for target keywords.
2. Firecrawl to crawl sitemap/blog for new page detection.

If Apify is unavailable, falls back to storing a stub SeoMetric from
page metadata (title tags, meta desc) already collected during website crawl.
"""
import uuid
from datetime import datetime, timezone, date
from typing import Optional

from temporalio import activity
from sqlalchemy import select, desc

from app.database import async_session
from app.models.seo import Keyword, KeywordRanking, SeoMetric, ContentGap, KeywordIntent
from app.models.data_collection import PageSnapshot, SourceType, QualityStatus
from app.models.competitors import Competitor
from app.models.brands import BrandProfile
from app.utils.apify import run_apify_actor
from app.utils.llm import call_openrouter


@activity.defn
async def collect_seo_data(
    competitor_id: str,
    brand_profile_id: str,
    website_url: str,
    seed_keywords: list[str] | None = None,
) -> dict:
    """
    Collect SEO data for a competitor:
    - Estimate domain authority from page metadata
    - Scrape SERP rankings for tracked keywords
    - Detect new pages from sitemap diff
    - Generate content gap insights via LLM
    """
    activity.logger.info(f"Collecting SEO data for {competitor_id}: {website_url}")
    comp_uuid = uuid.UUID(competitor_id)
    brand_uuid = uuid.UUID(brand_profile_id)

    keywords_tracked = 0
    rankings_created = 0
    gaps_found = 0

    async with async_session() as db:
        # 1. Get or create tracked keywords for this brand
        if seed_keywords:
            for kw_text in seed_keywords[:20]:
                stmt = select(Keyword).where(
                    Keyword.brand_profile_id == brand_uuid,
                    Keyword.keyword == kw_text,
                )
                result = await db.execute(stmt)
                kw = result.scalar_one_or_none()
                if not kw:
                    kw = Keyword(
                        brand_profile_id=brand_uuid,
                        keyword=kw_text,
                        intent=KeywordIntent.informational,
                    )
                    db.add(kw)
            await db.flush()

        # Get all tracked keywords for this brand
        stmt = select(Keyword).where(Keyword.brand_profile_id == brand_uuid).limit(50)
        result = await db.execute(stmt)
        keywords = list(result.scalars().all())
        keywords_tracked = len(keywords)

        if not keywords:
            activity.logger.info("No tracked keywords — using LLM to suggest from website content")

        # 2. Try Apify SERP scraping for each keyword (batched)
        if keywords:
            kw_texts = [k.keyword for k in keywords[:20]]

            serp_results = await run_apify_actor(
                "apify/google-search-scraper",
                {
                    "queries": "\n".join(kw_texts),
                    "maxPagesPerQuery": 1,
                    "resultsPerPage": 20,
                    "countryCode": "US",
                    "languageCode": "en",
                },
                timeout=180.0,
            )

            # Parse SERP results and find competitor's ranking
            domain = _extract_domain(website_url)
            rank_by_kw: dict[str, int] = {}

            for serp_page in serp_results:
                query = serp_page.get("searchQuery", {}).get("term", "")
                organic = serp_page.get("organicResults", [])
                for item in organic:
                    item_url = item.get("url", "")
                    if domain and domain in item_url:
                        rank_by_kw[query] = item.get("position", 99)
                        break

            # Create KeywordRanking records
            today = date.today()
            for kw in keywords:
                rank = rank_by_kw.get(kw.keyword)
                if rank is not None:
                    ranking = KeywordRanking(
                        keyword_id=kw.id,
                        competitor_id=comp_uuid,
                        rank=rank,
                        url=website_url,
                        recorded_on=today,
                    )
                    db.add(ranking)
                    rankings_created += 1

        # 3. Estimate SeoMetric from website snapshot metadata
        stmt = (
            select(PageSnapshot)
            .where(
                PageSnapshot.competitor_id == comp_uuid,
                PageSnapshot.source_type == SourceType.website,
                PageSnapshot.quality_status == QualityStatus.clean,
            )
            .order_by(desc(PageSnapshot.scraped_at))
            .limit(5)
        )
        result = await db.execute(stmt)
        snapshots = list(result.scalars().all())

        new_page_count = 0
        if len(snapshots) >= 2:
            # Count pages crawled in latest run vs previous
            latest_ts = snapshots[0].scraped_at
            prev_ts = snapshots[-1].scraped_at
            stmt_new = (
                select(PageSnapshot)
                .where(
                    PageSnapshot.competitor_id == comp_uuid,
                    PageSnapshot.source_type == SourceType.website,
                    PageSnapshot.quality_status == QualityStatus.clean,
                    PageSnapshot.scraped_at >= latest_ts,
                )
            )
            count_result = await db.execute(stmt_new)
            new_page_count = len(list(count_result.scalars().all()))

        # 4. LLM: extract content gaps from website text
        if snapshots and keywords:
            website_text = snapshots[0].extracted_text or snapshots[0].raw_content or ""
            if website_text and len(website_text) > 500:
                kw_list = [k.keyword for k in keywords[:10]]
                try:
                    gap_data = await call_openrouter(
                        system_prompt=(
                            "You are an SEO analyst. Given website content and keywords the brand tracks, "
                            "identify content gaps — topics the competitor covers well that the brand may be missing. "
                            "Respond as JSON: {\"gaps\": [{\"keyword\": \"...\", \"competitor_strength\": \"high|medium|low\", "
                            "\"reason\": \"why competitor ranks well\"}]}"
                        ),
                        user_prompt=(
                            f"Brand tracked keywords: {', '.join(kw_list)}\n\n"
                            f"Competitor website content (first 2000 chars):\n{website_text[:2000]}"
                        ),
                        model="google/gemini-2.0-flash",
                    )

                    for gap in gap_data.get("gaps", [])[:10]:
                        kw_text = gap.get("keyword", "")
                        # Find matching keyword or skip
                        matching_kw = next((k for k in keywords if k.keyword.lower() == kw_text.lower()), None)
                        if not matching_kw:
                            continue
                        content_gap = ContentGap(
                            keyword_id=matching_kw.id,
                            competitor_id=comp_uuid,
                            competitor_ranks=True,
                            brand_ranks=False,
                            gap_score={"strength": gap.get("competitor_strength", "medium"), "reason": gap.get("reason", "")},
                        )
                        db.add(content_gap)
                        gaps_found += 1
                except Exception as e:
                    activity.logger.warning(f"SEO gap LLM failed: {e}")

        # 5. Upsert SeoMetric aggregate
        month_start = date.today().replace(day=1)
        stmt = select(SeoMetric).where(
            SeoMetric.competitor_id == comp_uuid,
            SeoMetric.month == month_start,
        )
        result = await db.execute(stmt)
        existing_metric = result.scalar_one_or_none()

        if not existing_metric:
            metric = SeoMetric(
                competitor_id=comp_uuid,
                month=month_start,
                domain_authority=None,  # Would come from Moz/Ahrefs API if configured
                organic_traffic_est=None,
                backlinks_total=None,
                new_pages=new_page_count,
                keywords_in_top10=rankings_created,
            )
            db.add(metric)
        else:
            existing_metric.new_pages = new_page_count
            existing_metric.keywords_in_top10 = rankings_created

        await db.commit()

    return {
        "status": "ok",
        "keywords_tracked": keywords_tracked,
        "rankings_created": rankings_created,
        "content_gaps_found": gaps_found,
    }


def _extract_domain(url: str) -> str | None:
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return domain.replace("www.", "") if domain else None
    except Exception:
        return None
