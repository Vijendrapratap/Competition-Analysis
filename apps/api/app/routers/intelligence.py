"""
Intelligence router — analyst layer endpoints.

GET  /brands/{brand_id}/intelligence/summary      → latest IntelligenceSummary
GET  /brands/{brand_id}/intelligence/benchmarks   → rolling benchmarks
GET  /competitors/{comp_id}/notes                 → analyst notes
POST /competitors/{comp_id}/notes                 → add note
GET  /competitors/{comp_id}/tags                  → taxonomy tags
POST /competitors/{comp_id}/tags                  → add tag
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import AccountId

router = APIRouter()


# ── Intelligence Summary ──────────────────────────────────────────────────────

@router.get("/brands/{brand_id}/intelligence/summary")
async def get_intelligence_summary(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.intelligence import IntelligenceSummary
        stmt = (
            select(IntelligenceSummary)
            .where(IntelligenceSummary.brand_profile_id == brand_id)
            .order_by(desc(IntelligenceSummary.generated_at))
            .limit(1)
        )
        result = await db.execute(stmt)
        summary = result.scalar_one_or_none()
        if not summary:
            return {"summary": None, "generated_at": None}
        return {
            "summary": summary.summary_text,
            "period": summary.period,
            "key_findings": summary.key_findings,
            "recommended_actions": summary.recommended_actions,
            "generated_at": summary.generated_at.isoformat() if summary.generated_at else None,
        }
    except Exception:
        return {"summary": None, "generated_at": None}


# ── Benchmarks ────────────────────────────────────────────────────────────────

@router.get("/brands/{brand_id}/intelligence/benchmarks")
async def get_benchmarks(
    brand_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.intelligence import Benchmark
        stmt = (
            select(Benchmark)
            .where(Benchmark.brand_profile_id == brand_id)
            .order_by(desc(Benchmark.computed_at))
            .limit(20)
        )
        result = await db.execute(stmt)
        benchmarks = list(result.scalars().all())
        return {
            "benchmarks": [
                {
                    "metric_key": b.metric_key,
                    "brand_value": float(b.brand_value) if b.brand_value else None,
                    "market_avg": float(b.market_avg) if b.market_avg else None,
                    "market_top": float(b.market_top) if b.market_top else None,
                    "percentile": b.percentile,
                    "computed_at": b.computed_at.isoformat() if b.computed_at else None,
                }
                for b in benchmarks
            ]
        }
    except Exception:
        return {"benchmarks": []}


# ── Competitor Notes ──────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    content: str
    visibility: str = "team"


@router.get("/competitors/{competitor_id}/notes")
async def get_competitor_notes(
    competitor_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.intelligence import CompetitorNote
        stmt = (
            select(CompetitorNote)
            .where(CompetitorNote.competitor_id == competitor_id)
            .order_by(desc(CompetitorNote.created_at))
        )
        result = await db.execute(stmt)
        notes = list(result.scalars().all())
        return {
            "notes": [
                {
                    "id": str(n.id),
                    "content": n.content,
                    "visibility": str(n.visibility),
                    "author_id": str(n.author_id) if n.author_id else None,
                    "created_at": n.created_at.isoformat() if n.created_at else None,
                }
                for n in notes
            ]
        }
    except Exception:
        return {"notes": []}


@router.post("/competitors/{competitor_id}/notes", status_code=201)
async def create_competitor_note(
    competitor_id: UUID,
    body: NoteCreate,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.intelligence import CompetitorNote, NoteVisibility
        try:
            visibility = NoteVisibility(body.visibility)
        except ValueError:
            visibility = NoteVisibility.team

        note = CompetitorNote(
            competitor_id=competitor_id,
            content=body.content,
            visibility=visibility,
        )
        db.add(note)
        await db.commit()
        await db.refresh(note)
        return {"id": str(note.id), "content": note.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Competitor Tags ───────────────────────────────────────────────────────────

class TagCreate(BaseModel):
    name: str
    color: str | None = None


@router.get("/competitors/{competitor_id}/tags")
async def get_competitor_tags(
    competitor_id: UUID,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.intelligence import CompetitorTagLink, CompetitorTag
        from sqlalchemy.orm import selectinload
        stmt = (
            select(CompetitorTagLink)
            .options(selectinload(CompetitorTagLink.tag))
            .where(CompetitorTagLink.competitor_id == competitor_id)
        )
        result = await db.execute(stmt)
        links = list(result.scalars().all())
        return {
            "tags": [
                {"id": str(lnk.tag.id), "name": lnk.tag.name, "color": lnk.tag.color}
                for lnk in links
                if lnk.tag
            ]
        }
    except Exception:
        return {"tags": []}


@router.post("/competitors/{competitor_id}/tags", status_code=201)
async def add_competitor_tag(
    competitor_id: UUID,
    body: TagCreate,
    account_id: AccountId,
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.intelligence import CompetitorTag, CompetitorTagLink
        # Get or create tag
        stmt = select(CompetitorTag).where(CompetitorTag.name == body.name)
        result = await db.execute(stmt)
        tag = result.scalar_one_or_none()
        if not tag:
            tag = CompetitorTag(name=body.name, color=body.color)
            db.add(tag)
            await db.flush()

        # Link to competitor
        link = CompetitorTagLink(competitor_id=competitor_id, tag_id=tag.id)
        db.add(link)
        await db.commit()
        return {"id": str(tag.id), "name": tag.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
