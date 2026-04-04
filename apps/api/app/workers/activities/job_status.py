from datetime import datetime, timezone
from uuid import UUID

from temporalio import activity
from sqlalchemy import select

from app.database import async_session
from app.models.collection_jobs import CollectionJob


@activity.defn
async def update_job_status(
    job_id: str,
    status: str,
    error_log: list[dict] | None = None,
) -> None:
    async with async_session() as db:
        stmt = select(CollectionJob).where(CollectionJob.id == UUID(job_id))
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()
        if not job:
            return

        job.status = status
        if status == "running":
            job.started_at = datetime.now(timezone.utc)
        elif status in ("completed", "failed", "partial"):
            job.completed_at = datetime.now(timezone.utc)
        if error_log:
            job.error_log = {"errors": error_log}
        await db.commit()


@activity.defn
async def mark_competitor_complete(job_id: str, count: int) -> None:
    async with async_session() as db:
        stmt = select(CollectionJob).where(CollectionJob.id == UUID(job_id))
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()
        if job:
            job.competitors_completed = count
            await db.commit()
