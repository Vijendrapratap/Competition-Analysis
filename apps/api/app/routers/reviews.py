"""
Reviews router.

GET  /competitors/{comp_id}/reviews              → paginated reviews
GET  /competitors/{comp_id}/reviews/aggregate    → sentiment aggregate
GET  /brands/{brand_id}/reviews/comparison       → cross-competitor review comparison
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import AccountId

router = APIRouter()


@router.get("/competitors/{competitor_id}/reviews")
async def get_reviews(
    competitor_id: UUID,
    account_id: AccountId,
    platform: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.reviews import CompetitorReview, ReviewPlatform

        stmt = (
            select(CompetitorReview)
            .where(CompetitorReview.competitor_id == competitor_id)
        )
        if platform:
            try:
                stmt = stmt.where(CompetitorReview.platform == ReviewPlatform(platform))
            except ValueError:
                pass

        stmt = stmt.order_by(desc(CompetitorReview.published_at)).offset(offset).limit(limit)
        result = await db.execute(stmt)
        reviews = list(result.scalars().all())

        return {
            "reviews": [
                {
                    "id": str(r.id),
                    "platform": str(r.platform),
                    "rating": float(r.rating) if r.rating else None,
                    "title": r.title,
                    "body": r.body,
                    "pros": r.pros,
                    "cons": r.cons,
                    "reviewer_role": r.reviewer_role,
                    "reviewer_company_size": r.reviewer_company_size,
                    "sentiment_score": float(r.sentiment_score) if r.sentiment_score else None,
                    "sentiment_label": r.sentiment_label,
                    "published_at": r.published_at.isoformat() if r.published_at else None,
                }
                for r in reviews
            ],
            "limit": limit,
            "offset": offset,
        }
    except Exception:
        return {"reviews": [], "limit": limit, "offset": offset}


@router.get("/competitors/{competitor_id}/reviews/aggregate")
async def get_review_aggregate(
    competitor_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.reviews import ReviewAggregate

        stmt = (
            select(ReviewAggregate)
            .where(ReviewAggregate.competitor_id == competitor_id)
            .order_by(desc(ReviewAggregate.computed_at))
            .limit(1)
        )
        result = await db.execute(stmt)
        agg = result.scalar_one_or_none()
        if not agg:
            return {"aggregate": None}

        return {
            "aggregate": {
                "total_reviews": agg.total_reviews,
                "avg_rating": float(agg.avg_rating) if agg.avg_rating else None,
                "sentiment_score": float(agg.sentiment_score) if agg.sentiment_score else None,
                "top_praises": agg.top_praises or [],
                "top_complaints": agg.top_complaints or [],
                "positioning_gaps": agg.positioning_gaps or [],
                "review_summary": agg.review_summary,
                "platform_breakdown": agg.platform_breakdown or {},
                "computed_at": agg.computed_at.isoformat() if agg.computed_at else None,
            }
        }
    except Exception:
        return {"aggregate": None}


@router.get("/brands/{brand_id}/reviews/comparison")
async def get_review_comparison(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    """Cross-competitor review comparison for brand."""
    try:
        from app.models.reviews import ReviewAggregate
        from app.models.competitors import Competitor

        stmt = select(Competitor).where(
            Competitor.brand_profile_id == brand_id,
            Competitor.active == True,
        )
        result = await db.execute(stmt)
        competitors = list(result.scalars().all())

        comparison = []
        for comp in competitors:
            stmt = (
                select(ReviewAggregate)
                .where(ReviewAggregate.competitor_id == comp.id)
                .order_by(desc(ReviewAggregate.computed_at))
                .limit(1)
            )
            result = await db.execute(stmt)
            agg = result.scalar_one_or_none()

            comparison.append({
                "competitor_id": str(comp.id),
                "competitor_name": comp.name,
                "total_reviews": agg.total_reviews if agg else 0,
                "avg_rating": float(agg.avg_rating) if agg and agg.avg_rating else None,
                "sentiment_score": float(agg.sentiment_score) if agg and agg.sentiment_score else None,
                "top_praises": (agg.top_praises or [])[:3] if agg else [],
                "top_complaints": (agg.top_complaints or [])[:3] if agg else [],
            })

        return {"comparison": comparison}
    except Exception:
        return {"comparison": []}
