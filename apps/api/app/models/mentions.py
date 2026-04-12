"""
Brand mention and influencer tracking models.

BrandMention      - any mention of a competitor across news, forums, social (non-owned)
InfluencerMention - specific influencer/creator collaborations detected
ShareOfVoiceDaily - per-channel daily SoV breakdowns (supplements the existing monthly SoV)
"""
import enum
import uuid
from datetime import datetime, date

from sqlalchemy import (
    String, Text, Numeric, Integer, ForeignKey, Index, Boolean,
    Enum, DateTime, Date, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MentionSource(str, enum.Enum):
    news = "news"
    reddit = "reddit"
    twitter = "twitter"
    linkedin = "linkedin"
    youtube = "youtube"
    podcast = "podcast"
    forum = "forum"
    other = "other"


class MentionSentiment(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class BrandMention(Base):
    """
    A mention of a competitor brand in non-owned channels.
    Can be scraped from Google News, Reddit, Twitter/X, etc.
    """
    __tablename__ = "brand_mentions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("brand_profiles.id", ondelete="CASCADE"), nullable=False
    )

    source: Mapped[MentionSource] = mapped_column(
        Enum(MentionSource, name="mention_source_enum"), nullable=False
    )
    url: Mapped[str | None] = mapped_column(String(2048))
    title: Mapped[str | None] = mapped_column(String(512))
    snippet: Mapped[str | None] = mapped_column(Text)

    # Author / publisher
    author_name: Mapped[str | None] = mapped_column(String(256))
    author_followers: Mapped[int | None] = mapped_column(Integer)
    publisher: Mapped[str | None] = mapped_column(String(256))

    sentiment: Mapped[MentionSentiment | None] = mapped_column(
        Enum(MentionSentiment, name="mention_sentiment_enum")
    )
    sentiment_score: Mapped[float | None] = mapped_column(Numeric(4, 3))

    reach_estimate: Mapped[int | None] = mapped_column(Integer)  # estimated impressions
    engagement: Mapped[int | None] = mapped_column(Integer)       # likes/shares/comments combined

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    extra_metadata: Mapped[dict | None] = mapped_column(JSONB)  # platform-specific fields

    __table_args__ = (
        Index("ix_mentions_competitor_date", "competitor_id", "published_at"),
        Index("ix_mentions_source", "source"),
    )


class InfluencerMention(Base):
    """
    Tracks detected influencer/creator partnerships or paid promotions
    (inferred from consistent tagging, sponsored posts, or affiliate codes).
    """
    __tablename__ = "influencer_mentions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True
    )

    platform: Mapped[str] = mapped_column(String(64))
    influencer_handle: Mapped[str] = mapped_column(String(256))
    influencer_followers: Mapped[int | None] = mapped_column(Integer)
    influencer_niche: Mapped[str | None] = mapped_column(String(128))

    post_url: Mapped[str | None] = mapped_column(String(2048))
    post_caption: Mapped[str | None] = mapped_column(Text)
    is_paid: Mapped[bool | None] = mapped_column(Boolean)  # None = unknown
    first_detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    estimated_reach: Mapped[int | None] = mapped_column(Integer)
    engagement_total: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        Index("ix_influencer_competitor", "competitor_id", "platform"),
    )


class ShareOfVoiceDaily(Base):
    """
    Per-channel daily Share of Voice breakdown.
    Supplements the existing monthly ShareOfVoice table
    with granular channel data for time-series charts.
    """
    __tablename__ = "share_of_voice_daily"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("brand_profiles.id", ondelete="CASCADE"), nullable=False
    )
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True
    )

    recorded_on: Mapped[date] = mapped_column(Date, nullable=False)
    channel: Mapped[str] = mapped_column(String(64), nullable=False)  # "linkedin", "instagram", "news"
    sov_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)  # 0.0 - 100.0
    mention_count: Mapped[int] = mapped_column(Integer, default=0)
    engagement_total: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        Index("ix_sov_daily_brand_date", "brand_profile_id", "recorded_on"),
        Index("ix_sov_daily_competitor_channel", "competitor_id", "channel"),
    )
