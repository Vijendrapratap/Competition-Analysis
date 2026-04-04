from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import AccountId
from app.models.brands import BrandProfile
from app.models.kpi_config import KpiConfig
from app.schemas.kpi_config import KpiConfigCreate, KpiConfigUpdate, KpiConfigResponse

router = APIRouter()


@router.get("/brands/{brand_id}/kpi-config", response_model=KpiConfigResponse | None)
async def get_kpi_config(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BrandProfile).where(
        BrandProfile.id == brand_id, BrandProfile.account_id == account_id
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Brand not found")

    stmt = select(KpiConfig).where(KpiConfig.brand_profile_id == brand_id)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        return None
    return KpiConfigResponse.model_validate(config)


@router.post("/brands/{brand_id}/kpi-config", response_model=KpiConfigResponse)
async def save_kpi_config(
    brand_id: UUID,
    payload: KpiConfigCreate,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BrandProfile).where(
        BrandProfile.id == brand_id, BrandProfile.account_id == account_id
    )
    result = await db.execute(stmt)
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    # Check if config already exists
    stmt = select(KpiConfig).where(KpiConfig.brand_profile_id == brand_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="KPI config already exists, use PATCH")

    config = KpiConfig(
        brand_profile_id=brand_id,
        filter_mode=payload.filter_mode,
        kpi_pack=payload.kpi_pack,
        kpis=payload.kpis,
    )
    db.add(config)

    # Mark brand setup as complete
    brand.setup_complete = True

    await db.flush()
    await db.refresh(config)
    return KpiConfigResponse.model_validate(config)


@router.patch("/brands/{brand_id}/kpi-config", response_model=KpiConfigResponse)
async def update_kpi_config(
    brand_id: UUID,
    payload: KpiConfigUpdate,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BrandProfile).where(
        BrandProfile.id == brand_id, BrandProfile.account_id == account_id
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Brand not found")

    stmt = select(KpiConfig).where(KpiConfig.brand_profile_id == brand_id)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="KPI config not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    await db.flush()
    await db.refresh(config)
    return KpiConfigResponse.model_validate(config)


@router.get("/brands/{brand_id}/kpi-recommendations")
async def kpi_recommendations(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BrandProfile).where(
        BrandProfile.id == brand_id, BrandProfile.account_id == account_id
    )
    result = await db.execute(stmt)
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    # Return default recommendations based on industry
    return {
        "industry": brand.industry,
        "recommended_filter_mode": "weekly",
        "message": "Use KPI packs from packages/shared/constants/kpi-packs.ts",
    }
