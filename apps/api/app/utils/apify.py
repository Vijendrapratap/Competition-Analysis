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

    # Apify REST paths address actors as "username~actor-name", not "username/actor-name"
    actor_path = actor_id.replace("/", "~")

    try:
        # Bearer auth keeps the token out of URLs (query params end up in error logs)
        headers = {"Authorization": f"Bearer {settings.APIFY_API_TOKEN}"}
        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            # Start actor run
            resp = await client.post(
                f"{APIFY_API_URL}/acts/{actor_path}/runs",
                json=input_data,
            )
            resp.raise_for_status()
            run_data = resp.json()["data"]
            run_id = run_data["id"]

            # Wait for completion
            while True:
                resp = await client.get(
                    f"{APIFY_API_URL}/actor-runs/{run_id}",
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
                params={"format": "json"},
            )
            resp.raise_for_status()
            return resp.json()

    except Exception as e:
        logger.error("apify_error", actor_id=actor_id, error=str(e))
        return []
