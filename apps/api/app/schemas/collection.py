from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CollectionJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    brand_profile_id: UUID
    job_type: str
    status: str
    triggered_by: str
    competitors_total: int | None
    competitors_completed: int | None
    started_at: datetime | None
    completed_at: datetime | None
    error_log: dict | None
    created_at: datetime


class CollectionTriggerResponse(BaseModel):
    message: str
    job_id: UUID


class DataQualityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    competitor_id: UUID
    source_type: str
    collection_run_id: UUID
    raw_record_count: int
    clean_count: int
    warning_count: int
    rejected_count: int
    rejection_reasons: dict | None
    data_confidence_score: float
    processed_at: datetime
