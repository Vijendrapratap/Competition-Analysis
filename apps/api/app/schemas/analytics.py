from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class KpiSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    brand_profile_id: UUID
    competitor_id: UUID | None
    filter_mode: str
    period_start: datetime
    period_end: datetime
    kpi_key: str
    kpi_value: float
    kpi_label: str
    delta_pct: float | None
    computed_at: datetime


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    brand_profile_id: UUID
    competitor_id: UUID
    alert_type: str
    severity: str
    title: str
    description: str
    evidence: dict | None
    triggered_at: datetime
    read: bool
    dismissed: bool


class AlertRuleCreate(BaseModel):
    competitor_id: UUID | None = None
    kpi_key: str
    condition: str
    threshold: float


class AlertRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    brand_profile_id: UUID
    competitor_id: UUID | None
    kpi_key: str
    condition: str
    threshold: float
    active: bool
    created_at: datetime


class ShareOfVoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    brand_profile_id: UUID
    period_start: datetime
    period_end: datetime
    filter_mode: str
    entries: list[dict]


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    brand_profile_id: UUID
    filter_mode: str
    period_start: datetime
    period_end: datetime
    executive_summary: str | None
    report_data: dict | None
    generated_at: datetime


class DashboardResponse(BaseModel):
    summary: dict
    executive_summary: str | None
    kpi_snapshots: dict
    competitor_cards: list[dict]
    messaging_themes: list[dict]
    paid_media_summary: dict
    opportunities: list[dict]
    alerts: list[AlertResponse]
