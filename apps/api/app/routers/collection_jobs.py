from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import AccountId
from app.models.brands import BrandProfile
from app.models.collection_jobs import CollectionJob, JobType, JobStatus, TriggeredBy
from app.models.competitors import Competitor
from app.schemas.collection import CollectionJobResponse

router = APIRouter()


@router.post("/brands/{brand_id}/collect")
async def trigger_collection(
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

    # Count active competitors
    stmt = select(Competitor).where(
        Competitor.brand_profile_id == brand_id, Competitor.active == True
    )
    result = await db.execute(stmt)
    competitors = result.scalars().all()
    if not competitors:
        raise HTTPException(status_code=400, detail="No active competitors to collect data for")

    job = CollectionJob(
        brand_profile_id=brand_id,
        job_type=JobType.full_collection,
        status=JobStatus.pending,
        triggered_by=TriggeredBy.user,
        competitors_total=len(competitors),
        competitors_completed=0,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)

    # TODO: Dispatch Temporal FullCollectionWorkflow (Phase 4.1)

    return {"message": "Collection triggered", "job_id": str(job.id)}


@router.get("/collection-jobs/{job_id}", response_model=CollectionJobResponse)
async def get_collection_job(
    job_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(CollectionJob)
        .join(BrandProfile, CollectionJob.brand_profile_id == BrandProfile.id)
        .where(CollectionJob.id == job_id, BrandProfile.account_id == account_id)
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Collection job not found")
    return CollectionJobResponse.model_validate(job)


@router.get("/brands/{brand_id}/collection-history", response_model=list[CollectionJobResponse])
async def collection_history(
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

    stmt = (
        select(CollectionJob)
        .where(CollectionJob.brand_profile_id == brand_id)
        .order_by(CollectionJob.created_at.desc())
        .limit(20)
    )
    result = await db.execute(stmt)
    return [CollectionJobResponse.model_validate(j) for j in result.scalars().all()]
