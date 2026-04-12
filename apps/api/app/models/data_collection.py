import uuid
from datetime import datetime
import enum
from sqlalchemy import String, Text, Integer, Numeric, Enum, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class SourceType(str, enum.Enum):
    website = "website"
    facebook = "facebook"
    instagram = "instagram"
    linkedin = "linkedin"
    youtube = "youtube"
    ad_library = "ad_library"


class QualityStatus(str, enum.Enum):
    clean = "clean"
    warning = "warning"
    rejected = "rejected"


class Platform(str, enum.Enum):
    facebook = "facebook"
    instagram = "instagram"
    linkedin = "linkedin"
    youtube = "youtube"


class PostType(str, enum.Enum):
    reel = "reel"
    image = "image"
    carousel = "carousel"
    video = "video"
    text = "text"
    story = "story"


class MediaType(str, enum.Enum):
    image = "image"
    video = "video"
    carousel = "carousel"


class ThemeSource(str, enum.Enum):
    social = "social"
    website = "website"
    ads = "ads"


class ChangeType(str, enum.Enum):
    headline = "headline"
    pricing = "pricing"
    new_page = "new_page"
    nav_change = "nav_change"
    offer = "offer"


class Significance(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class PageSnapshot(Base):
    __tablename__ = "page_snapshots"
    __table_args__ = (
        Index("ix_page_snapshots_competitor_source_scraped", "competitor_id", "source_type", "scraped_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id"))
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType))
    url: Mapped[str] = mapped_column(String(2000))
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True, name="metadata")
    quality_status: Mapped[QualityStatus] = mapped_column(Enum(QualityStatus), default=QualityStatus.clean)
    quality_notes: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class SocialPost(Base):
    __tablename__ = "social_posts"
    __table_args__ = (
        UniqueConstraint("competitor_id", "platform", "post_id", name="uq_social_post"),
        Index("ix_social_posts_competitor_published", "competitor_id", "published_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id"))
    platform: Mapped[Platform] = mapped_column(Enum(Platform))
    post_id: Mapped[str] = mapped_column(Text)
    post_type: Mapped[PostType] = mapped_column(Enum(PostType))
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtags: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    likes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shares: Mapped[int | None] = mapped_column(Integer, nullable=True)
    views: Mapped[int | None] = mapped_column(Integer, nullable=True)
    engagement_rate: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    media_urls: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    collected_at: Mapped[datetime] = mapped_column(server_default=func.now())


class AdCreative(Base):
    __tablename__ = "ad_creatives"
    __table_args__ = (
        UniqueConstraint("competitor_id", "platform", "ad_id", name="uq_ad_creative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id"))
    platform: Mapped[str] = mapped_column(Text)
    ad_id: Mapped[str] = mapped_column(Text)
    headline: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType))
    media_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    landing_page_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_seen: Mapped[datetime | None] = mapped_column(nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(nullable=True)
    active: Mapped[bool] = mapped_column(default=True)
    collected_at: Mapped[datetime] = mapped_column(server_default=func.now())


class MessageTheme(Base):
    __tablename__ = "message_themes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id"))
    source: Mapped[ThemeSource] = mapped_column(Enum(ThemeSource))
    theme: Mapped[str] = mapped_column(Text)
    evidence: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    frequency: Mapped[int | None] = mapped_column(Integer, nullable=True)
    period_start: Mapped[datetime | None] = mapped_column(nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class WebsiteChange(Base):
    __tablename__ = "website_changes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id"))
    change_type: Mapped[ChangeType] = mapped_column(Enum(ChangeType))
    before_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    after_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    significance: Mapped[Significance] = mapped_column(Enum(Significance), default=Significance.medium)
    detected_at: Mapped[datetime] = mapped_column(server_default=func.now())
