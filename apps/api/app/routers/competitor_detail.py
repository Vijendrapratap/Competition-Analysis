from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import AccountId
from app.models.brands import BrandProfile
from app.models.competitors import Competitor
from app.models.data_collection import SocialPost, AdCreative, MessageTheme, WebsiteChange, PageSnapshot
from app.models.analytics import KpiSnapshot
from app.models.data_quality import DataQualityLog

router = APIRouter()


async def _verify_competitor_access(competitor_id: UUID, account_id: UUID, db: AsyncSession) -> Competitor:
    stmt = (
        select(Competitor)
        .join(BrandProfile, Competitor.brand_profile_id == BrandProfile.id)
        .where(Competitor.id == competitor_id, BrandProfile.account_id == account_id)
    )
    result = await db.execute(stmt)
    competitor = result.scalar_one_or_none()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return competitor


@router.get("/competitors/{competitor_id}/profile")
async def get_competitor_profile(
    competitor_id: UUID,
    account_id: AccountId,
    filter_mode: str = Query(default="weekly"),
    db: AsyncSession = Depends(get_db),
):
    competitor = await _verify_competitor_access(competitor_id, account_id, db)

    # Basic metrics from KPI snapshots
    stmt = (
        select(KpiSnapshot)
        .where(KpiSnapshot.competitor_id == competitor_id)
        .order_by(desc(KpiSnapshot.computed_at))
        .limit(20)
    )
    result = await db.execute(stmt)
    snapshots = result.scalars().all()
    metrics = {}
    for s in snapshots:
        if s.kpi_key not in metrics:
            metrics[s.kpi_key] = {"value": float(s.kpi_value), "delta": float(s.delta_pct) if s.delta_pct else None}

    # Post count
    stmt = select(func.count()).select_from(SocialPost).where(SocialPost.competitor_id == competitor_id)
    result = await db.execute(stmt)
    posts_count = result.scalar() or 0

    # Active ads count
    stmt = select(func.count()).select_from(AdCreative).where(
        AdCreative.competitor_id == competitor_id, AdCreative.active == True
    )
    result = await db.execute(stmt)
    active_ads = result.scalar() or 0

    # Best post
    stmt = (
        select(SocialPost)
        .where(SocialPost.competitor_id == competitor_id)
        .order_by(desc(SocialPost.likes))
        .limit(1)
    )
    result = await db.execute(stmt)
    best = result.scalar_one_or_none()
    best_post = None
    if best:
        best_post = {
            "caption": best.caption,
            "likes": best.likes or 0,
            "comments": best.comments or 0,
            "shares": best.shares or 0,
            "post_type": best.post_type.value if best.post_type else None,
        }

    # Format mix
    stmt = (
        select(SocialPost.post_type, func.count().label("count"))
        .where(SocialPost.competitor_id == competitor_id)
        .group_by(SocialPost.post_type)
    )
    result = await db.execute(stmt)
    format_mix = [{"name": row[0].value if row[0] else "unknown", "value": row[1]} for row in result.all()]

    # Top hashtags
    stmt = select(SocialPost.hashtags).where(
        SocialPost.competitor_id == competitor_id,
        SocialPost.hashtags != None,
    ).limit(50)
    result = await db.execute(stmt)
    all_tags: dict[str, int] = {}
    for (tags,) in result.all():
        if tags:
            for tag in tags:
                all_tags[tag] = all_tags.get(tag, 0) + 1
    top_hashtags = sorted(all_tags, key=all_tags.get, reverse=True)[:15]

    # Data confidence
    stmt = (
        select(DataQualityLog.data_confidence_score)
        .where(DataQualityLog.competitor_id == competitor_id)
        .order_by(desc(DataQualityLog.processed_at))
        .limit(1)
    )
    result = await db.execute(stmt)
    confidence = result.scalar_one_or_none()

    # Platform breakdown
    stmt = (
        select(
            SocialPost.platform,
            func.count().label("posts"),
            func.avg(SocialPost.engagement_rate).label("engagement"),
        )
        .where(SocialPost.competitor_id == competitor_id)
        .group_by(SocialPost.platform)
    )
    result = await db.execute(stmt)
    platform_breakdown = {}
    for row in result.all():
        platform_breakdown[row[0].value] = {
            "posts": row[1],
            "engagement": float(row[2]) if row[2] else None,
            "followers": None,
        }

    return {
        "name": competitor.name,
        "tier": competitor.tier.value,
        "website": competitor.website,
        "metrics": {
            "posts_count": posts_count,
            "active_ads": active_ads,
            "avg_engagement": metrics.get("engagement_rate", {}).get("value"),
            "follower_delta": metrics.get("follower_growth_delta", {}).get("delta"),
            "followers": None,
            "posts_delta": metrics.get("posting_frequency", {}).get("delta"),
        },
        "best_post": best_post,
        "format_mix": format_mix,
        "top_hashtags": top_hashtags,
        "data_confidence": float(confidence) if confidence else None,
        "platform_breakdown": platform_breakdown,
    }


