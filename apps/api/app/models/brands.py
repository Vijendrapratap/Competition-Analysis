import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    name: Mapped[str] = mapped_column(String(255))
    website: Mapped[str] = mapped_column(String(500))
    industry: Mapped[str] = mapped_column(String(100))
    target_region: Mapped[str] = mapped_column(String(100))
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    persona: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    social_profiles: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    setup_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    account: Mapped["Account"] = relationship(back_populates="brand_profiles")
    competitors: Mapped[list["Competitor"]] = relationship(back_populates="brand_profile", cascade="all, delete-orphan")
    kpi_config: Mapped["KpiConfig | None"] = relationship(back_populates="brand_profile", uselist=False)
