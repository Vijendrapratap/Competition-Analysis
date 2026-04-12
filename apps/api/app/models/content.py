"""
Content intelligence.
Tracks individual content pieces, ad campaigns, and content performance
beyond raw social posts.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Numeric, Integer, Enum, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ContentFormat(str, enum.Enum):
    blog_post = "blog_post"
    landing_page = "landing_page"
    case_study = "case_study"
    whitepaper = "whitepaper"
    video = "video"
    podcast = "podcast"
    webinar = "webinar"
    infographic = "infographic"
    social_post = "social_post"
    ad = "ad"
    email = "email"
    press_release = "press_release"
    job_listing = "job_listing"
    other = "other"


class ContentStage(str, enum.Enum):
    awareness = "awareness"
    consideration = "consideration"
    decision = "decision"
    retention = "retention"
    unknown = "unknown"


class CampaignStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    ended = "ended"
    unknown = "unknown"


class ContentPiece(Base):
    """
    A single piece of content published by a competitor.
    Structured enrichment on top of raw PageSnapshot / SocialPost.
    """
    __tablename__ = "content_pieces"
    __table_args__ = (
        UniqueConstraint("competitor_id", "canonical_url", name="uq_content_piece_url"),
        Index("ix_content_pieces_competitor_format", "competitor_id", "format"),
        Index("ix_content_pieces_published_at", "competitor_id", "published_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id", ondelete="CASCADE"))
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))

    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    canonical_url: Mapped[str] = mapped_column(String(2000))
    format: Mapped[ContentFormat] = mapped_column(Enum(ContentFormat), default=ContentFormat.other)
    funnel_stage: Mapped[ContentStage] = mapped_column(Enum(ContentStage), default=ContentStage.unknown)

    # Content body
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reading_time_min: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Metadata
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    topics: Mapped[list | None] = mapped_column(JSONB, nullable=True)        # AI-extracted topic list
    keywords_targeted: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    sentiment_score: Mapped[float | None] = mapped_column(Numeric, nullable=True)  # -1 to 1

    # Engagement (when available)
    social_shares: Mapped[int | None] = mapped_column(Integer, nullable=True)
    backlinks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    organic_traffic_est: Mapped[int | None] = mapped_column(Integer, nullable=True)

    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    collected_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    competitor: Mapped["Competitor"] = relationship()
    campaign_links: Mapped[list["CampaignContent"]] = relationship(back_populates="content_piece")


class AdCampaign(Base):
    """
    Groups multiple AdCreatives into a logical campaign.
    Detected by clustering similar ads by creative theme + date range.
    """
    __tablename__ = "ad_campaigns"
    __table_args__ = (
        Index("ix_ad_campaigns_competitor_status", "competitor_id", "status"),
        Index("ix_ad_campaigns_first_seen", "competitor_id", "first_seen"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id", ondelete="CASCADE"))
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))

    name: Mapped[str] = mapped_column(String(500))            # AI-generated campaign name
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)  # AI-inferred (brand, lead gen, conversion…)
    primary_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    platforms: Mapped[list | None] = mapped_column(JSONB, nullable=True)  # ["facebook", "instagram"]
    status: Mapped[CampaignStatus] = mapped_column(Enum(CampaignStatus), default=CampaignStatus.unknown)

    ad_count: Mapped[int] = mapped_column(Integer, default=0)
    first_seen: Mapped[datetime | None] = mapped_column(nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(nullable=True)

    ai_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget_est_monthly: Mapped[float | None] = mapped_column(Numeric, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    ad_links: Mapped[list["CampaignAd"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    content_links: Mapped[list["CampaignContent"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class CampaignAd(Base):
    """Junction: AdCampaign ↔ AdCreative (many-to-many)."""
    __tablename__ = "campaign_ads"

    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ad_campaigns.id", ondelete="CASCADE"), primary_key=True)
    ad_creative_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ad_creatives.id", ondelete="CASCADE"), primary_key=True)

    campaign: Mapped["AdCampaign"] = relationship(back_populates="ad_links")


class CampaignContent(Base):
    """Junction: AdCampaign ↔ ContentPiece (many-to-many)."""
    __tablename__ = "campaign_content"

    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ad_campaigns.id", ondelete="CASCADE"), primary_key=True)
    content_piece_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_pieces.id", ondelete="CASCADE"), primary_key=True)

    campaign: Mapped["AdCampaign"] = relationship(back_populates="content_links")
    content_piece: Mapped["ContentPiece"] = relationship(back_populates="campaign_links")


class ContentBenchmark(Base):
    """
    Aggregated content production stats per competitor per period.
    Pre-computed for dashboard charts.
    """
    __tablename__ = "content_benchmarks"
    __table_args__ = (
        UniqueConstraint("brand_profile_id", "competitor_id", "period_label", name="uq_content_benchmark"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    competitor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("competitors.id"), nullable=True)  # NULL = own brand
    period_label: Mapped[str] = mapped_column(String(20))   # "2024-W10", "2024-03"
    posts_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_engagement_rate: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    top_format: Mapped[str | None] = mapped_column(String(50), nullable=True)
    top_topics: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(server_default=func.now())