@router.get("/competitors/{competitor_id}/posts")
async def get_competitor_posts(
    competitor_id: UUID,
    account_id: AccountId,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=50),
    db: AsyncSession = Depends(get_db),
):
    await _verify_competitor_access(competitor_id, account_id, db)
    offset = (page - 1) * limit
    stmt = (
        select(SocialPost)
        .where(SocialPost.competitor_id == competitor_id)
        .order_by(desc(SocialPost.published_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    posts = result.scalars().all()
    return [
        {
            "post_id": p.post_id,
            "platform": p.platform.value,
            "post_type": p.post_type.value if p.post_type else None,
            "caption": p.caption,
            "likes": p.likes,
            "comments": p.comments,
            "shares": p.shares,
            "views": p.views,
            "published_at": p.published_at.isoformat() if p.published_at else None,
        }
        for p in posts
    ]


@router.get("/competitors/{competitor_id}/ads")
async def get_competitor_ads(
    competitor_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    await _verify_competitor_access(competitor_id, account_id, db)
    stmt = (
        select(AdCreative)
        .where(AdCreative.competitor_id == competitor_id, AdCreative.active == True)
        .order_by(desc(AdCreative.first_seen))
    )
    result = await db.execute(stmt)
    ads = result.scalars().all()
    return [
        {
            "ad_id": a.ad_id,
            "platform": a.platform,
            "headline": a.headline,
            "body_text": a.body_text,
            "cta": a.cta,
            "media_type": a.media_type.value if a.media_type else None,
            "media_url": a.media_url,
            "landing_page_url": a.landing_page_url,
            "first_seen": a.first_seen.isoformat() if a.first_seen else None,
            "last_seen": a.last_seen.isoformat() if a.last_seen else None,
        }
        for a in ads
    ]


@router.get("/competitors/{competitor_id}/changes")
async def get_competitor_changes(
    competitor_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    await _verify_competitor_access(competitor_id, account_id, db)
    stmt = (
        select(WebsiteChange)
        .where(WebsiteChange.competitor_id == competitor_id)
        .order_by(desc(WebsiteChange.detected_at))
        .limit(20)
    )
    result = await db.execute(stmt)
    changes = result.scalars().all()
    return [
        {
            "change_type": c.change_type.value,
            "before_value": c.before_value,
            "after_value": c.after_value,
            "significance": c.significance.value,
            "detected_at": c.detected_at.isoformat() if c.detected_at else None,
        }
        for c in changes
    ]


@router.get("/competitors/{competitor_id}/themes")
async def get_competitor_themes(
    competitor_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    await _verify_competitor_access(competitor_id, account_id, db)
    stmt = (
        select(MessageTheme)
        .where(MessageTheme.competitor_id == competitor_id)
        .order_by(desc(MessageTheme.frequency))
        .limit(10)
    )
    result = await db.execute(stmt)
    themes = result.scalars().all()
    return [
        {
            "theme": t.theme,
            "frequency": t.frequency,
            "evidence": t.evidence or [],
            "source": t.source.value,
        }
        for t in themes
    ]
