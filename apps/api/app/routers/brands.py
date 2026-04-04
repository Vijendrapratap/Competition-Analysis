import asyncio
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session
from app.middleware.auth import CurrentUser, AccountId
from app.models.brands import BrandProfile
from app.schemas.brands import BrandCreate, BrandUpdate, BrandResponse, PersonaStatusResponse
from app.agents.brand_persona import generate_brand_persona

router = APIRouter()


@router.post("/brands", response_model=BrandResponse)
async def create_brand(
    payload: BrandCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    brand = BrandProfile(
        account_id=current_user.account_id,
        name=payload.name,
        website=payload.website,
        industry=payload.industry,
        target_region=payload.target_region,
        target_audience=payload.target_audience,
        social_profiles=payload.social_profiles.model_dump() if payload.social_profiles else None,
    )
    db.add(brand)
    await db.flush()
    await db.refresh(brand)
    return BrandResponse.model_validate(brand)


@router.get("/brands/{brand_id}", response_model=BrandResponse)
async def get_brand(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BrandProfile).where(
        BrandProfile.id == brand_id,
        BrandProfile.account_id == account_id,
    )
    result = await db.execute(stmt)
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return BrandResponse.model_validate(brand)


@router.patch("/brands/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_id: UUID,
    payload: BrandUpdate,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BrandProfile).where(
        BrandProfile.id == brand_id,
        BrandProfile.account_id == account_id,
    )
    result = await db.execute(stmt)
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "social_profiles" in update_data and update_data["social_profiles"] is not None:
        update_data["social_profiles"] = payload.social_profiles.model_dump()
    if "persona" in update_data and update_data["persona"] is not None:
        update_data["persona"] = payload.persona.model_dump()

    for field, value in update_data.items():
        setattr(brand, field, value)

    await db.flush()
    await db.refresh(brand)
    return BrandResponse.model_validate(brand)


async def _run_persona_generation(brand_id: UUID):
    """Background task to generate persona with its own DB session."""
    async with async_session() as db:
        try:
            await generate_brand_persona(brand_id, db)
            await db.commit()
        except Exception:
            await db.rollback()


@router.post("/brands/{brand_id}/generate-persona", response_model=PersonaStatusResponse)
async def generate_persona_endpoint(
    brand_id: UUID,
    background_tasks: BackgroundTasks,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BrandProfile).where(
        BrandProfile.id == brand_id,
        BrandProfile.account_id == account_id,
    )
    result = await db.execute(stmt)
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")

    background_tasks.add_task(_run_persona_generation, brand_id)
    return PersonaStatusResponse(status="generating", persona=None)


@router.get("/brands/{brand_id}/persona-status", response_model=PersonaStatusResponse)
async def persona_status(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BrandProfile).where(
        BrandProfile.id == brand_id,
        BrandProfile.account_id == account_id,
    )
    result = await db.execute(stmt)
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")

    if brand.persona:
        return PersonaStatusResponse(status="complete", persona=brand.persona)
    return PersonaStatusResponse(status="pending", persona=None)
