import uuid
from datetime import datetime, timezone
from decimal import Decimal

from temporalio import activity
from sqlalchemy import select, func, desc

from app.database import async_session
from app.models.data_collection import (
    SocialPost, AdCreative, PageSnapshot, MessageTheme,
    WebsiteChange, SourceType, QualityStatus, ThemeSource,
    ChangeType, Significance,
)
from app.models.analytics import KpiSnapshot
from app.models.kpi_config import FilterMode
from app.utils.llm import call_openrouter

import difflib


# ─────────────────────────────────────────
# AGENT 1: Social Analysis (100% deterministic)
# ─────────────────────────────────────────

@activity.defn
async def run_social_analysis(
    competitor_id: str,
    filter_mode: str,
    period_start: str,
    period_end: str,
) -> dict:
    activity.logger.info(f"Social analysis for {competitor_id}")
    comp_uuid = uuid.UUID(competitor_id)
    p_start = datetime.fromisoformat(period_start)
    p_end = datetime.fromisoformat(period_end)

    async with async_session() as db:
        # Query clean posts in period
        stmt = (
            select(SocialPost)
            .where(
                SocialPost.competitor_id == comp_uuid,
                SocialPost.published_at >= p_start,
                SocialPost.published_at <= p_end,
            )
            .order_by(desc(SocialPost.published_at))
        )
        result = await db.execute(stmt)
        posts = list(result.scalars().all())

        if not posts:
            return {"status": "no_data", "kpis_created": 0}

        # Compute KPIs
        posting_frequency = len(posts)
        eng_rates = [float(p.engagement_rate) for p in posts if p.engagement_rate]
        avg_engagement = sum(eng_rates) / len(eng_rates) if eng_rates else 0

        # Content format breakdown
        format_counts: dict[str, int] = {}
        for p in posts:
            fmt = p.post_type.value if p.post_type else "unknown"
            format_counts[fmt] = format_counts.get(fmt, 0) + 1
        top_format = max(format_counts, key=format_counts.get) if format_counts else None

        # Engagement spikes (posts > 3x average)
        spike_count = 0
        if avg_engagement > 0:
            for p in posts:
                if p.engagement_rate and float(p.engagement_rate) > avg_engagement * 3:
                    spike_count += 1

        # Look up brand_profile_id for this competitor
        from app.models.competitors import Competitor
        stmt = select(Competitor.brand_profile_id).where(Competitor.id == comp_uuid)
        result = await db.execute(stmt)
        brand_profile_id = result.scalar_one()

        # Upsert KPI snapshots
        kpis = [
            ("posting_frequency", posting_frequency, "Posts this period"),
            ("engagement_rate", avg_engagement, "Avg engagement rate"),
            ("top_content_format", hash(top_format or "") % 100, top_format or "N/A"),
            ("engagement_spike_count", spike_count, "Posts with 3x avg engagement"),
        ]

        for key, value, label in kpis:
            # Get previous period value for delta
            stmt = (
                select(KpiSnapshot.kpi_value)
                .where(
                    KpiSnapshot.competitor_id == comp_uuid,
                    KpiSnapshot.kpi_key == key,
                    KpiSnapshot.period_end < p_start,
                )
                .order_by(desc(KpiSnapshot.period_end))
                .limit(1)
            )
            result = await db.execute(stmt)
            prev_value = result.scalar_one_or_none()
            delta_pct = None
            if prev_value and float(prev_value) > 0:
                delta_pct = ((value - float(prev_value)) / float(prev_value)) * 100

            snapshot = KpiSnapshot(
                brand_profile_id=brand_profile_id,
                competitor_id=comp_uuid,
                filter_mode=filter_mode,
                period_start=p_start,
                period_end=p_end,
                kpi_key=key,
                kpi_value=Decimal(str(round(value, 6))),
                kpi_label=label,
                delta_pct=Decimal(str(round(delta_pct, 2))) if delta_pct is not None else None,
            )
            db.add(snapshot)

        await db.commit()

    return {"status": "ok", "kpis_created": len(kpis), "posts_analyzed": len(posts)}


