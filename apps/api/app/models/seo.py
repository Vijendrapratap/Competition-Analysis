"""
SEO & keyword intelligence.
Tracks keywords, SERP rankings, backlinks, and organic traffic estimates
for both the brand and competitors.
"""
import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, Boolean, Text, Numeric, Integer, Enum, Date, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class KeywordIntent(str, enum.Enum):
    branded = "branded"
    informational = "informational"
    navigational = "navigational"
    transactional = "transactional"
    commercial = "commercial"


class RankingType(str, enum.Enum):
    organic = "organic"
    featured_snippet = "featured_snippet"
    local_pack = "local_pack"
    paid = "paid"
    image = "image"
    video = "video"


class Keyword(Base):
    """Master keyword registry shared across a brand's competitive set."""
    __tablename__ = "keywords"
    __table_args__ = (
        UniqueConstraint("brand_profile_id", "keyword", name="uq_keyword_per_brand"),
        Index("ix_keywords_brand_volume", "brand_profile_id", "monthly_search_volume"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    keyword: Mapped[str] = mapped_column(String(500))
    intent: Mapped[KeywordIntent] = mapped_column(Enum(KeywordIntent), default=KeywordIntent.informational)
    monthly_search_volume: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[float | None] = mapped_column(Numeric, nullable=True)   # 0-100
    cpc_usd: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    added_by: Mapped[str] = mapped_column(String(50), default="user")  # user | ai_discovery
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    rankings: Mapped[list["KeywordRanking"]] = relationship(back_populates="keyword", cascade="all, delete-orphan")


class KeywordRanking(Base):
    """
    Daily rank snapshot for a keyword → entity (brand or competitor).
    competitor_id=NULL means it is for the brand itself.
    """
    __tablename__ = "keyword_rankings"
    __table_args__ = (
        UniqueConstraint("keyword_id", "entity_id", "entity_type", "ranked_on", name="uq_ranking_per_day"),
        Index("ix_keyword_rankings_keyword_entity_date", "keyword_id", "entity_id", "ranked_on"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    keyword_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"))
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    # entity_id can reference brand_profiles.id or competitors.id
    entity_id: Mapped[uuid.UUID] = mapped_column()
    entity_type: Mapped[str] = mapped_column(String(20))   # "brand" | "competitor"
    ranking_type: Mapped[RankingType] = mapped_column(Enum(RankingType), default=RankingType.organic)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-100, NULL = not in top 100
    url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    ranked_on: Mapped[date] = mapped_column(Date)

    keyword: Mapped["Keyword"] = relationship(back_populates="rankings")


class SeoMetric(Base):
    """
    Aggregated SEO health metrics per entity per month.
    Covers domain authority, backlinks, organic traffic, etc.
    """
    __tablename__ = "seo_metrics"
    __table_args__ = (
        UniqueConstraint("brand_profile_id", "entity_id", "entity_type", "period_month", name="uq_seo_metric_month"),
        Index("ix_seo_metrics_brand_entity_month", "brand_profile_id", "entity_id", "period_month"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    entity_id: Mapped[uuid.UUID] = mapped_column()
    entity_type: Mapped[str] = mapped_column(String(20))    # "brand" | "competitor"
    period_month: Mapped[date] = mapped_column(Date)         # first day of month
    domain_authority: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    page_authority: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    backlinks_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    referring_domains: Mapped[int | None] = mapped_column(Integer, nullable=True)
    organic_traffic_est: Mapped[int | None] = mapped_column(Integer, nullable=True)
    organic_keywords_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    top_10_keywords: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="semrush")  # semrush | ahrefs | moz | manual
    collected_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ContentGap(Base):
    """
    Keywords where competitor ranks but brand does not (AI-detected gaps).
    """
    __tablename__ = "content_gaps"
    __table_args__ = (
        Index("ix_content_gaps_brand_competitor", "brand_profile_id", "competitor_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id", ondelete="CASCADE"))
    keyword_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("keywords.id"), nullable=True)
    keyword_text: Mapped[str] = mapped_column(String(500))
    competitor_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_volume: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    opportunity_score: Mapped[float | None] = mapped_column(Numeric, nullable=True)  # 0-100
    detected_at: Mapped[datetime] = mapped_column(server_default=func.now())
    actioned: Mapped[bool] = mapped_column(Boolean, default=False)
