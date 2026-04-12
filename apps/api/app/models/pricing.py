"""
Pricing & Product intelligence.
Tracks competitor pricing pages, tiers, features, and changes over time.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Numeric, Integer, Enum, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class PricingModel(str, enum.Enum):
    per_seat = "per_seat"
    flat = "flat"
    usage = "usage"
    freemium = "freemium"
    tiered = "tiered"
    custom = "custom"
    unknown = "unknown"


class BillingCycle(str, enum.Enum):
    monthly = "monthly"
    annual = "annual"
    one_time = "one_time"
    usage = "usage"


class PricingPage(Base):
    """Snapshot of a competitor's pricing page — one row per scrape."""
    __tablename__ = "pricing_pages"
    __table_args__ = (
        Index("ix_pricing_pages_competitor_scraped", "competitor_id", "scraped_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(2000))
    raw_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    pricing_model: Mapped[PricingModel] = mapped_column(Enum(PricingModel), default=PricingModel.unknown)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    has_free_tier: Mapped[bool] = mapped_column(Boolean, default=False)
    has_trial: Mapped[bool] = mapped_column(Boolean, default=False)
    trial_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(server_default=func.now())

    competitor: Mapped["Competitor"] = relationship()
    tiers: Mapped[list["PricingTier"]] = relationship(back_populates="pricing_page", cascade="all, delete-orphan")


class PricingTier(Base):
    """Individual pricing tier extracted from a pricing page."""
    __tablename__ = "pricing_tiers"
    __table_args__ = (
        Index("ix_pricing_tiers_page", "pricing_page_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pricing_page_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pricing_pages.id", ondelete="CASCADE"))
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    price_monthly: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    price_annual: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    billing_cycle: Mapped[BillingCycle] = mapped_column(Enum(BillingCycle), default=BillingCycle.monthly)
    seat_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seat_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    features: Mapped[list | None] = mapped_column(JSONB, nullable=True)   # list of feature strings
    cta_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_highlighted: Mapped[bool] = mapped_column(Boolean, default=False)  # "most popular" badge
    position: Mapped[int] = mapped_column(Integer, default=0)             # left-to-right order

    pricing_page: Mapped["PricingPage"] = relationship(back_populates="tiers")


class PricingChange(Base):
    """
    Detected change between two pricing page scrapes.
    AI compares consecutive snapshots and emits a row here.
    """
    __tablename__ = "pricing_changes"
    __table_args__ = (
        Index("ix_pricing_changes_competitor_detected", "competitor_id", "detected_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id", ondelete="CASCADE"))
    tier_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    field_changed: Mapped[str] = mapped_column(String(100))  # e.g. "price_monthly", "features", "tier_added"
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_pct: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    ai_interpretation: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(server_default=func.now())
    alert_sent: Mapped[bool] = mapped_column(Boolean, default=False)
