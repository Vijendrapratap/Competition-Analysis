import uuid
from datetime import datetime
from sqlalchemy import Integer, Numeric, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.data_collection import SourceType


class DataQualityLog(Base):
    __tablename__ = "data_quality_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("competitors.id"))
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType))
    collection_run_id: Mapped[uuid.UUID] = mapped_column()
    raw_record_count: Mapped[int] = mapped_column(Integer)
    clean_count: Mapped[int] = mapped_column(Integer)
    warning_count: Mapped[int] = mapped_column(Integer)
    rejected_count: Mapped[int] = mapped_column(Integer)
    rejection_reasons: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    data_confidence_score: Mapped[float] = mapped_column(Numeric)
    processed_at: Mapped[datetime] = mapped_column(server_default=func.now())
