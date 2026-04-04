from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import AccountId
from app.models.analytics import Alert, AlertRule, AlertCondition
from app.models.brands import BrandProfile
from app.schemas.analytics import AlertResponse, AlertRuleCreate, AlertRuleResponse

router = APIRouter()


@router.get("/brands/{brand_id}/alerts", response_model=list[AlertResponse])
async def get_alerts(
    brand_id: UUID,
    account_id: AccountId,
    unread: bool = False,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Alert).join(
        BrandProfile, Alert.brand_profile_id == BrandProfile.id
    ).where(
        BrandProfile.id == brand_id, BrandProfile.account_id == account_id
    )
    if unread:
        stmt = stmt.where(Alert.read == False, Alert.dismissed == False)
    stmt = stmt.order_by(Alert.triggered_at.desc()).limit(50)

    result = await db.execute(stmt)
    return [AlertResponse.model_validate(a) for a in result.scalars().all()]


@router.patch("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Alert).join(
        BrandProfile, Alert.brand_profile_id == BrandProfile.id
    ).where(Alert.id == alert_id, BrandProfile.account_id == account_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.read = True
    return {"status": "ok"}


@router.patch("/alerts/{alert_id}/dismiss")
async def dismiss_alert(
    alert_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Alert).join(
        BrandProfile, Alert.brand_profile_id == BrandProfile.id
    ).where(Alert.id == alert_id, BrandProfile.account_id == account_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.dismissed = True
    return {"status": "ok"}


@router.post("/brands/{brand_id}/alerts/read-all")
async def mark_all_read(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    # Verify brand access
    stmt = select(BrandProfile).where(
        BrandProfile.id == brand_id, BrandProfile.account_id == account_id
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Brand not found")

    stmt = (
        update(Alert)
        .where(Alert.brand_profile_id == brand_id, Alert.read == False)
        .values(read=True)
    )
    await db.execute(stmt)
    return {"status": "ok"}


# ── Alert Rules CRUD ──

@router.get("/brands/{brand_id}/alert-rules", response_model=list[AlertRuleResponse])
async def list_alert_rules(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AlertRule).join(
        BrandProfile, AlertRule.brand_profile_id == BrandProfile.id
    ).where(
        BrandProfile.id == brand_id, BrandProfile.account_id == account_id
    )
    result = await db.execute(stmt)
    return [AlertRuleResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/brands/{brand_id}/alert-rules", response_model=AlertRuleResponse)
async def create_alert_rule(
    brand_id: UUID,
    payload: AlertRuleCreate,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BrandProfile).where(
        BrandProfile.id == brand_id, BrandProfile.account_id == account_id
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Brand not found")

    rule = AlertRule(
        brand_profile_id=brand_id,
        competitor_id=payload.competitor_id,
        kpi_key=payload.kpi_key,
        condition=payload.condition,
        threshold=payload.threshold,
    )
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return AlertRuleResponse.model_validate(rule)


@router.delete("/alert-rules/{rule_id}")
async def delete_alert_rule(
    rule_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AlertRule).join(
        BrandProfile, AlertRule.brand_profile_id == BrandProfile.id
    ).where(AlertRule.id == rule_id, BrandProfile.account_id == account_id)
    result = await db.execute(stmt)
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    await db.delete(rule)
    return {"status": "deleted"}