# ─────────────────────────────────────────
# AGENT 2: Paid Media Analysis (1 LLM call)
# ─────────────────────────────────────────

@activity.defn
async def run_paid_media_analysis(
    competitor_id: str,
    filter_mode: str,
    period_start: str,
    period_end: str,
) -> dict:
    activity.logger.info(f"Paid media analysis for {competitor_id}")
    comp_uuid = uuid.UUID(competitor_id)
    p_start = datetime.fromisoformat(period_start)
    p_end = datetime.fromisoformat(period_end)

    async with async_session() as db:
        # Active ads
        stmt = select(AdCreative).where(
            AdCreative.competitor_id == comp_uuid,
            AdCreative.active == True,
        )
        result = await db.execute(stmt)
        ads = list(result.scalars().all())

        if not ads:
            return {"status": "no_ads", "themes": 0}

        # Deterministic metrics
        active_count = len(ads)
        new_count = sum(1 for a in ads if a.first_seen and a.first_seen >= p_start)
        format_counts: dict[str, int] = {}
        for a in ads:
            fmt = a.media_type.value if a.media_type else "unknown"
            format_counts[fmt] = format_counts.get(fmt, 0) + 1

        # LLM: Extract campaign themes (ONE call for all ads)
        ad_texts = []
        for a in ads[:30]:
            parts = []
            if a.headline:
                parts.append(f"Headline: {a.headline}")
            if a.body_text:
                parts.append(f"Body: {a.body_text[:200]}")
            if a.cta:
                parts.append(f"CTA: {a.cta}")
            if parts:
                ad_texts.append("\n".join(parts))

        themes_data = {"themes": [], "primary_hook": None, "cta_patterns": []}
        if ad_texts:
            try:
                themes_data = await call_openrouter(
                    system_prompt="You are a marketing analyst. Analyze these ad creatives and extract campaign themes. Respond as JSON: {\"themes\": [{\"theme\": \"...\", \"frequency\": N, \"evidence\": [\"headline1\"]}], \"primary_hook\": \"...\", \"cta_patterns\": [{\"cta\": \"...\", \"frequency\": N}]}",
                    user_prompt=f"Analyze these {len(ad_texts)} ad creatives:\n\n" + "\n---\n".join(ad_texts),
                    model="google/gemini-2.5-pro",
                )
            except Exception as e:
                activity.logger.warning(f"Paid media LLM failed: {e}")

        # Save themes
        from app.models.competitors import Competitor
        stmt = select(Competitor.brand_profile_id).where(Competitor.id == comp_uuid)
        result = await db.execute(stmt)
        brand_profile_id = result.scalar_one()

        for t in themes_data.get("themes", []):
            theme = MessageTheme(
                competitor_id=comp_uuid,
                source=ThemeSource.ads,
                theme=t.get("theme", "Unknown"),
                evidence=t.get("evidence", []),
                frequency=t.get("frequency", 1),
                period_start=p_start,
                period_end=p_end,
            )
            db.add(theme)

        # KPI snapshots
        for key, value, label in [
            ("active_ads_count", active_count, "Active ad campaigns"),
            ("new_ad_creatives", new_count, "New ads this period"),
        ]:
            snapshot = KpiSnapshot(
                brand_profile_id=brand_profile_id,
                competitor_id=comp_uuid,
                filter_mode=filter_mode,
                period_start=p_start,
                period_end=p_end,
                kpi_key=key,
                kpi_value=Decimal(str(value)),
                kpi_label=label,
            )
            db.add(snapshot)

        await db.commit()

    return {"status": "ok", "ads_analyzed": len(ads), "themes": len(themes_data.get("themes", []))}


# ─────────────────────────────────────────
# AGENT 3: Website Change Analysis (conditional LLM)
# ─────────────────────────────────────────

