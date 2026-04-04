from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import AccountId
from app.models.brands import BrandProfile
from app.models.competitors import Competitor
from app.models.analytics import Alert, KpiSnapshot

router = APIRouter()


@router.get("/brands/{brand_id}/dashboard")
async def get_dashboard(
    brand_id: UUID,
    account_id: AccountId,
    filter_mode: str = Query(default="weekly"),
    db: AsyncSession = Depends(get_db),
):
    # Verify brand belongs to account
    stmt = select(BrandProfile).where(
        BrandProfile.id == brand_id, BrandProfile.account_id == account_id
    )
    result = await db.execute(stmt)
    brand = result.scalar_one_or_none()
    if not brand:
        return {"error": "Brand not found"}

    # Count competitors
    stmt = select(func.count()).select_from(Competitor).where(
        Competitor.brand_profile_id == brand_id, Competitor.active == True
    )
    result = await db.execute(stmt)
    competitor_count = result.scalar() or 0

    # Count unread alerts
    stmt = select(func.count()).select_from(Alert).where(
        Alert.brand_profile_id == brand_id, Alert.read == False
    )
    result = await db.execute(stmt)
    alert_count = result.scalar() or 0

    return {
        "summary": {
            "competitors_tracked": competitor_count,
            "channels_monitored": 0,
            "active_alerts": alert_count,
            "rising_threat": None,
        },
        "executive_summary": None,
        "kpi_snapshots": {},
        "competitor_cards": [],
        "messaging_themes": [],
        "paid_media_summary": {},
        "opportunities": [],
        "alerts": [],
    }


@router.get("/brands/{brand_id}/dashboard/refresh")
async def refresh_dashboard(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    # TODO: Trigger collection workflow (Phase 5)
    return {"message": "Dashboard refresh triggered"}


## Alerts are handled by the dedicated alerts router (app.routers.alerts)
