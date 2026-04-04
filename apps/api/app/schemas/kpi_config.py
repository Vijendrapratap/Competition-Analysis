from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class KpiConfigCreate(BaseModel):
    filter_mode: str = "weekly"
    kpi_pack: str = "default"
    kpis: list[str] = []


class KpiConfigUpdate(BaseModel):
    filter_mode: str | None = None
    kpi_pack: str | None = None
    kpis: list[str] | None = None


class KpiConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    brand_profile_id: UUID
    filter_mode: str
    kpi_pack: str
    kpis: list[str]
    created_at: datetime
    updated_at: datetime
