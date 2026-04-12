"""
Audit log and activity tracking.
Every important user action and system event is recorded here.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Text, Enum, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AuditAction(str, enum.Enum):
    # Auth
    user_login = "user_login"
    user_logout = "user_logout"
    user_invited = "user_invited"
    user_role_changed = "user_role_changed"
    user_removed = "user_removed"

    # Brand
    brand_created = "brand_created"
    brand_updated = "brand_updated"
    brand_deleted = "brand_deleted"

    # Competitors
    competitor_added = "competitor_added"
    competitor_updated = "competitor_updated"
    competitor_removed = "competitor_removed"

    # Collection
    collection_triggered = "collection_triggered"
    schedule_created = "schedule_created"
    schedule_updated = "schedule_updated"
    schedule_deleted = "schedule_deleted"

    # Settings
    kpi_config_updated = "kpi_config_updated"
    alert_rule_created = "alert_rule_created"
    alert_rule_deleted = "alert_rule_deleted"
    notification_prefs_updated = "notification_prefs_updated"

    # Reports
    report_generated = "report_generated"
    report_downloaded = "report_downloaded"

    # Billing
    plan_upgraded = "plan_upgraded"
    plan_downgraded = "plan_downgraded"

    # Integrations
    integration_connected = "integration_connected"
    integration_disconnected = "integration_disconnected"
    webhook_created = "webhook_created"
    webhook_deleted = "webhook_deleted"


class AuditLog(Base):
    """
    Immutable audit trail. Never update or delete rows.
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_account_created", "account_id", "created_at"),
        Index("ix_audit_logs_user_created", "user_id", "created_at"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction))
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. "competitor"
    resource_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    resource_label: Mapped[str | None] = mapped_column(String(500), nullable=True)  # human-readable name snapshot
    before_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)    # IPv4/IPv6
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User | None"] = relationship()
