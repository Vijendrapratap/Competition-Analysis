"""
Pricing intelligence router.

GET  /competitors/{comp_id}/pricing         → latest pricing snapshot + tiers
GET  /competitors/{comp_id}/pricing/history → pricing change log
GET  /brands/{brand_id}/pricing/matrix      → side-by-side pricing comparison
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import AccountId

router = APIRouter()


@router.get("/competitors/{competitor_id}/pricing")
async def get_competitor_pricing(
    competitor_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.pricing import PricingPage, PricingTier
        from sqlalchemy.orm import selectinload

        stmt = (
            select(PricingPage)
            .options(selectinload(PricingPage.tiers))
            .where(PricingPage.competitor_id == competitor_id)
            .order_by(desc(PricingPage.scraped_at))
            .limit(1)
        )
        result = await db.execute(stmt)
        page = result.scalar_one_or_none()
        if not page:
            return {"pricing": None, "tiers": []}

        return {
            "pricing": {
                "url": page.url,
                "pricing_model": str(page.pricing_model),
                "has_free_tier": page.has_free_tier,
                "has_enterprise": page.has_enterprise,
                "currency": page.currency,
                "pricing_notes": page.pricing_notes,
                "scraped_at": page.scraped_at.isoformat() if page.scraped_at else None,
            },
            "tiers": [
                {
                    "name": t.tier_name,
                    "price": float(t.price) if t.price else None,
                    "billing_cycle": str(t.billing_cycle),
                    "features": t.features or [],
                    "is_highlighted": t.is_highlighted,
                }
                for t in (page.tiers or [])
            ],
        }
    except Exception:
        return {"pricing": None, "tiers": []}


@router.get("/competitors/{competitor_id}/pricing/history")
async def get_pricing_history(
    competitor_id: UUID,
    account_id: AccountId,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.pricing import PricingChange

        stmt = (
            select(PricingChange)
            .where(PricingChange.competitor_id == competitor_id)
            .order_by(desc(PricingChange.detected_at))
            .limit(limit)
        )
        result = await db.execute(stmt)
        changes = list(result.scalars().all())
        return {
            "changes": [
                {
                    "tier_name": c.tier_name,
                    "old_price": float(c.old_price) if c.old_price else None,
                    "new_price": float(c.new_price) if c.new_price else None,
                    "change_type": c.change_type,
                    "detected_at": c.detected_at.isoformat() if c.detected_at else None,
                }
                for c in changes
            ]
        }
    except Exception:
        return {"changes": []}


@router.get("/brands/{brand_id}/pricing/matrix")
async def get_pricing_matrix(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    """Side-by-side pricing comparison across all tracked competitors."""
    try:
        from app.models.competitors import Competitor
        from app.models.pricing import PricingPage, PricingTier
        from sqlalchemy.orm import selectinload

        # Get all active competitors for this brand
        stmt = select(Competitor).where(
            Competitor.brand_profile_id == brand_id,
            Competitor.active == True,
        )
        result = await db.execute(stmt)
        competitors = list(result.scalars().all())

        matrix = []
        for comp in competitors:
            stmt = (
                select(PricingPage)
                .options(selectinload(PricingPage.tiers))
                .where(PricingPage.competitor_id == comp.id)
                .order_by(desc(PricingPage.scraped_at))
                .limit(1)
            )
            result = await db.execute(stmt)
            page = result.scalar_one_or_none()

            matrix.append({
                "competitor_id": str(comp.id),
                "competitor_name": comp.name,
                "pricing_model": str(page.pricing_model) if page else None,
                "has_free_tier": page.has_free_tier if page else None,
                "has_enterprise": page.has_enterprise if page else None,
                "currency": page.currency if page else "USD",
                "tiers": [
                    {
                        "name": t.tier_name,
                        "price": float(t.price) if t.price else None,
                        "billing_cycle": str(t.billing_cycle),
                    }
                    for t in (page.tiers or [])
                ] if page else [],
                "last_updated": page.scraped_at.isoformat() if page and page.scraped_at else None,
            })

        return {"matrix": matrix, "competitor_count": len(matrix)}
    except Exception:
        return {"matrix": [], "competitor_count": 0}
