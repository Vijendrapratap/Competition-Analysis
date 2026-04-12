"""
Analyst intelligence layer.
Manual notes, tags, AI summaries, and benchmarking baselines.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Numeric, Integer, Enum, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class NoteVisibility(str, enum.Enum):
    private = "private"   # only the author sees it
    team = "team"         # whole account sees it


class CompetitorTag(Base):
    """
    Taxonomy of tags that can be applied to competitors.
    E.g. "aggressive pricing", "feature parity", "VC-backed"
    """
    __tablename__ = "competitor_tags"
    __table_args__ = (
        UniqueConstraint("brand_profile_id", "name", name="uq_tag_per_brand"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String(20), default="#6b7280")   # hex colour for UI badge
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    competitor_links: Mapped[list["CompetitorTagLink"]] = relationship(back_populates="tag", cascade="all, delete-orphan")


class CompetitorTagLink(Base):
    """Junction: Competitor ↔ CompetitorTag."""
    __tablename__ = "competitor_tag_links"

    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitor_tags.id", ondelete="CASCADE"), primary_key=True)
    added_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    added_at: Mapped[datetime] = mapped_column(server_default=func.now())

    tag: Mapped["CompetitorTag"] = relationship(back_populates="competitor_links")


class CompetitorNote(Base):
    """
    Free-text analyst notes attached to a competitor.
    Supports markdown; optionally linked to a specific alert or content piece.
    """
    __tablename__ = "competitor_notes"
    __table_args__ = (
        Index("ix_competitor_notes_competitor", "competitor_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id", ondelete="CASCADE"))
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body: Mapped[str] = mapped_column(Text)
    visibility: Mapped[NoteVisibility] = mapped_column(Enum(NoteVisibility), default=NoteVisibility.team)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    linked_alert_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("alerts.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    author: Mapped["User"] = relationship()


class IntelligenceSummary(Base):
    """
    AI-generated weekly/monthly intelligence brief per competitor.
    Synthesizes all signals: social, ads, pricing, SEO, content.
    """
    __tablename__ = "intelligence_summaries"
    __table_args__ = (
        Index("ix_intel_summaries_brand_period", "brand_profile_id", "period_start"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    competitor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("competitors.id"), nullable=True)  # NULL = cross-competitor summary
    period_start: Mapped[datetime] = mapped_column()
    period_end: Mapped[datetime] = mapped_column()
    period_label: Mapped[str] = mapped_column(String(20))   # "2024-W12", "2024-03"

    headline: Mapped[str] = mapped_column(Text)             # one-line top insight
    summary_md: Mapped[str] = mapped_column(Text)           # markdown narrative
    key_moves: Mapped[list | None] = mapped_column(JSONB, nullable=True)   # [{title, description, impact}]
    opportunities: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    threats: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    signals_used: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # count of each signal type
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Benchmark(Base):
    """
    Rolling baseline metrics used for delta calculations.
    Seeded from historical data; updated on each analysis run.
    """
    __tablename__ = "benchmarks"
    __table_args__ = (
        UniqueConstraint("brand_profile_id", "entity_id", "entity_type", "metric_key", "window_days",
                         name="uq_benchmark"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    entity_id: Mapped[uuid.UUID] = mapped_column()           # brand_profiles.id or competitors.id
    entity_type: Mapped[str] = mapped_column(String(20))     # "brand" | "competitor"
    metric_key: Mapped[str] = mapped_column(String(100))     # e.g. "posting_frequency", "engagement_rate"
    window_days: Mapped[int] = mapped_column(Integer)        # baseline window (30, 90, 365)
    baseline_value: Mapped[float] = mapped_column(Numeric)
    baseline_stddev: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    computed_at: Mapped[datetime] = mapped_column(server_default=func.now())
