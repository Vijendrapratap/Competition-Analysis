import uuid
from datetime import datetime
import enum
from sqlalchemy import String, Boolean, Text, Integer, Numeric, Enum, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.kpi_config import FilterMode


class AlertType(str, enum.Enum):
    posting_spike = "posting_spike"
    new_campaign = "new_campaign"
    message_shift = "message_shift"
    pricing_change = "pricing_change"
    sov_move = "sov_move"
    engagement_spike = "engagement_spike"
    paid_pause = "paid_pause"


class Severity(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class AlertCondition(str, enum.Enum):
    increase_pct_gt = "increase_pct_gt"
    decrease_pct_gt = "decrease_pct_gt"
    new_value = "new_value"
    threshold_gt = "threshold_gt"
    threshold_lt = "threshold_lt"


class KpiSnapshot(Base):
    __tablename__ = "kpi_snapshots"
    __table_args__ = (
        Index("ix_kpi_brand_filter_period", "brand_profile_id", "filter_mode", "period_start"),
        Index("ix_kpi_competitor_key_period", "competitor_id", "kpi_key", "period_start"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id"))
    competitor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("competitors.id"), nullable=True)
    filter_mode: Mapped[FilterMode] = mapped_column(Enum(FilterMode))
    period_start: Mapped[datetime] = mapped_column()
    period_end: Mapped[datetime] = mapped_column()
    kpi_key: Mapped[str] = mapped_column(Text)
    kpi_value: Mapped[float] = mapped_column(Numeric)
    kpi_label: Mapped[str] = mapped_column(Text)
    delta_pct: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ShareOfVoice(Base):
    __tablename__ = "share_of_voice"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id"))
    period_start: Mapped[datetime] = mapped_column()
    period_end: Mapped[datetime] = mapped_column()
    filter_mode: Mapped[FilterMode] = mapped_column(Enum(FilterMode))
    entries: Mapped[list] = mapped_column(JSONB)


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("ix_alerts_brand_triggered", "brand_profile_id", "triggered_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id"))
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id"))
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType))
    severity: Mapped[Severity] = mapped_column(Enum(Severity))
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    evidence: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    triggered_at: Mapped[datetime] = mapped_column(server_default=func.now())
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    dismissed: Mapped[bool] = mapped_column(Boolean, default=False)


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id"))
    filter_mode: Mapped[FilterMode] = mapped_column(Enum(FilterMode))
    period_start: Mapped[datetime] = mapped_column()
    period_end: Mapped[datetime] = mapped_column()
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(server_default=func.now())


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id"))
    competitor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("competitors.id"), nullable=True)
    kpi_key: Mapped[str] = mapped_column(Text)
    condition: Mapped[AlertCondition] = mapped_column(Enum(AlertCondition))
    threshold: Mapped[float] = mapped_column(Numeric)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
