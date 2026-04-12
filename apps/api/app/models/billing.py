"""
Billing, plan limits, and API usage tracking.
Enforces per-plan quotas and tracks consumption for metering.
"""
import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, Boolean, Text, Integer, Numeric, Enum, Date, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UsageMetric(str, enum.Enum):
    llm_input_tokens = "llm_input_tokens"
    llm_output_tokens = "llm_output_tokens"
    scrape_pages = "scrape_pages"
    api_calls = "api_calls"
    reports_generated = "reports_generated"
    competitors_tracked = "competitors_tracked"
    users_count = "users_count"
    alerts_sent = "alerts_sent"


class PlanLimits(Base):
    """
    Defines hard and soft limits for each plan tier.
    Managed by admins; keyed by plan name.
    """
    __tablename__ = "plan_limits"

    plan: Mapped[str] = mapped_column(String(50), primary_key=True)  # starter | growth | enterprise
    max_competitors: Mapped[int] = mapped_column(Integer, default=5)
    max_users: Mapped[int] = mapped_column(Integer, default=3)
    max_brands: Mapped[int] = mapped_column(Integer, default=1)
    collection_frequency_hours: Mapped[int] = mapped_column(Integer, default=168)  # weekly by default
    llm_tokens_monthly: Mapped[int] = mapped_column(Integer, default=500_000)
    scrape_pages_monthly: Mapped[int] = mapped_column(Integer, default=1000)
    reports_monthly: Mapped[int] = mapped_column(Integer, default=4)
    history_days: Mapped[int] = mapped_column(Integer, default=90)   # how far back data is retained
    features: Mapped[dict] = mapped_column(JSONB, default=dict)      # feature flags per plan


class UsageRecord(Base):
    """
    Daily usage accumulator per account per metric.
    Reset daily; aggregated monthly for billing.
    """
    __tablename__ = "usage_records"
    __table_args__ = (
        UniqueConstraint("account_id", "metric", "recorded_on", name="uq_usage_daily"),
        Index("ix_usage_records_account_month", "account_id", "recorded_on"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    metric: Mapped[UsageMetric] = mapped_column(Enum(UsageMetric))
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    recorded_on: Mapped[date] = mapped_column(Date)   # UTC date


class BillingPeriod(Base):
    """
    Monthly billing summary per account.
    Created by a nightly job at month end.
    """
    __tablename__ = "billing_periods"
    __table_args__ = (
        UniqueConstraint("account_id", "period_month", name="uq_billing_period"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    period_month: Mapped[date] = mapped_column(Date)          # first day of month
    plan: Mapped[str] = mapped_column(String(50))
    usage_summary: Mapped[dict] = mapped_column(JSONB)         # {metric: total_quantity}
    overage_usd: Mapped[float] = mapped_column(Numeric, default=0)
    invoice_id: Mapped[str | None] = mapped_column(String(255), nullable=True)   # Stripe invoice ID
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