@activity.defn
async def run_website_change_analysis(competitor_id: str) -> dict:
    activity.logger.info(f"Website change analysis for {competitor_id}")
    comp_uuid = uuid.UUID(competitor_id)

    async with async_session() as db:
        # Get latest two website snapshots
        stmt = (
            select(PageSnapshot)
            .where(
                PageSnapshot.competitor_id == comp_uuid,
                PageSnapshot.source_type == SourceType.website,
                PageSnapshot.quality_status == QualityStatus.clean,
            )
            .order_by(desc(PageSnapshot.scraped_at))
            .limit(2)
        )
        result = await db.execute(stmt)
        snapshots = list(result.scalars().all())

        if len(snapshots) < 2:
            return {"status": "insufficient_data", "changes": 0}

        current = snapshots[0]
        previous = snapshots[1]

        current_text = current.extracted_text or current.raw_content or ""
        previous_text = previous.extracted_text or previous.raw_content or ""

        if not current_text or not previous_text:
            return {"status": "no_text", "changes": 0}

        # Compute diff
        diff = list(difflib.unified_diff(
            previous_text.splitlines(),
            current_text.splitlines(),
            lineterm="",
            n=0,
        ))

        if not diff:
            return {"status": "no_changes", "changes": 0}

        # Calculate change magnitude
        change_ratio = len(diff) / max(len(previous_text.splitlines()), 1)

        changes_created = 0

        # For significant diffs, use LLM to classify
        if change_ratio > 0.05:
            diff_text = "\n".join(diff[:100])  # Cap at 100 lines
            try:
                classifications = await call_openrouter(
                    system_prompt="Classify website changes. For each change, provide type and significance. Respond as JSON: {\"changes\": [{\"type\": \"headline|pricing|new_page|nav_change|offer\", \"significance\": \"high|medium|low\", \"before\": \"...\", \"after\": \"...\", \"summary\": \"...\"}]}",
                    user_prompt=f"Website diff:\n{diff_text}",
                    model="google/gemini-2.0-flash",
                )

                for c in classifications.get("changes", []):
                    change_type_str = c.get("type", "headline")
                    sig_str = c.get("significance", "medium")
                    try:
                        ct = ChangeType(change_type_str)
                    except ValueError:
                        ct = ChangeType.headline
                    try:
                        sig = Significance(sig_str)
                    except ValueError:
                        sig = Significance.medium

                    change = WebsiteChange(
                        competitor_id=comp_uuid,
                        change_type=ct,
                        before_value=c.get("before", "")[:1000],
                        after_value=c.get("after", "")[:1000],
                        significance=sig,
                    )
                    db.add(change)
                    changes_created += 1

            except Exception as e:
                activity.logger.warning(f"Website change LLM failed: {e}")
                # Fallback: create a generic change record
                change = WebsiteChange(
                    competitor_id=comp_uuid,
                    change_type=ChangeType.headline,
                    before_value=previous_text[:500],
                    after_value=current_text[:500],
                    significance=Significance.medium if change_ratio > 0.1 else Significance.low,
                )
                db.add(change)
                changes_created = 1
        else:
            # Minor change, no LLM needed
            change = WebsiteChange(
                competitor_id=comp_uuid,
                change_type=ChangeType.headline,
                before_value=None,
                after_value=None,
                significance=Significance.low,
            )
            db.add(change)
            changes_created = 1

        await db.commit()

    return {"status": "ok", "changes": changes_created, "change_ratio": round(change_ratio, 3)}


# ─────────────────────────────────────────
# AGENT 4: Messaging Analysis (1 LLM call)
# ─────────────────────────────────────────

