"""Alert delivery service — handles in-app, email, and future Slack delivery."""

import structlog
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accounts import User
from app.models.analytics import Alert, Severity
from app.models.brands import BrandProfile
from app.services.email import send_alert_email

logger = structlog.get_logger()


async def deliver_alerts(brand_profile_id: UUID, db: AsyncSession) -> None:
    """Process and deliver alerts for a brand profile."""
    # Get brand + owner
    stmt = select(BrandProfile).where(BrandProfile.id == brand_profile_id)
    result = await db.execute(stmt)
    brand = result.scalar_one_or_none()
    if not brand:
        return

    stmt = select(User).where(User.account_id == brand.account_id, User.role == "owner")
    result = await db.execute(stmt)
    owner = result.scalar_one_or_none()
    if not owner:
        return

    # Get undelivered alerts
    stmt = (
        select(Alert)
        .where(Alert.brand_profile_id == brand_profile_id, Alert.read == False)
        .order_by(Alert.triggered_at.desc())
    )
    result = await db.execute(stmt)
    alerts = list(result.scalars().all())

    if not alerts:
        return

    # Split by severity
    high_alerts = [a for a in alerts if a.severity == Severity.high]
    other_alerts = [a for a in alerts if a.severity != Severity.high]

    # Immediate email for high severity
    if high_alerts:
        try:
            await send_alert_email(
                to_email=owner.email,
                subject=f"[CompeteIQ] {len(high_alerts)} urgent alert{'s' if len(high_alerts) != 1 else ''} for {brand.name}",
                brand_name=brand.name,
                alerts=[
                    {
                        "severity": a.severity.value,
                        "title": a.title,
                        "description": a.description,
                    }
                    for a in high_alerts
                ],
            )
        except Exception as e:
            logger.error("high_alert_email_failed", error=str(e))

    # Digest for medium/low (bundled)
    if other_alerts:
        try:
            await send_alert_email(
                to_email=owner.email,
                subject=f"[CompeteIQ] {len(other_alerts)} competitive alert{'s' if len(other_alerts) != 1 else ''} for {brand.name}",
                brand_name=brand.name,
                alerts=[
                    {
                        "severity": a.severity.value,
                        "title": a.title,
                        "description": a.description,
                    }
                    for a in other_alerts
                ],
            )
        except Exception as e:
            logger.error("digest_email_failed", error=str(e))

    logger.info(
        "alerts_delivered",
        brand_id=str(brand_profile_id),
        high=len(high_alerts),
        other=len(other_alerts),
    )
