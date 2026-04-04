import structlog
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from temporalio.client import Client, Schedule, ScheduleActionStartWorkflow, ScheduleSpec, ScheduleIntervalSpec
from datetime import timedelta

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import AccountId
from app.models.brands import BrandProfile
from app.models.kpi_config import KpiConfig

logger = structlog.get_logger()
router = APIRouter()

CRON_SCHEDULES = {
    "daily": "0 0 * * *",       # Midnight UTC
    "weekly": "0 2 * * 1",      # Monday 2AM UTC
    "monthly": "0 2 1 * *",     # 1st of month 2AM UTC
}


@router.get("/brands/{brand_id}/schedule")
async def get_schedule(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(KpiConfig).join(
        BrandProfile, KpiConfig.brand_profile_id == BrandProfile.id
    ).where(
        BrandProfile.id == brand_id, BrandProfile.account_id == account_id
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()

    if not config:
        return {"active": False, "filter_mode": None, "cron": None}

    return {
        "active": True,
        "filter_mode": config.filter_mode.value,
        "cron": CRON_SCHEDULES.get(config.filter_mode.value),
        "schedule_id": f"competeiq-schedule-{brand_id}",
    }


@router.post("/brands/{brand_id}/schedule/trigger")
async def manual_trigger(
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

    stmt = select(KpiConfig).where(KpiConfig.brand_profile_id == brand_id)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    filter_mode = config.filter_mode.value if config else "weekly"

    try:
        settings = get_settings()
        client = await Client.connect(settings.TEMPORAL_HOST)
        handle = await client.start_workflow(
            "ScheduledCollectionWorkflow",
            args=[filter_mode],
            id=f"manual-trigger-{brand_id}",
            task_queue="competeiq-main",
        )
        return {"message": "Manual collection triggered", "workflow_id": handle.id}
    except Exception as e:
        logger.error("manual_trigger_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to trigger collection")
