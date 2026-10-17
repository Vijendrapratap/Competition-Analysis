from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import CurrentUser, AccountId
from app.models.brands import BrandProfile
from app.models.competitors import Competitor
from app.schemas.competitors import (
    CompetitorCreate,
    CompetitorUpdate,
    CompetitorResponse,
)

router = APIRouter()

PLAN_COMPETITOR_LIMITS = {"starter": 5, "growth": 10, "enterprise": 20}


async def _get_brand_for_account(
    brand_id: UUID, account_id: UUID, db: AsyncSession
) -> BrandProfile:
    stmt = select(BrandProfile).where(
        BrandProfile.id == brand_id,
        BrandProfile.account_id == account_id,
    )
    result = await db.execute(stmt)
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return brand


@router.get("/brands/{brand_id}/competitors", response_model=list[CompetitorResponse])
async def list_competitors(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    await _get_brand_for_account(brand_id, account_id, db)
    stmt = (
        select(Competitor)
        .where(Competitor.brand_profile_id == brand_id)
        .order_by(Competitor.created_at)
    )
    result = await db.execute(stmt)
    return [CompetitorResponse.model_validate(c) for c in result.scalars().all()]


@router.post("/brands/{brand_id}/competitors", response_model=CompetitorResponse)
async def add_competitor(
    brand_id: UUID,
    payload: CompetitorCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    brand = await _get_brand_for_account(brand_id, current_user.account_id, db)

    # Check plan limits
    stmt = select(Competitor).where(
        Competitor.brand_profile_id == brand_id, Competitor.active == True
    )
    result = await db.execute(stmt)
    current_count = len(result.scalars().all())
    raw_plan = current_user.account.plan if current_user.account else "starter"
    plan = getattr(raw_plan, "value", raw_plan)  # enum in DB rows, plain str on the dev stub
    limit = PLAN_COMPETITOR_LIMITS.get(plan, 5)
    if current_count >= limit:
        raise HTTPException(
            status_code=400,
            detail=f"Plan limit reached: {limit} competitors on {plan} plan",
        )

    competitor = Competitor(
        brand_profile_id=brand_id,
        name=payload.name,
        website=payload.website,
        tier=payload.tier,
        social_profiles=payload.social_profiles.model_dump() if payload.social_profiles else None,
        ad_library_url=payload.ad_library_url,
    )
    db.add(competitor)
    await db.flush()
    await db.refresh(competitor)
    return CompetitorResponse.model_validate(competitor)


@router.patch("/competitors/{competitor_id}", response_model=CompetitorResponse)
async def update_competitor(
    competitor_id: UUID,
    payload: CompetitorUpdate,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Competitor)
        .join(BrandProfile, Competitor.brand_profile_id == BrandProfile.id)
        .where(Competitor.id == competitor_id, BrandProfile.account_id == account_id)
    )
    result = await db.execute(stmt)
    competitor = result.scalar_one_or_none()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "social_profiles" in update_data and update_data["social_profiles"] is not None:
        update_data["social_profiles"] = payload.social_profiles.model_dump()

    for field, value in update_data.items():
        setattr(competitor, field, value)

    await db.flush()
    await db.refresh(competitor)
    return CompetitorResponse.model_validate(competitor)


@router.delete("/competitors/{competitor_id}")
async def delete_competitor(
    competitor_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Competitor)
        .join(BrandProfile, Competitor.brand_profile_id == BrandProfile.id)
        .where(Competitor.id == competitor_id, BrandProfile.account_id == account_id)
    )
    result = await db.execute(stmt)
    competitor = result.scalar_one_or_none()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    await db.delete(competitor)
    return {"message": "Competitor deleted"}


@router.post("/brands/{brand_id}/competitors/discover")
async def discover_competitors_endpoint(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    await _get_brand_for_account(brand_id, account_id, db)

    from app.agents.competitor_discovery import discover_competitors
    suggestions = await discover_competitors(brand_id, db)
    return {"suggestions": suggestions}
