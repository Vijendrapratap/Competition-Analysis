import uuid
from datetime import datetime, timezone

from temporalio import activity

from app.database import async_session
from app.models.data_collection import (
    PageSnapshot, SocialPost, SourceType, Platform, PostType, QualityStatus,
)
from app.utils.apify import run_apify_actor


def _map_post_type(raw: str | None) -> PostType:
    mapping = {
        "photo": PostType.image,
        "video": PostType.video,
        "link": PostType.text,
        "status": PostType.text,
        "reel": PostType.reel,
        "carousel": PostType.carousel,
    }
    return mapping.get((raw or "").lower(), PostType.text)


@activity.defn
async def collect_facebook_data(competitor_id: str, facebook_url: str) -> dict:
    """Scrape Facebook page posts via Apify."""
    activity.logger.info(f"Collecting Facebook data for {competitor_id}: {facebook_url}")

    results = await run_apify_actor(
        "apify/facebook-pages-scraper",
        {
            "startUrls": [{"url": facebook_url}],
            "maxPosts": 20,
            "maxPostComments": 0,
        },
        timeout=180.0,
    )

    if not results:
        async with async_session() as db:
            snapshot = PageSnapshot(
                competitor_id=uuid.UUID(competitor_id),
                source_type=SourceType.facebook,
                url=facebook_url,
                quality_status=QualityStatus.rejected,
                quality_notes=["apify_facebook_failed"],
                scraped_at=datetime.now(timezone.utc),
            )
            db.add(snapshot)
            await db.commit()
        return {"status": "failed", "posts": 0}

    post_count = 0
    async with async_session() as db:
        # Store profile-level data as PageSnapshot
        first = results[0] if results else {}
        profile_data = {
            "page_name": first.get("pageName"),
            "likes": first.get("likes"),
            "followers": first.get("followers"),
        }
        snapshot = PageSnapshot(
            competitor_id=uuid.UUID(competitor_id),
            source_type=SourceType.facebook,
            url=facebook_url,
            raw_content=str(profile_data),
            extracted_text=None,
            metadata=profile_data,
            quality_status=QualityStatus.clean,
            scraped_at=datetime.now(timezone.utc),
        )
        db.add(snapshot)

        # Store individual posts
        for item in results:
            posts = item.get("posts", [item]) if "posts" not in item else item["posts"]
            if not isinstance(posts, list):
                posts = [item]

            for post in posts:
                post_id = post.get("postId") or post.get("id") or str(uuid.uuid4())
                caption = post.get("text") or post.get("message") or ""
                published = post.get("time") or post.get("timestamp")

                pub_dt = None
                if published:
                    try:
                        pub_dt = datetime.fromisoformat(str(published).replace("Z", "+00:00"))
                    except (ValueError, TypeError):
                        pass

                social_post = SocialPost(
                    competitor_id=uuid.UUID(competitor_id),
                    platform=Platform.facebook,
                    post_id=str(post_id),
                    post_type=_map_post_type(post.get("type")),
                    caption=caption[:5000] if caption else None,
                    hashtags=None,
                    published_at=pub_dt,
                    likes=post.get("likes") or post.get("reactions"),
                    comments=post.get("comments"),
                    shares=post.get("shares"),
                    views=post.get("views"),
                    media_urls=post.get("images") or post.get("media"),
                    collected_at=datetime.now(timezone.utc),
                )
                db.add(social_post)
                post_count += 1

        await db.commit()

    return {"status": "ok", "posts": post_count}
