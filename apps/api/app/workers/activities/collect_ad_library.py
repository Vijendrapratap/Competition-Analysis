import uuid
from datetime import datetime, timezone

from temporalio import activity

from app.database import async_session
from app.models.data_collection import AdCreative, MediaType, PageSnapshot, SourceType, QualityStatus
from app.utils.apify import run_apify_actor
from sqlalchemy import select


def _map_media_type(raw: str | None) -> MediaType:
    mapping = {
        "image": MediaType.image,
        "video": MediaType.video,
        "carousel": MediaType.carousel,
        "dco": MediaType.carousel,
    }
    return mapping.get((raw or "").lower(), MediaType.image)


@activity.defn
async def collect_ad_library_data(competitor_id: str, ad_library_url: str) -> dict:
    """Scrape Facebook Ad Library via Apify."""
    activity.logger.info(f"Collecting ad library for {competitor_id}: {ad_library_url}")

    results = await run_apify_actor(
        "apify/facebook-ads-scraper",
        {
            "startUrls": [{"url": ad_library_url}],
            "maxItems": 50,
        },
        timeout=180.0,
    )

    if not results:
        async with async_session() as db:
            snapshot = PageSnapshot(
                competitor_id=uuid.UUID(competitor_id),
                source_type=SourceType.ad_library,
                url=ad_library_url,
                quality_status=QualityStatus.rejected,
                quality_notes=["apify_ad_library_failed"],
                scraped_at=datetime.now(timezone.utc),
            )
            db.add(snapshot)
            await db.commit()
        return {"status": "failed", "ads": 0}

    ad_count = 0
    seen_ad_ids = set()
    async with async_session() as db:
        # Get existing ad IDs for this competitor to detect paused ads
        stmt = select(AdCreative.ad_id).where(
            AdCreative.competitor_id == uuid.UUID(competitor_id),
            AdCreative.active == True,
        )
        result = await db.execute(stmt)
        existing_ids = {row[0] for row in result.all()}

        for ad in results:
            ad_id = ad.get("adArchiveID") or ad.get("id") or str(uuid.uuid4())
            ad_id_str = str(ad_id)
            seen_ad_ids.add(ad_id_str)

            headline = ad.get("title") or ad.get("adTitle") or ""
            body = ad.get("bodyText") or ad.get("adBody") or ""
            cta = ad.get("ctaText") or ad.get("callToAction") or ""
            media_type = _map_media_type(ad.get("mediaType") or ad.get("adMediaType"))
            media_url = ad.get("imageUrl") or ad.get("videoUrl")
            landing_url = ad.get("linkUrl") or ad.get("landingPageUrl")

            start_date = ad.get("startDate") or ad.get("adStartedRunning")
            first_seen_dt = None
            if start_date:
                try:
                    first_seen_dt = datetime.fromisoformat(str(start_date).replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

            # Upsert: check if exists
            stmt = select(AdCreative).where(
                AdCreative.competitor_id == uuid.UUID(competitor_id),
                AdCreative.platform == "facebook",
                AdCreative.ad_id == ad_id_str,
            )
            existing = (await db.execute(stmt)).scalar_one_or_none()

            if existing:
                existing.last_seen = datetime.now(timezone.utc)
                existing.active = True
                if headline:
                    existing.headline = headline
                if body:
                    existing.body_text = body
            else:
                creative = AdCreative(
                    competitor_id=uuid.UUID(competitor_id),
                    platform="facebook",
                    ad_id=ad_id_str,
                    headline=headline or None,
                    body_text=body or None,
                    cta=cta or None,
                    media_type=media_type,
                    media_url=media_url,
                    landing_page_url=landing_url,
                    first_seen=first_seen_dt or datetime.now(timezone.utc),
                    last_seen=datetime.now(timezone.utc),
                    active=True,
                )
                db.add(creative)
                ad_count += 1

        # Mark ads not in current results as inactive (paused)
        paused_ids = existing_ids - seen_ad_ids
        if paused_ids:
            for pid in paused_ids:
                stmt = select(AdCreative).where(
                    AdCreative.competitor_id == uuid.UUID(competitor_id),
                    AdCreative.ad_id == pid,
                )
                ad_record = (await db.execute(stmt)).scalar_one_or_none()
                if ad_record:
                    ad_record.active = False

        await db.commit()

    return {"status": "ok", "ads": ad_count, "paused": len(existing_ids - seen_ad_ids) if existing_ids else 0}
