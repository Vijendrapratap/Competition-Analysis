"""
Customer review models — G2, Capterra, App Store, TrustRadius, etc.

CompetitorReview   - individual review record
ReviewAggregate    - LLM-generated summary per competitor per collection cycle
"""
import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String, Text, Numeric, Integer, ForeignKey, Index, Boolean,
    Enum, DateTime, func,
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReviewPlatform(str, enum.Enum):
    g2 = "g2"
    capterra = "capterra"
    trustradius = "trustradius"
    appstore = "appstore"
    playstore = "playstore"
    trustpilot = "trustpilot"
    other = "other"


class CompetitorReview(Base):
    __tablename__ = "competitor_reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True
    )

    platform: Mapped[ReviewPlatform] = mapped_column(
        Enum(ReviewPlatform, name="review_platform_enum"), nullable=False
    )
    external_id: Mapped[str | None] = mapped_column(String(256))  # platform's own review ID
    rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))  # e.g. 4.5
    title: Mapped[str | None] = mapped_column(String(512))
    body: Mapped[str | None] = mapped_column(Text)
    pros: Mapped[str | None] = mapped_column(Text)
    cons: Mapped[str | None] = mapped_column(Text)

    reviewer_role: Mapped[str | None] = mapped_column(String(256))
    reviewer_company_size: Mapped[str | None] = mapped_column(String(128))
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # LLM-scored sentiment
    sentiment_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))  # -1.0 to 1.0
    sentiment_label: Mapped[str | None] = mapped_column(String(32))

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        Index("ix_reviews_competitor_platform", "competitor_id", "platform"),
        Index("ix_reviews_published_at", "published_at"),
    )


class ReviewAggregate(Base):
    """
    LLM-generated aggregate per competitor per collection cycle.
    Re-computed on each full collection run.
    """
    __tablename__ = "review_aggregates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("brand_profiles.id", ondelete="CASCADE"), nullable=False
    )

    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    avg_rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    sentiment_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))  # -1 to 1

    top_praises: Mapped[list | None] = mapped_column(JSONB)       # ["Fast onboarding", ...]
    top_complaints: Mapped[list | None] = mapped_column(JSONB)    # ["Expensive", ...]
    positioning_gaps: Mapped[list | None] = mapped_column(JSONB)  # gaps brand could target
    review_summary: Mapped[str | None] = mapped_column(Text)

    platform_breakdown: Mapped[dict | None] = mapped_column(JSONB)
    # {"g2": {"count": 120, "avg_rating": 4.3}, "capterra": {...}}

    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        Index("ix_review_agg_competitor", "competitor_id", "computed_at"),
    )
