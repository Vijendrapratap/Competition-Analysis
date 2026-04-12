"""
Customer review collection activity.

Scrapes G2, Capterra, and App Store reviews for competitors via Apify.
Stores individual reviews and computes aggregate sentiment/rating snapshots.
"""
import uuid
from datetime import datetime, timezone

from temporalio import activity
from sqlalchemy import select, func

from app.database import async_session
from app.models.reviews import CompetitorReview, ReviewAggregate, ReviewPlatform
from app.utils.apify import run_apify_actor
from app.utils.llm import call_openrouter


@activity.defn
async def collect_review_data(
    competitor_id: str,
    brand_profile_id: str,
    competitor_name: str,
    g2_slug: str | None = None,
    capterra_slug: str | None = None,
) -> dict:
    """Scrape reviews from G2 and Capterra, aggregate sentiment."""
    activity.logger.info(f"Collecting reviews for {competitor_id}: {competitor_name}")
    comp_uuid = uuid.UUID(competitor_id)
    brand_uuid = uuid.UUID(brand_profile_id)

    total_reviews = 0

    async with async_session() as db:
        # ── G2 Reviews ──
        if g2_slug:
            g2_results = await run_apify_actor(
                "tri_angle/g2-reviews-scraper",
                {
                    "productSlug": g2_slug,
                    "maxReviews": 50,
                },
                timeout=180.0,
            )
            for item in g2_results:
                review = CompetitorReview(
                    competitor_id=comp_uuid,
                    platform=ReviewPlatform.g2,
                    external_id=item.get("id") or item.get("reviewId"),
                    rating=float(item.get("rating") or item.get("starRating") or 0),
                    title=item.get("title"),
                    body=(item.get("text") or item.get("body") or "")[:5000],
                    reviewer_role=item.get("reviewerTitle") or item.get("jobTitle"),
                    reviewer_company_size=item.get("companySize"),
                    helpful_count=item.get("helpfulCount") or 0,
                    published_at=_parse_date(item.get("createdAt") or item.get("date")),
                    pros=item.get("pros"),
                    cons=item.get("cons"),
                    collected_at=datetime.now(timezone.utc),
                )
                db.add(review)
                total_reviews += 1

        # ── Capterra Reviews ──
        if capterra_slug:
            capterra_results = await run_apify_actor(
                "apify/capterra-reviews-scraper",
                {
                    "startUrls": [{"url": f"https://www.capterra.com/reviews/{capterra_slug}"}],
                    "maxReviews": 50,
                },
                timeout=180.0,
            )
            for item in capterra_results:
                review = CompetitorReview(
                    competitor_id=comp_uuid,
                    platform=ReviewPlatform.capterra,
                    external_id=item.get("id"),
                    rating=float(item.get("overallRating") or item.get("rating") or 0),
                    title=item.get("title"),
                    body=(item.get("reviewBody") or item.get("text") or "")[:5000],
                    reviewer_role=item.get("jobTitle"),
                    reviewer_company_size=item.get("companySize"),
                    helpful_count=item.get("helpfulCount") or 0,
                    published_at=_parse_date(item.get("date")),
                    pros=item.get("pros"),
                    cons=item.get("cons"),
                    collected_at=datetime.now(timezone.utc),
                )
                db.add(review)
                total_reviews += 1

        await db.flush()

        # ── Aggregate sentiment via LLM (if enough reviews) ──
        if total_reviews >= 5:
            stmt = (
                select(CompetitorReview)
                .where(CompetitorReview.competitor_id == comp_uuid)
                .order_by(CompetitorReview.published_at.desc())
                .limit(30)
            )
            result = await db.execute(stmt)
            recent_reviews = list(result.scalars().all())

            review_texts = []
            for r in recent_reviews[:20]:
                parts = []
                if r.title:
                    parts.append(f"Title: {r.title}")
                if r.pros:
                    parts.append(f"Pros: {r.pros}")
                if r.cons:
                    parts.append(f"Cons: {r.cons}")
                if parts:
                    review_texts.append(f"[{r.rating}★] " + " | ".join(parts))

            if review_texts:
                try:
                    sentiment = await call_openrouter(
                        system_prompt=(
                            "You are a product review analyst. Analyze these customer reviews and extract: "
                            "top praised features, top pain points, and positioning gaps the brand could exploit. "
                            "Respond as JSON: {\"avg_rating\": 4.2, \"top_praises\": [\"...\"], "
                            "\"top_complaints\": [\"...\"], \"positioning_gaps\": [\"...\"], "
                            "\"sentiment_score\": 0.7, \"review_summary\": \"...\"}"
                        ),
                        user_prompt="\n\n".join(review_texts),
                        model="google/gemini-2.0-flash",
                    )

                    # Compute avg rating
                    ratings = [r.rating for r in recent_reviews if r.rating]
                    avg_rating = sum(ratings) / len(ratings) if ratings else None

                    # Count per-platform
                    from sqlalchemy import case
                    stmt = select(
                        CompetitorReview.platform,
                        func.count().label("cnt"),
                        func.avg(CompetitorReview.rating).label("avg"),
                    ).where(
                        CompetitorReview.competitor_id == comp_uuid
                    ).group_by(CompetitorReview.platform)
                    result = await db.execute(stmt)
                    platform_breakdown = {str(row[0]): {"count": row[1], "avg_rating": float(row[2] or 0)} for row in result.all()}

                    aggregate = ReviewAggregate(
                        competitor_id=comp_uuid,
                        brand_profile_id=brand_uuid,
                        total_reviews=total_reviews,
                        avg_rating=avg_rating,
                        sentiment_score=sentiment.get("sentiment_score"),
                        top_praises=sentiment.get("top_praises", []),
                        top_complaints=sentiment.get("top_complaints", []),
                        positioning_gaps=sentiment.get("positioning_gaps", []),
                        review_summary=sentiment.get("review_summary"),
                        platform_breakdown=platform_breakdown,
                        computed_at=datetime.now(timezone.utc),
                    )
                    db.add(aggregate)
                except Exception as e:
                    activity.logger.warning(f"Review sentiment LLM failed: {e}")

        await db.commit()

    return {
        "status": "ok",
        "reviews_collected": total_reviews,
    }


def _parse_date(val) -> datetime | None:
    if not val:
        return None
    try:
        return datetime.fromisoformat(str(val).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
