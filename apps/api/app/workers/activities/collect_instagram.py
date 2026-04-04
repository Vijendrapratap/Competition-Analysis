import uuid
import re
from datetime import datetime, timezone

from temporalio import activity

from app.database import async_session
from app.models.data_collection import (
    PageSnapshot, SocialPost, SourceType, Platform, PostType, QualityStatus,
)
from app.utils.apify import run_apify_actor


def _map_ig_type(raw: str | None) -> PostType:
    mapping = {
        "image": PostType.image,
        "video": PostType.video,
        "sidecar": PostType.carousel,
        "reel": PostType.reel,
        "carousel_album": PostType.carousel,
    }
    return mapping.get((raw or "").lower(), PostType.image)


def _extract_hashtags(caption: str | None) -> list[str] | None:
    if not caption:
        return None
    tags = re.findall(r"#(\w+)", caption)
    return tags[:30] if tags else None


@activity.defn
async def collect_instagram_data(competitor_id: str, instagram_handle: str) -> dict:
    """Scrape Instagram profile posts via Apify."""
    handle = instagram_handle.lstrip("@")
    activity.logger.info(f"Collecting Instagram data for {competitor_id}: @{handle}")

    results = await run_apify_actor(
        "apify/instagram-scraper",
        {
            "directUrls": [f"https://www.instagram.com/{handle}/"],
            "resultsType": "posts",
            "resultsLimit": 20,
        },
        timeout=180.0,
    )

    if not results:
        async with async_session() as db:
            snapshot = PageSnapshot(
                competitor_id=uuid.UUID(competitor_id),
                source_type=SourceType.instagram,
                url=f"https://instagram.com/{handle}",
                quality_status=QualityStatus.rejected,
                quality_notes=["apify_instagram_failed"],
                scraped_at=datetime.now(timezone.utc),
            )
            db.add(snapshot)
            await db.commit()
        return {"status": "failed", "posts": 0}

    post_count = 0
    async with async_session() as db:
        # Profile snapshot
        first = results[0] if results else {}
        profile_data = {
            "username": handle,
            "followers": first.get("ownerFollowerCount") or first.get("followersCount"),
        }
        snapshot = PageSnapshot(
            competitor_id=uuid.UUID(competitor_id),
            source_type=SourceType.instagram,
            url=f"https://instagram.com/{handle}",
            metadata=profile_data,
            quality_status=QualityStatus.clean,
            scraped_at=datetime.now(timezone.utc),
        )
        db.add(snapshot)

        for post in results:
            post_id = post.get("id") or post.get("shortCode") or str(uuid.uuid4())
            caption = post.get("caption") or ""

            published = post.get("timestamp") or post.get("takenAtTimestamp")
            pub_dt = None
            if published:
                try:
                    if isinstance(published, (int, float)):
                        pub_dt = datetime.fromtimestamp(published, tz=timezone.utc)
                    else:
                        pub_dt = datetime.fromisoformat(str(published).replace("Z", "+00:00"))
                except (ValueError, TypeError, OSError):
                    pass

            social_post = SocialPost(
                competitor_id=uuid.UUID(competitor_id),
                platform=Platform.instagram,
                post_id=str(post_id),
                post_type=_map_ig_type(post.get("type")),
                caption=caption[:5000] if caption else None,
                hashtags=_extract_hashtags(caption),
                published_at=pub_dt,
                likes=post.get("likesCount") or post.get("likes"),
                comments=post.get("commentsCount") or post.get("comments"),
                shares=None,
                views=post.get("videoViewCount") or post.get("views"),
                media_urls=post.get("images") or ([post["displayUrl"]] if post.get("displayUrl") else None),
                collected_at=datetime.now(timezone.utc),
            )
            db.add(social_post)
            post_count += 1

        await db.commit()

    return {"status": "ok", "posts": post_count}
