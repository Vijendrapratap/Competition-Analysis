"""
Generic time-series metric storage.

MetricTimeSeries allows storing ANY numeric metric for any entity
without schema migrations. Used for custom KPIs, experimental signals,
and metrics that don't fit existing specialized tables.

Think of it as a flexible append-only metric log.

Fields:
- entity_type: "competitor" | "brand" | "account"
- entity_id: UUID of the entity
- metric_key: dot-separated key, e.g. "social.linkedin.followers"
- metric_value: the numeric value
- dimensions: JSONB for arbitrary slicing (e.g. {"platform": "linkedin", "region": "US"})
- source: where the value came from ("apify", "llm", "manual", "calculated")
"""
import uuid
from datetime import datetime, date

from sqlalchemy import (
    String, Numeric, Index, UniqueConstraint,
    DateTime, Date, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MetricTimeSeries(Base):
    """
    Generic append-only metric store.
    One row per entity × metric_key × recorded_on.
    """
    __tablename__ = "metric_time_series"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)  # "competitor" | "brand"
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False)

    metric_key: Mapped[str] = mapped_column(String(256), nullable=False)
    # Examples:
    #   social.linkedin.followers
    #   social.instagram.engagement_rate
    #   seo.domain_authority
    #   ads.active_count
    #   reviews.avg_rating.g2
    #   sentiment.net_score

    metric_value: Mapped[float | None] = mapped_column(Numeric(18, 6))
    metric_text: Mapped[str | None] = mapped_column(String(1024))  # for non-numeric values
    dimensions: Mapped[dict | None] = mapped_column(JSONB)
    # {"platform": "linkedin", "region": "SEA", "filter_mode": "weekly"}

    source: Mapped[str | None] = mapped_column(String(64))  # "apify" | "llm" | "manual" | "calculated"
    confidence: Mapped[float | None] = mapped_column(Numeric(3, 2))  # 0.0 – 1.0

    recorded_on: Mapped[date] = mapped_column(Date, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        Index("ix_mts_entity_key_date", "entity_id", "metric_key", "recorded_on"),
        Index("ix_mts_entity_type", "entity_type", "entity_id"),
        Index("ix_mts_key", "metric_key"),
        # Allow multiple entries per day only if dimensions differ
        # Enforce uniqueness per entity × key × day × dimensions via application logic
    )
