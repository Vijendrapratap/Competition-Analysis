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
        "image": PostType.image,
        "video": PostType.video,
        "article": PostType.text,
        "document": PostType.carousel,
        "poll": PostType.text,
    }
    return mapping.get((raw or "").lower(), PostType.text)


@activity.defn
async def collect_linkedin_data(competitor_id: str, linkedin_url: str) -> dict:
    """Scrape LinkedIn company page posts via Apify."""
    activity.logger.info(f"Collecting LinkedIn data for {competitor_id}: {linkedin_url}")

    results = await run_apify_actor(
        "curious_coder/linkedin-company-posts-scraper",
        {
            "companyUrls": [linkedin_url],
            "maxPosts": 20,
        },
        timeout=240.0,
    )

    if not results:
        async with async_session() as db:
            snapshot = PageSnapshot(
                competitor_id=uuid.UUID(competitor_id),
                source_type=SourceType.linkedin,
                url=linkedin_url,
                quality_status=QualityStatus.rejected,
                quality_notes=["apify_linkedin_failed"],
                scraped_at=datetime.now(timezone.utc),
            )
            db.add(snapshot)
            await db.commit()
        return {"status": "failed", "posts": 0}

    post_count = 0
    async with async_session() as db:
        # Store profile snapshot
        first = results[0] if results else {}
        profile_data = {
            "company_name": first.get("companyName"),
            "followers": first.get("followersCount"),
            "employees": first.get("employeeCount"),
            "description": first.get("description"),
        }
        snapshot = PageSnapshot(
            competitor_id=uuid.UUID(competitor_id),
            source_type=SourceType.linkedin,
            url=linkedin_url,
            raw_content=str(profile_data),
            extra_metadata=profile_data,
            quality_status=QualityStatus.clean,
            scraped_at=datetime.now(timezone.utc),
        )
        db.add(snapshot)

        # Store individual posts
        for item in results:
            posts = item.get("posts", [item])
            if not isinstance(posts, list):
                posts = [item]

            for post in posts:
                post_id = post.get("urn") or post.get("id") or str(uuid.uuid4())
                caption = post.get("text") or post.get("commentary") or ""
                published = post.get("postedAt") or post.get("publishedAt")

                pub_dt = None
                if published:
                    try:
                        pub_dt = datetime.fromisoformat(str(published).replace("Z", "+00:00"))
                    except (ValueError, TypeError):
                        pub_dt = datetime.now(timezone.utc)

                reactions = post.get("totalReactionCount") or post.get("likes") or 0
                comments = post.get("totalCommentCount") or post.get("comments") or 0

                # Compute engagement rate
                followers = profile_data.get("followers") or 0
                eng_rate = None
                if followers and followers > 0:
                    eng_rate = (reactions + comments) / followers

                social_post = SocialPost(
                    competitor_id=uuid.UUID(competitor_id),
                    platform=Platform.linkedin,
                    post_id=str(post_id),
                    post_type=_map_post_type(post.get("type")),
                    caption=caption[:5000] if caption else None,
                    hashtags=post.get("hashtags"),
                    published_at=pub_dt,
                    likes=reactions,
                    comments=comments,
                    shares=post.get("shareCount") or post.get("reposts") or 0,
                    views=post.get("impressionCount"),
                    engagement_rate=eng_rate,
                    media_urls=post.get("images") or post.get("videoUrl"),
                    collected_at=datetime.now(timezone.utc),
                )
                db.add(social_post)
                post_count += 1

        await db.commit()

    return {"status": "ok", "posts": post_count}
