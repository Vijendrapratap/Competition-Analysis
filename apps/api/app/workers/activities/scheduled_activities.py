import uuid
from temporalio import activity
from sqlalchemy import select

from app.database import async_session
from app.models.brands import BrandProfile
from app.models.competitors import Competitor
from app.models.kpi_config import KpiConfig
from app.models.accounts import User, Account
from app.services.email import send_alert_email


@activity.defn
async def get_brands_for_schedule(filter_mode: str) -> list[dict]:
    """Get all active brands with the specified filter mode."""
    async with async_session() as db:
        stmt = (
            select(BrandProfile)
            .join(KpiConfig, KpiConfig.brand_profile_id == BrandProfile.id)
            .where(
                BrandProfile.setup_complete == True,
                KpiConfig.filter_mode == filter_mode,
            )
        )
        result = await db.execute(stmt)
        brands = result.scalars().all()
        return [
            {"id": str(b.id), "name": b.name, "account_id": str(b.account_id)}
            for b in brands
        ]


@activity.defn
async def get_competitor_configs(brand_id: str) -> list[dict]:
    """Get competitor configs for a brand."""
    async with async_session() as db:
        stmt = select(Competitor).where(
            Competitor.brand_profile_id == uuid.UUID(brand_id),
            Competitor.active == True,
        )
        result = await db.execute(stmt)
        competitors = result.scalars().all()
        return [
            {
                "id": str(c.id),
                "name": c.name,
                "website": c.website,
                "social_profiles": c.social_profiles,
                "ad_library_url": c.ad_library_url,
            }
            for c in competitors
        ]


@activity.defn
async def send_failure_notification(brand_id: str, error_message: str) -> None:
    """Send failure notification to account owner."""
    async with async_session() as db:
        stmt = select(BrandProfile).where(BrandProfile.id == uuid.UUID(brand_id))
        result = await db.execute(stmt)
        brand = result.scalar_one_or_none()
        if not brand:
            return

        stmt = select(User).where(User.account_id == brand.account_id, User.role == "owner")
        result = await db.execute(stmt)
        owner = result.scalar_one_or_none()
        if not owner:
            return

        try:
            await send_alert_email(
                to_email=owner.email,
                subject=f"[CompeteIQ] Collection failed for {brand.name}",
                brand_name=brand.name,
                alerts=[{
                    "severity": "high",
                    "title": "Collection Pipeline Failed",
                    "description": f"Scheduled collection for {brand.name} failed: {error_message}. Please check your configuration or try a manual trigger.",
                }],
            )
        except Exception as e:
            activity.logger.warning(f"Failed to send failure notification: {e}")
