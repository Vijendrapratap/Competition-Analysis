import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class PlanType(str, enum.Enum):
    starter = "starter"
    growth = "growth"
    enterprise = "enterprise"


class UserRole(str, enum.Enum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    plan: Mapped[PlanType] = mapped_column(Enum(PlanType), default=PlanType.starter)
    # Subscription / billing
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    plan_expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    trial_ends_at: Mapped[datetime | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    users: Mapped[list["User"]] = relationship(back_populates="account")
    brand_profiles: Mapped[list["BrandProfile"]] = relationship(back_populates="account")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    clerk_user_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.owner)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    account: Mapped["Account"] = relationship(back_populates="users")
