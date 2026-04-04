import uuid
import re
from datetime import datetime, timezone, timedelta

from temporalio import activity
from sqlalchemy import select, func

from app.database import async_session
from app.models.data_collection import PageSnapshot, SocialPost, QualityStatus
from app.models.data_quality import DataQualityLog
from app.utils.llm import call_openrouter


# URL patterns to reject
REJECT_URL_PATTERNS = [
    r"/cdn-cgi/",
    r"\.cloudfront\.net/assets/",
    r"/pixel/",
    r"/tracking/",
    r"/analytics/",
    r"\.gif\?",
    r"utm_source=",
]
REJECT_URL_RE = re.compile("|".join(REJECT_URL_PATTERNS), re.IGNORECASE)


@activity.defn
async def run_data_hygiene(competitor_id: str, collection_job_id: str) -> dict:
    """Three-layer data validation pipeline."""
    activity.logger.info(f"Running data hygiene for competitor {competitor_id}")

    comp_uuid = uuid.UUID(competitor_id)
    job_uuid = uuid.UUID(collection_job_id)

    async with async_session() as db:
        # Load recent snapshots (from this collection run)
        stmt = select(PageSnapshot).where(
            PageSnapshot.competitor_id == comp_uuid,
        ).order_by(PageSnapshot.created_at.desc()).limit(50)
        result = await db.execute(stmt)
        snapshots = list(result.scalars().all())

        raw_count = len(snapshots)
        clean_count = 0
        warning_count = 0
        rejected_count = 0
        rejection_reasons: dict[str, int] = {}

        # ── Layer 1: Source Validation (rule-based) ──
        for snap in snapshots:
            if snap.quality_status == QualityStatus.rejected:
                rejected_count += 1
                continue

            notes = list(snap.quality_notes or [])
            status = QualityStatus.clean

            # Check URL validity
            if snap.url and REJECT_URL_RE.search(snap.url):
                status = QualityStatus.rejected
                notes.append("invalid_url_pattern")
                rejection_reasons["invalid_url_pattern"] = rejection_reasons.get("invalid_url_pattern", 0) + 1

            # Check content minimum
            elif snap.raw_content and len(snap.raw_content.strip()) < 50:
                status = QualityStatus.rejected
                notes.append("content_too_short")
                rejection_reasons["content_too_short"] = rejection_reasons.get("content_too_short", 0) + 1

            elif snap.extracted_text and len(snap.extracted_text.strip()) < 100:
                status = QualityStatus.warning
                notes.append("extracted_text_thin")

            # Check data freshness
            if snap.scraped_at:
                age = datetime.now(timezone.utc) - snap.scraped_at.replace(tzinfo=timezone.utc)
                if age > timedelta(days=7):
                    if status == QualityStatus.clean:
                        status = QualityStatus.warning
                    notes.append("stale_data")

            # Check response size (potential scraping artifact)
            if snap.raw_content and len(snap.raw_content) > 50000:
                if status == QualityStatus.clean:
                    status = QualityStatus.warning
                notes.append("oversized_content")

            snap.quality_status = status
            snap.quality_notes = notes if notes else None

            if status == QualityStatus.clean:
                clean_count += 1
            elif status == QualityStatus.warning:
                warning_count += 1
            else:
                rejected_count += 1

        # ── Layer 2: Deduplication + Normalization ──
        # Social post dedup is handled by DB unique constraint (competitor_id, platform, post_id)
        # Normalize engagement rates
        stmt = select(SocialPost).where(SocialPost.competitor_id == comp_uuid)
        result = await db.execute(stmt)
        posts = list(result.scalars().all())

        # Try to get follower count from page snapshot metadata
        follower_count = None
        for snap in snapshots:
            if snap.metadata and isinstance(snap.metadata, dict):
                fc = snap.metadata.get("followers") or snap.metadata.get("followersCount")
                if fc and isinstance(fc, (int, float)) and fc > 0:
                    follower_count = int(fc)
                    break

        for post in posts:
            likes = post.likes or 0
            comments = post.comments or 0
            shares = post.shares or 0
            if follower_count and follower_count > 0:
                post.engagement_rate = (likes + comments + shares) / follower_count

        # ── Layer 3: Contextual Validation (LLM, only if needed) ──
        if raw_count > 0 and (warning_count / max(raw_count, 1)) > 0.2:
            activity.logger.info(f"Layer 3: >20% warnings ({warning_count}/{raw_count}), running LLM validation")

            warning_snapshots = [s for s in snapshots if s.quality_status == QualityStatus.warning][:10]
            if warning_snapshots:
                batch_text = "\n---\n".join(
                    f"URL: {s.url}\nContent preview: {(s.extracted_text or s.raw_content or '')[:200]}"
                    for s in warning_snapshots
                )

                try:
                    llm_result = await call_openrouter(
                        system_prompt="You are a data quality validator. For each content snippet, respond with JSON: {\"results\": [{\"index\": 0, \"valid\": true/false, \"reason\": \"...\"}]}",
                        user_prompt=f"Validate these web content snippets. Are they legitimate business content?\n\n{batch_text}",
                        model="google/gemini-2.0-flash",
                    )

                    for item in llm_result.get("results", []):
                        idx = item.get("index", -1)
                        if 0 <= idx < len(warning_snapshots):
                            snap = warning_snapshots[idx]
                            if item.get("valid"):
                                snap.quality_status = QualityStatus.clean
                                warning_count -= 1
                                clean_count += 1
                            else:
                                snap.quality_status = QualityStatus.rejected
                                snap.quality_notes = list(snap.quality_notes or []) + [f"llm_rejected: {item.get('reason', '')}"]
                                warning_count -= 1
                                rejected_count += 1
                except Exception as e:
                    activity.logger.warning(f"Layer 3 LLM validation failed: {e}")

        # Calculate confidence score
        confidence = (clean_count / max(raw_count, 1)) * 100

        # Write DataQualityLog
        log = DataQualityLog(
            competitor_id=comp_uuid,
            source_type=snapshots[0].source_type if snapshots else "website",
            collection_run_id=job_uuid,
            raw_record_count=raw_count,
            clean_count=clean_count,
            warning_count=warning_count,
            rejected_count=rejected_count,
            rejection_reasons=rejection_reasons if rejection_reasons else None,
            data_confidence_score=round(confidence, 1),
        )
        db.add(log)
        await db.commit()

    return {
        "raw": raw_count,
        "clean": clean_count,
        "warnings": warning_count,
        "rejected": rejected_count,
        "confidence": round(confidence, 1),
    }
