"""
SEO intelligence router.

GET  /brands/{brand_id}/seo/keywords             → tracked keywords
POST /brands/{brand_id}/seo/keywords             → add keyword
GET  /competitors/{comp_id}/seo/rankings         → keyword rankings (time-series)
GET  /competitors/{comp_id}/seo/metrics          → domain authority, traffic, backlinks
GET  /brands/{brand_id}/seo/gaps                 → content gap analysis
GET  /brands/{brand_id}/seo/matrix               → keyword rank comparison across competitors
"""
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import AccountId

router = APIRouter()


# ── Keywords ──────────────────────────────────────────────────────────────────

class KeywordCreate(BaseModel):
    keyword: str
    intent: str = "informational"


@router.get("/brands/{brand_id}/seo/keywords")
async def list_keywords(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.seo import Keyword
        stmt = select(Keyword).where(Keyword.brand_profile_id == brand_id).order_by(Keyword.keyword)
        result = await db.execute(stmt)
        keywords = list(result.scalars().all())
        return {
            "keywords": [
                {"id": str(k.id), "keyword": k.keyword, "intent": str(k.intent)}
                for k in keywords
            ]
        }
    except Exception:
        return {"keywords": []}


@router.post("/brands/{brand_id}/seo/keywords", status_code=201)
async def add_keyword(
    brand_id: UUID,
    body: KeywordCreate,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    from app.models.seo import Keyword, KeywordIntent
    try:
        intent = KeywordIntent(body.intent)
    except ValueError:
        intent = KeywordIntent.informational

    kw = Keyword(brand_profile_id=brand_id, keyword=body.keyword, intent=intent)
    db.add(kw)
    await db.commit()
    await db.refresh(kw)
    return {"id": str(kw.id), "keyword": kw.keyword, "intent": str(kw.intent)}


# ── Rankings ──────────────────────────────────────────────────────────────────

@router.get("/competitors/{competitor_id}/seo/rankings")
async def get_rankings(
    competitor_id: UUID,
    account_id: AccountId,
    days: int = Query(default=30, le=90),
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.seo import KeywordRanking, Keyword
        from sqlalchemy import and_
        from datetime import timedelta

        since = date.today().replace(day=1)  # current month
        stmt = (
            select(KeywordRanking, Keyword.keyword)
            .join(Keyword, KeywordRanking.keyword_id == Keyword.id)
            .where(
                KeywordRanking.competitor_id == competitor_id,
                KeywordRanking.recorded_on >= since,
            )
            .order_by(KeywordRanking.recorded_on.desc())
        )
        result = await db.execute(stmt)
        rows = result.all()
        return {
            "rankings": [
                {
                    "keyword": kw,
                    "rank": r.rank,
                    "url": r.url,
                    "recorded_on": str(r.recorded_on),
                }
                for r, kw in rows
            ]
        }
    except Exception:
        return {"rankings": []}


# ── SEO Metrics ───────────────────────────────────────────────────────────────

@router.get("/competitors/{competitor_id}/seo/metrics")
async def get_seo_metrics(
    competitor_id: UUID,
    account_id: AccountId,
    months: int = Query(default=3, le=12),
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.seo import SeoMetric

        stmt = (
            select(SeoMetric)
            .where(SeoMetric.competitor_id == competitor_id)
            .order_by(desc(SeoMetric.month))
            .limit(months)
        )
        result = await db.execute(stmt)
        metrics = list(result.scalars().all())
        return {
            "metrics": [
                {
                    "month": str(m.month),
                    "domain_authority": m.domain_authority,
                    "organic_traffic_est": m.organic_traffic_est,
                    "backlinks_total": m.backlinks_total,
                    "new_pages": m.new_pages,
                    "keywords_in_top10": m.keywords_in_top10,
                }
                for m in metrics
            ]
        }
    except Exception:
        return {"metrics": []}


# ── Content Gaps ──────────────────────────────────────────────────────────────

@router.get("/brands/{brand_id}/seo/gaps")
async def get_content_gaps(
    brand_id: UUID,
    account_id: AccountId,
    competitor_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.seo import ContentGap, Keyword
        from app.models.competitors import Competitor

        stmt = (
            select(ContentGap, Keyword.keyword, Competitor.name)
            .join(Keyword, ContentGap.keyword_id == Keyword.id)
            .join(Competitor, ContentGap.competitor_id == Competitor.id)
            .where(Keyword.brand_profile_id == brand_id)
        )
        if competitor_id:
            stmt = stmt.where(ContentGap.competitor_id == competitor_id)

        stmt = stmt.order_by(desc(ContentGap.created_at)).limit(50)
        result = await db.execute(stmt)
        rows = result.all()

        return {
            "gaps": [
                {
                    "keyword": kw,
                    "competitor": comp_name,
                    "competitor_ranks": gap.competitor_ranks,
                    "brand_ranks": gap.brand_ranks,
                    "gap_score": gap.gap_score,
                }
                for gap, kw, comp_name in rows
            ]
        }
    except Exception:
        return {"gaps": []}


# ── Rank Comparison Matrix ────────────────────────────────────────────────────

@router.get("/brands/{brand_id}/seo/matrix")
async def get_rank_matrix(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    """Keyword ranking side-by-side across all competitors."""
    try:
        from app.models.seo import Keyword, KeywordRanking
        from app.models.competitors import Competitor

        stmt = select(Keyword).where(Keyword.brand_profile_id == brand_id).limit(20)
        result = await db.execute(stmt)
        keywords = list(result.scalars().all())

        stmt = select(Competitor).where(
            Competitor.brand_profile_id == brand_id,
            Competitor.active == True,
        )
        result = await db.execute(stmt)
        competitors = list(result.scalars().all())

        matrix = []
        for kw in keywords:
            row: dict = {"keyword": kw.keyword, "intent": str(kw.intent), "competitors": {}}
            for comp in competitors:
                stmt = (
                    select(KeywordRanking.rank)
                    .where(
                        KeywordRanking.keyword_id == kw.id,
                        KeywordRanking.competitor_id == comp.id,
                    )
                    .order_by(desc(KeywordRanking.recorded_on))
                    .limit(1)
                )
                result = await db.execute(stmt)
                rank = result.scalar_one_or_none()
                row["competitors"][comp.name] = rank
            matrix.append(row)

        return {"matrix": matrix, "keywords": len(keywords), "competitors": len(competitors)}
    except Exception:
        return {"matrix": [], "keywords": 0, "competitors": 0}
