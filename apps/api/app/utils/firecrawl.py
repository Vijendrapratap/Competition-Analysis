import httpx
import structlog

from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

FIRECRAWL_API_URL = "https://api.firecrawl.dev/v0"


async def crawl_url(url: str, *, max_pages: int = 3) -> list[dict]:
    """Crawl a URL using Firecrawl and return markdown content.

    Returns list of dicts: [{"url": "...", "markdown": "...", "metadata": {...}}]
    """
    if not settings.FIRECRAWL_API_KEY:
        logger.warning("firecrawl_skipped", reason="no API key configured")
        return []

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{FIRECRAWL_API_URL}/scrape",
                headers={
                    "Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "url": url,
                    "pageOptions": {
                        "onlyMainContent": True,
                        "includeMarkdown": True,
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()

        if data.get("success") and data.get("data"):
            page = data["data"]
            return [{
                "url": url,
                "markdown": page.get("markdown", ""),
                "metadata": page.get("metadata", {}),
            }]

        return []

    except Exception as e:
        logger.error("firecrawl_error", url=url, error=str(e))
        return []
