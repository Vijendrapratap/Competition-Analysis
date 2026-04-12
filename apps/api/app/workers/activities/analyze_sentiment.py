"""
Sentiment analysis activity.

Runs after social collection. Uses LLM to score each uncategorised post
for sentiment (positive/neutral/negative) and emotion tags.
Batches up to 40 posts per LLM call to minimise costs.
Also writes an aggregated SentimentSnapshot KPI.
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from temporalio import activity
from sqlalchemy import select, desc

from app.database import async_session
from app.models.data_collection import SocialPost
from app.models.analytics import KpiSnapshot
from app.models.competitors import Competitor
from app.utils.llm import call_openrouter


SENTIMENT_SYSTEM_PROMPT = """You are a sentiment analyst specializing in B2B marketing content.
Analyze each numbered post and return sentiment scores.
Respond ONLY as JSON:
{
  "results": [
    {
      "index": 1,
      "sentiment": "positive|neutral|negative",
      "score": 0.75,
      "emotions": ["confident", "educational"],
      "intent": "thought_leadership|product_push|social_proof|engagement|promotional"
    }
  ]
}
"""


@activity.defn
async def run_sentiment_analysis(
    competitor_id: str,
    filter_mode: str,
    period_start: str,
    period_end: str,
) -> dict:
    """Score uncategorised social posts for sentiment and intent."""
    activity.logger.info(f"Sentiment analysis for {competitor_id}")
    comp_uuid = uuid.UUID(competitor_id)
    p_start = datetime.fromisoformat(period_start)
    p_end = datetime.fromisoformat(period_end)

    async with async_session() as db:
        # Get posts without sentiment scores
        stmt = (
            select(SocialPost)
            .where(
                SocialPost.competitor_id == comp_uuid,
                SocialPost.published_at >= p_start,
                SocialPost.published_at <= p_end,
                SocialPost.sentiment_score.is_(None),
                SocialPost.caption.isnot(None),
            )
            .order_by(desc(SocialPost.published_at))
            .limit(40)
        )
        result = await db.execute(stmt)
        posts = list(result.scalars().all())

        if not posts:
            return {"status": "no_unscored_posts", "scored": 0}

        # Build numbered prompt
        numbered_posts = []
        for i, post in enumerate(posts, 1):
            numbered_posts.append(f"{i}. {(post.caption or '')[:300]}")

        try:
            sentiment_data = await call_openrouter(
                system_prompt=SENTIMENT_SYSTEM_PROMPT,
                user_prompt="\n\n".join(numbered_posts),
                model="google/gemini-2.0-flash",
            )
        except Exception as e:
            activity.logger.warning(f"Sentiment LLM failed: {e}")
            return {"status": "llm_failed", "scored": 0}

        # Apply scores to posts
        results = sentiment_data.get("results", [])
        scored = 0
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}

        for item in results:
            idx = item.get("index", 0) - 1
            if 0 <= idx < len(posts):
                post = posts[idx]
                score = item.get("score", 0.5)
                post.sentiment_score = Decimal(str(round(score, 4)))
                post.sentiment_label = item.get("sentiment", "neutral")
                # Store emotions/intent in extra_metadata if field exists
                # (graceful — field may not exist on all DBs)
                try:
                    if hasattr(post, "extra_metadata") and post.extra_metadata is None:
                        post.extra_metadata = {}
                    if hasattr(post, "extra_metadata"):
                        post.extra_metadata = {
                            **(post.extra_metadata or {}),
                            "emotions": item.get("emotions", []),
                            "intent": item.get("intent", "unknown"),
                        }
                except Exception:
                    pass

                sentiment_counts[item.get("sentiment", "neutral")] = (
                    sentiment_counts.get(item.get("sentiment", "neutral"), 0) + 1
                )
                scored += 1

        # Get brand_profile_id
        stmt = select(Competitor.brand_profile_id).where(Competitor.id == comp_uuid)
        result = await db.execute(stmt)
        brand_profile_id = result.scalar_one()

        # Write aggregate sentiment KPI
        pos = sentiment_counts["positive"]
        neg = sentiment_counts["negative"]
        total = scored or 1
        net_sentiment = (pos - neg) / total  # range -1 to 1

        snapshot = KpiSnapshot(
            brand_profile_id=brand_profile_id,
            competitor_id=comp_uuid,
            filter_mode=filter_mode,
            period_start=p_start,
            period_end=p_end,
            kpi_key="net_sentiment_score",
            kpi_value=Decimal(str(round(net_sentiment, 4))),
            kpi_label="Net sentiment score (social posts)",
            metadata={
                "positive": pos,
                "neutral": sentiment_counts["neutral"],
                "negative": neg,
                "total_scored": scored,
            },
        )
        db.add(snapshot)

        await db.commit()

    return {
        "status": "ok",
        "scored": scored,
        "positive": sentiment_counts["positive"],
        "neutral": sentiment_counts["neutral"],
        "negative": sentiment_counts["negative"],
        "net_sentiment": round(net_sentiment, 3),
    }
