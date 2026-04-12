"""
Collection schedule configuration.
Defines when data collection jobs run for each brand.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Integer, Enum, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ScheduleType(str, enum.Enum):
    full = "full"            # collect all data sources
    social_only = "social_only"
    website_only = "website_only"
    ads_only = "ads_only"
    seo_only = "seo_only"
    pricing_only = "pricing_only"


class CollectionSchedule(Base):
    """
    Cron-style schedule that triggers Temporal collection workflows.
    Each brand can have multiple schedules for different collection types.
    """
    __tablename__ = "collection_schedules"
    __table_args__ = (
        Index("ix_schedules_brand_active", "brand_profile_id", "active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    schedule_type: Mapped[ScheduleType] = mapped_column(Enum(ScheduleType), default=ScheduleType.full)
    cron_expression: Mapped[str] = mapped_column(String(100))    # e.g. "0 6 * * 1" (Mon 6am)
    timezone: Mapped[str] = mapped_column(String(100), default="UTC")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    temporal_schedule_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_run_at: Mapped[datetime | None] = mapped_column(nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    brand_profile: Mapped["BrandProfile"] = relationship()
