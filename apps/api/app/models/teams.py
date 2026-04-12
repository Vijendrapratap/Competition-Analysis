"""
Team management: invitations and user preferences.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Enum, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.accounts import UserRole


class InvitationStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    expired = "expired"
    revoked = "revoked"


class Invitation(Base):
    """
    Pending invitation to join an account.
    Token is emailed; expires after 7 days.
    """
    __tablename__ = "invitations"
    __table_args__ = (
        Index("ix_invitations_token", "token"),
        Index("ix_invitations_account_status", "account_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    invited_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    email: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.viewer)
    token: Mapped[str] = mapped_column(String(128), unique=True)
    status: Mapped[InvitationStatus] = mapped_column(Enum(InvitationStatus), default=InvitationStatus.pending)
    accepted_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    expires_at: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    account: Mapped["Account"] = relationship()
    inviter: Mapped["User"] = relationship(foreign_keys=[invited_by])


class UserPreference(Base):
    """
    Per-user UI/UX preferences (theme, default filters, dashboard layout, etc.)
    One row per user; upserted on change.
    """
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    theme: Mapped[str] = mapped_column(String(20), default="light")        # light | dark | system
    default_filter_mode: Mapped[str] = mapped_column(String(20), default="weekly")
    default_competitor_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    dashboard_layout: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    onboarding_step: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship()


class SavedView(Base):
    """
    User-saved filter combinations for the dashboard.
    e.g. "LinkedIn vs Salesforce — last 30 days"
    """
    __tablename__ = "saved_views"
    __table_args__ = (
        Index("ix_saved_views_user", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    filters: Mapped[dict] = mapped_column(JSONB)    # {competitor_ids, filter_mode, date_range, kpi_keys}
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship()
