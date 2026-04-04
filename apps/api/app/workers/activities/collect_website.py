import uuid
from datetime import datetime, timezone

from temporalio import activity
from sqlalchemy import select

from app.database import async_session
from app.models.data_collection import PageSnapshot, SourceType, QualityStatus
from app.utils.firecrawl import crawl_url


@activity.defn
async def collect_website_data(competitor_id: str, website_url: str) -> dict:
    """Crawl competitor website and store page snapshots."""
    activity.logger.info(f"Collecting website data for {competitor_id}: {website_url}")

    pages = await crawl_url(website_url, max_pages=3)

    if not pages:
        # Create rejected snapshot if crawl failed
        async with async_session() as db:
            snapshot = PageSnapshot(
                competitor_id=uuid.UUID(competitor_id),
                source_type=SourceType.website,
                url=website_url,
                raw_content=None,
                extracted_text=None,
                quality_status=QualityStatus.rejected,
                quality_notes=["firecrawl_failed"],
                scraped_at=datetime.now(timezone.utc),
            )
            db.add(snapshot)
            await db.commit()
        return {"status": "failed", "pages": 0}

    async with async_session() as db:
        for page in pages:
            markdown = page.get("markdown", "")
            metadata = page.get("metadata", {})

            snapshot = PageSnapshot(
                competitor_id=uuid.UUID(competitor_id),
                source_type=SourceType.website,
                url=page.get("url", website_url),
                raw_content=markdown,
                extracted_text=markdown[:50000] if markdown else None,
                metadata=metadata,
                quality_status=QualityStatus.clean,
                scraped_at=datetime.now(timezone.utc),
            )
            db.add(snapshot)

        await db.commit()

    return {"status": "ok", "pages": len(pages)}
