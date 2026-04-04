import uuid
from datetime import datetime
import enum
from sqlalchemy import Integer, Enum, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class JobType(str, enum.Enum):
    full_collection = "full_collection"
    incremental = "incremental"
    manual = "manual"


class JobStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    partial = "partial"


class TriggeredBy(str, enum.Enum):
    user = "user"
    schedule = "schedule"
    system = "system"


class CollectionJob(Base):
    __tablename__ = "collection_jobs"
    __table_args__ = (
        Index("ix_collection_jobs_brand_status", "brand_profile_id", "status", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    brand_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("brand_profiles.id"))
    job_type: Mapped[JobType] = mapped_column(Enum(JobType))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.pending)
    triggered_by: Mapped[TriggeredBy] = mapped_column(Enum(TriggeredBy))
    competitors_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    competitors_completed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_log: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
