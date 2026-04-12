"""
Notification preferences and delivery log.
Controls how alerts are delivered to each user and records every delivery attempt.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Integer, Enum, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class NotificationChannel(str, enum.Enum):
    email = "email"
    slack = "slack"
    webhook = "webhook"
    in_app = "in_app"
    sms = "sms"


class DigestFrequency(str, enum.Enum):
    immediate = "immediate"
    daily = "daily"
    weekly = "weekly"
    never = "never"


class DeliveryStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    bounced = "bounced"
    opened = "opened"
    clicked = "clicked"


class NotificationPreference(Base):
    """
    Per-user notification settings.
    One row per user per channel; channels can be toggled independently.
    """
    __tablename__ = "notification_preferences"
    __table_args__ = (
        Index("ix_notif_prefs_user_channel", "user_id", "channel"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    channel: Mapped[NotificationChannel] = mapped_column(Enum(NotificationChannel))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    digest_frequency: Mapped[DigestFrequency] = mapped_column(Enum(DigestFrequency), default=DigestFrequency.immediate)

    # Alert-type filters — null means "all"
    alert_types: Mapped[list | None] = mapped_column(JSONB, nullable=True)     # ["posting_spike", "pricing_change"]
    min_severity: Mapped[str] = mapped_column(String(20), default="low")       # low | medium | high

    # Channel-specific config
    destination: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # email → email address, slack → webhook URL or channel ID, sms → phone number

    # Quiet hours (UTC)
    quiet_hours_start: Mapped[str | None] = mapped_column(String(5), nullable=True)  # "22:00"
    quiet_hours_end: Mapped[str | None] = mapped_column(String(5), nullable=True)    # "08:00"
    quiet_days: Mapped[list | None] = mapped_column(JSONB, nullable=True)            # [6, 7] = Sat, Sun

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship()


class NotificationDelivery(Base):
    """
    Audit trail for every notification attempt.
    Linked to an Alert; one row per channel per attempt.
    """
    __tablename__ = "notification_deliveries"
    __table_args__ = (
        Index("ix_notif_deliveries_alert", "alert_id"),
        Index("ix_notif_deliveries_user_sent", "user_id", "sent_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    alert_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    channel: Mapped[NotificationChannel] = mapped_column(Enum(NotificationChannel))
    status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus), default=DeliveryStatus.pending)
    destination: Mapped[str | None] = mapped_column(String(500), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=1)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    opened_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship()
