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


@router.get("/brands/{brand_id}/alerts")
async def get_alerts(
    brand_id: UUID,
    account_id: AccountId,
    unread: bool = False,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Alert).where(Alert.brand_profile_id == brand_id)
    if unread:
        stmt = stmt.where(Alert.read == False)
    stmt = stmt.order_by(Alert.triggered_at.desc()).limit(50)

    result = await db.execute(stmt)
    alerts = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "alert_type": a.alert_type.value,
            "severity": a.severity.value,
            "title": a.title,
            "description": a.description,
            "triggered_at": a.triggered_at.isoformat(),
            "read": a.read,
        }
        for a in alerts
    ]
