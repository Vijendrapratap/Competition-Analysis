import uuid
import enum
from datetime import datetime
from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class FilterMode(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class KpiPack(str, enum.Enum):
    default = "default"
    custom = "custom"


class KpiConfig(Base):
    __tablename__ = "kpi_configs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id"), unique=True)
    filter_mode: Mapped[FilterMode] = mapped_column(Enum(FilterMode), default=FilterMode.weekly)
    kpi_pack: Mapped[KpiPack] = mapped_column(Enum(KpiPack), default=KpiPack.default)
    kpis: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    brand_profile: Mapped["BrandProfile"] = relationship(back_populates="kpi_config")
