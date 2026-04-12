"""
External integrations: webhooks, Slack, CRM connectors, and API keys.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Integer, Enum, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class IntegrationType(str, enum.Enum):
    slack = "slack"
    teams = "teams"
    hubspot = "hubspot"
    salesforce = "salesforce"
    notion = "notion"
    jira = "jira"
    zapier = "zapier"
    custom_webhook = "custom_webhook"


class WebhookEventType(str, enum.Enum):
    alert_triggered = "alert_triggered"
    report_ready = "report_ready"
    competitor_added = "competitor_added"
    collection_completed = "collection_completed"
    pricing_change = "pricing_change"
    campaign_detected = "campaign_detected"


class DeliveryStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"
    retrying = "retrying"


class Integration(Base):
    """
    Connected third-party service per account.
    Stores OAuth tokens (encrypted) and config.
    """
    __tablename__ = "integrations"
    __table_args__ = (
        UniqueConstraint("account_id", "type", name="uq_integration_per_account_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    type: Mapped[IntegrationType] = mapped_column(Enum(IntegrationType))
    name: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Encrypted at-rest (AES-256) — store cipher text only
    encrypted_credentials: Mapped[str | None] = mapped_column(Text, nullable=True)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)   # non-secret config

    connected_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    connected_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_used_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class Webhook(Base):
    """
    Outbound webhook endpoints registered by an account.
    Fires on selected event types.
    """
    __tablename__ = "webhooks"
    __table_args__ = (
        Index("ix_webhooks_account_active", "account_id", "active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(2000))
    secret: Mapped[str | None] = mapped_column(String(255), nullable=True)  # HMAC signing secret
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    event_types: Mapped[list] = mapped_column(JSONB, default=list)   # list of WebhookEventType values
    headers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # custom headers
    retry_count: Mapped[int] = mapped_column(Integer, default=3)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    deliveries: Mapped[list["WebhookDelivery"]] = relationship(back_populates="webhook", cascade="all, delete-orphan")


class WebhookDelivery(Base):
    """
    Delivery log for every webhook fire attempt.
    """
    __tablename__ = "webhook_deliveries"
    __table_args__ = (
        Index("ix_webhook_deliveries_webhook_sent", "webhook_id", "sent_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    webhook_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("webhooks.id", ondelete="CASCADE"))
    event_type: Mapped[WebhookEventType] = mapped_column(Enum(WebhookEventType))
    payload: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus), default=DeliveryStatus.pending)
    response_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    next_retry_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    webhook: Mapped["Webhook"] = relationship(back_populates="deliveries")


class ApiKey(Base):
    """
    Machine-readable API keys for programmatic access to CompeteIQ.
    Used by external tools, Zapier, etc.
    """
    __tablename__ = "api_keys"
    __table_args__ = (
        Index("ix_api_keys_account_active", "account_id", "active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(255))
    key_prefix: Mapped[str] = mapped_column(String(20))        # first 8 chars for display
    key_hash: Mapped[str] = mapped_column(String(64))          # SHA-256 of full key
    scopes: Mapped[list] = mapped_column(JSONB, default=list)  # ["read:alerts", "read:reports"]
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
