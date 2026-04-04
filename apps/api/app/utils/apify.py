import httpx
import structlog

from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

APIFY_API_URL = "https://api.apify.com/v2"


async def run_apify_actor(actor_id: str, input_data: dict, *, timeout: float = 120.0) -> list[dict]:
    """Run an Apify actor and return the results."""
    if not settings.APIFY_API_TOKEN:
        logger.warning("apify_skipped", reason="no API token configured")
        return []

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Start actor run
            resp = await client.post(
                f"{APIFY_API_URL}/acts/{actor_id}/runs",
                params={"token": settings.APIFY_API_TOKEN},
                json=input_data,
            )
            resp.raise_for_status()
            run_data = resp.json()["data"]
            run_id = run_data["id"]

            # Wait for completion
            while True:
                resp = await client.get(
                    f"{APIFY_API_URL}/actor-runs/{run_id}",
                    params={"token": settings.APIFY_API_TOKEN},
                )
                resp.raise_for_status()
                status = resp.json()["data"]["status"]

                if status == "SUCCEEDED":
                    break
                elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
                    logger.error("apify_actor_failed", actor_id=actor_id, status=status)
                    return []

                import asyncio
                await asyncio.sleep(3)

            # Get results
            dataset_id = resp.json()["data"]["defaultDatasetId"]
            resp = await client.get(
                f"{APIFY_API_URL}/datasets/{dataset_id}/items",
                params={"token": settings.APIFY_API_TOKEN, "format": "json"},
            )
            resp.raise_for_status()
            return resp.json()

    except Exception as e:
        logger.error("apify_error", actor_id=actor_id, error=str(e))
        return []
