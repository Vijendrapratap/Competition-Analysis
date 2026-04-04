from fastapi import APIRouter
from sqlalchemy import text

from app.database import async_session

router = APIRouter()


@router.get("/health")
async def health_check():
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "ok",
        "service": "competeiq-api",
        "database": db_status,
    }