@activity.defn
async def run_messaging_analysis(
    competitor_id: str,
    filter_mode: str,
    period_start: str,
    period_end: str,
) -> dict:
    activity.logger.info(f"Messaging analysis for {competitor_id}")
    comp_uuid = uuid.UUID(competitor_id)
    p_start = datetime.fromisoformat(period_start)
    p_end = datetime.fromisoformat(period_end)

    async with async_session() as db:
        # Collect text from all sources

        # Social captions (top 30 by engagement)
        stmt = (
            select(SocialPost.caption)
            .where(
                SocialPost.competitor_id == comp_uuid,
                SocialPost.caption != None,
                SocialPost.published_at >= p_start,
                SocialPost.published_at <= p_end,
            )
            .order_by(desc(SocialPost.likes))
            .limit(30)
        )
        result = await db.execute(stmt)
        social_captions = [row[0] for row in result.all() if row[0]]

        # Website copy
        stmt = (
            select(PageSnapshot.extracted_text)
            .where(
                PageSnapshot.competitor_id == comp_uuid,
                PageSnapshot.source_type == SourceType.website,
                PageSnapshot.quality_status == QualityStatus.clean,
            )
            .order_by(desc(PageSnapshot.scraped_at))
            .limit(1)
        )
        result = await db.execute(stmt)
        website_text = result.scalar_one_or_none() or ""

        # Ad text
        stmt = (
            select(AdCreative.headline, AdCreative.body_text)
            .where(
                AdCreative.competitor_id == comp_uuid,
                AdCreative.active == True,
            )
            .limit(30)
        )
        result = await db.execute(stmt)
        ad_texts = [
            f"Headline: {row[0] or ''} Body: {row[1] or ''}"
            for row in result.all()
            if row[0] or row[1]
        ]

        # Check if we have enough text
        total_text_count = len(social_captions) + (1 if website_text else 0) + len(ad_texts)
        if total_text_count == 0:
            return {"status": "no_text_data", "themes": 0}

        # Build batched prompt
        text_sections = []
        if social_captions:
            text_sections.append("[SOCIAL POSTS]\n" + "\n---\n".join(c[:300] for c in social_captions[:20]))
        if website_text:
            text_sections.append("[WEBSITE COPY]\n" + website_text[:2000])
        if ad_texts:
            text_sections.append("[AD CREATIVES]\n" + "\n---\n".join(ad_texts[:15]))

        # Get competitor name
        from app.models.competitors import Competitor
        stmt = select(Competitor.name, Competitor.brand_profile_id).where(Competitor.id == comp_uuid)
        result = await db.execute(stmt)
        row = result.one()
        comp_name = row[0]
        brand_profile_id = row[1]

        # ONE LLM call
        try:
            messaging = await call_openrouter(
                system_prompt=f'You are a competitive messaging analyst. Analyze all text content from competitor "{comp_name}" and extract messaging patterns. Respond as JSON: {{"messaging_themes": [{{"theme": "...", "frequency": N, "evidence": ["quote1"], "source": "social|website|ads"}}], "cta_patterns": [{{"pattern": "...", "percentage": N}}], "audience_language": {{"tone": "...", "emoji_usage": "...", "question_hooks": true/false, "language_style": "..."}}, "positioning_statement": "..."}}',
                user_prompt="\n\n".join(text_sections),
                model="google/gemini-2.5-pro",
            )
        except Exception as e:
            activity.logger.warning(f"Messaging LLM failed: {e}")
            return {"status": "llm_failed", "themes": 0}

        # Save themes
        themes_created = 0
        for t in messaging.get("messaging_themes", []):
            source_str = t.get("source", "social")
            try:
                source = ThemeSource(source_str.split("+")[0])
            except ValueError:
                source = ThemeSource.social

            theme = MessageTheme(
                competitor_id=comp_uuid,
                source=source,
                theme=t.get("theme", "Unknown"),
                evidence=t.get("evidence", []),
                frequency=t.get("frequency", 1),
                period_start=p_start,
                period_end=p_end,
            )
            db.add(theme)
            themes_created += 1

        await db.commit()

    return {"status": "ok", "themes": themes_created}
