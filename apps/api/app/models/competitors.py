import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CompetitorTier(str, enum.Enum):
    direct = "direct"
    indirect = "indirect"
    aspirational = "aspirational"
    regional = "regional"


class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id"))
    name: Mapped[str] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tier: Mapped[CompetitorTier] = mapped_column(Enum(CompetitorTier), default=CompetitorTier.direct)
    social_profiles: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ad_library_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    ai_discovered: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    brand_profile: Mapped["BrandProfile"] = relationship(back_populates="competitors")
