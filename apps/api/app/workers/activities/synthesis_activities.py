import uuid
import statistics
from datetime import datetime, timezone
from decimal import Decimal

from temporalio import activity
from sqlalchemy import select, func, desc

from app.database import async_session
from app.models.competitors import Competitor
from app.models.analytics import (
    KpiSnapshot, ShareOfVoice, Alert, AlertType, Severity, Report, AlertRule,
)
from app.models.data_collection import (
    AdCreative, SocialPost, WebsiteChange, MessageTheme, ChangeType,
)
from app.models.kpi_config import FilterMode
from app.utils.llm import call_openrouter


# ─────────────────────────────────────────
# AGENT 1: Benchmark & SOV (100% deterministic)
# ─────────────────────────────────────────

@activity.defn
async def run_benchmark_and_sov(
    brand_profile_id: str,
    filter_mode: str,
    period_start: str,
    period_end: str,
) -> dict:
    activity.logger.info(f"Benchmark & SOV for brand {brand_profile_id}")
    bp_uuid = uuid.UUID(brand_profile_id)
    p_start = datetime.fromisoformat(period_start)
    p_end = datetime.fromisoformat(period_end)

    async with async_session() as db:
        # Get all competitors
        stmt = select(Competitor).where(
            Competitor.brand_profile_id == bp_uuid, Competitor.active == True
        )
        result = await db.execute(stmt)
        competitors = list(result.scalars().all())

        if not competitors:
            return {"status": "no_competitors"}

        # Get all KPI snapshots for this period
        stmt = select(KpiSnapshot).where(
            KpiSnapshot.brand_profile_id == bp_uuid,
            KpiSnapshot.period_start >= p_start,
            KpiSnapshot.period_end <= p_end,
        )
        result = await db.execute(stmt)
        all_snapshots = list(result.scalars().all())

        # Group by kpi_key
        kpi_groups: dict[str, list[KpiSnapshot]] = {}
        for s in all_snapshots:
            kpi_groups.setdefault(s.kpi_key, []).append(s)

        # For each KPI, compute benchmarks
        for key, snaps in kpi_groups.items():
            values = [float(s.kpi_value) for s in snaps if s.kpi_value is not None]
            if not values:
                continue
            avg = statistics.mean(values)
            stdev = statistics.stdev(values) if len(values) > 1 else 0

            # Benchmark snapshot (competitor_id=NULL)
            benchmark = KpiSnapshot(
                brand_profile_id=bp_uuid,
                competitor_id=None,
                filter_mode=filter_mode,
                period_start=p_start,
                period_end=p_end,
                kpi_key=f"{key}_benchmark",
                kpi_value=Decimal(str(round(avg, 4))),
                kpi_label=f"Category avg: {key}",
            )
            db.add(benchmark)

            # Flag anomalies (> 2 stdev)
            if stdev > 0:
                for s in snaps:
                    if s.kpi_value is not None and abs(float(s.kpi_value) - avg) > 2 * stdev:
                        # Recalculate delta vs benchmark
                        s.delta_pct = Decimal(str(round(((float(s.kpi_value) - avg) / max(avg, 0.001)) * 100, 2)))

        # Activity-Based Share of Voice
        sov_entries = []
        total_score = 0

        for comp in competitors:
            # Count ads
            stmt = select(func.count()).select_from(AdCreative).where(
                AdCreative.competitor_id == comp.id, AdCreative.active == True
            )
            ad_count = (await db.execute(stmt)).scalar() or 0

            # Count posts
            stmt = select(func.count()).select_from(SocialPost).where(
                SocialPost.competitor_id == comp.id,
                SocialPost.published_at >= p_start,
                SocialPost.published_at <= p_end,
            )
            post_count = (await db.execute(stmt)).scalar() or 0

            # Check for video
            stmt = select(func.count()).select_from(SocialPost).where(
                SocialPost.competitor_id == comp.id,
                SocialPost.post_type.in_(["video", "reel"]),
                SocialPost.published_at >= p_start,
            )
            has_video = ((await db.execute(stmt)).scalar() or 0) > 0

            # Avg engagement
            stmt = select(func.avg(SocialPost.engagement_rate)).where(
                SocialPost.competitor_id == comp.id,
                SocialPost.published_at >= p_start,
            )
            avg_eng = (await db.execute(stmt)).scalar() or 0

            activity_score = (ad_count * 3) + (post_count * 2) + (5 if has_video else 0) + (float(avg_eng) * 10)
            total_score += activity_score

            sov_entries.append({
                "competitor_id": str(comp.id),
                "brand_name": comp.name,
                "activity_score": round(activity_score, 2),
                "sov_pct": 0,  # Calculated below
            })

        # Calculate percentages
        if total_score > 0:
            for entry in sov_entries:
                entry["sov_pct"] = round((entry["activity_score"] / total_score) * 100, 1)

        sov = ShareOfVoice(
            brand_profile_id=bp_uuid,
            period_start=p_start,
            period_end=p_end,
            filter_mode=filter_mode,
            entries=sov_entries,
        )
        db.add(sov)
        await db.commit()

    return {"status": "ok", "competitors_benchmarked": len(competitors), "sov_entries": len(sov_entries)}


# ─────────────────────────────────────────
# AGENT 2: Alert Evaluation (rule-based + 1 LLM call)
# ─────────────────────────────────────────

@activity.defn
async def run_alert_evaluation(brand_profile_id: str, filter_mode: str) -> dict:
    activity.logger.info(f"Alert evaluation for brand {brand_profile_id}")
    bp_uuid = uuid.UUID(brand_profile_id)

    async with async_session() as db:
        triggered: list[dict] = []

        # Get competitors
        stmt = select(Competitor).where(
            Competitor.brand_profile_id == bp_uuid, Competitor.active == True
        )
        result = await db.execute(stmt)
        competitors = list(result.scalars().all())

        for comp in competitors:
            # Check posting spike
            stmt = (
                select(KpiSnapshot)
                .where(
                    KpiSnapshot.competitor_id == comp.id,
                    KpiSnapshot.kpi_key == "posting_frequency",
                )
                .order_by(desc(KpiSnapshot.computed_at))
                .limit(1)
            )
            result = await db.execute(stmt)
            snap = result.scalar_one_or_none()
            if snap and snap.delta_pct and float(snap.delta_pct) > 40:
                triggered.append({
                    "competitor_id": str(comp.id),
                    "competitor_name": comp.name,
                    "type": "posting_spike",
                    "severity": "medium",
                    "detail": f"Posting frequency increased by {float(snap.delta_pct):.0f}%",
                })

            # Check new campaigns (direct tier)
            if comp.tier.value == "direct":
                stmt = select(func.count()).select_from(AdCreative).where(
                    AdCreative.competitor_id == comp.id,
                    AdCreative.active == True,
                    AdCreative.first_seen >= func.now() - func.cast("7 days", func.literal_column("interval")),
                )
                # Simplified: just check for any active ads
                stmt2 = select(func.count()).select_from(AdCreative).where(
                    AdCreative.competitor_id == comp.id,
                    AdCreative.active == True,
                )
                new_ads = (await db.execute(stmt2)).scalar() or 0
                if new_ads > 0:
                    triggered.append({
                        "competitor_id": str(comp.id),
                        "competitor_name": comp.name,
                        "type": "new_campaign",
                        "severity": "medium",
                        "detail": f"{new_ads} active ad campaigns detected",
                    })

            # Check pricing changes
            stmt = (
                select(WebsiteChange)
                .where(
                    WebsiteChange.competitor_id == comp.id,
                    WebsiteChange.change_type == ChangeType.pricing,
                )
                .order_by(desc(WebsiteChange.detected_at))
                .limit(1)
            )
            result = await db.execute(stmt)
            pricing_change = result.scalar_one_or_none()
            if pricing_change:
                triggered.append({
                    "competitor_id": str(comp.id),
                    "competitor_name": comp.name,
                    "type": "pricing_change",
                    "severity": "high",
                    "detail": "Pricing page change detected",
                })

        # Check user-defined alert rules
        stmt = select(AlertRule).where(
            AlertRule.brand_profile_id == bp_uuid, AlertRule.active == True
        )
        result = await db.execute(stmt)
        rules = list(result.scalars().all())

        for rule in rules:
            target_comps = [c for c in competitors if rule.competitor_id is None or c.id == rule.competitor_id]
            for comp in target_comps:
                stmt = (
                    select(KpiSnapshot)
                    .where(
                        KpiSnapshot.competitor_id == comp.id,
                        KpiSnapshot.kpi_key == rule.kpi_key,
                    )
                    .order_by(desc(KpiSnapshot.computed_at))
                    .limit(1)
                )
                result = await db.execute(stmt)
                snap = result.scalar_one_or_none()
                if not snap or snap.delta_pct is None:
                    continue

                delta = float(snap.delta_pct)
                threshold = float(rule.threshold)
                condition_met = False

                if rule.condition.value == "increase_pct_gt" and delta > threshold:
                    condition_met = True
                elif rule.condition.value == "decrease_pct_gt" and delta < -threshold:
                    condition_met = True
                elif rule.condition.value == "threshold_gt" and float(snap.kpi_value) > threshold:
                    condition_met = True
                elif rule.condition.value == "threshold_lt" and float(snap.kpi_value) < threshold:
                    condition_met = True

                if condition_met:
                    triggered.append({
                        "competitor_id": str(comp.id),
                        "competitor_name": comp.name,
                        "type": "custom_rule",
                        "severity": "medium",
                        "detail": f"Custom alert: {rule.kpi_key} {rule.condition.value} {threshold}",
                    })

        if not triggered:
            return {"status": "no_alerts", "count": 0}

        # ONE LLM call for all alert descriptions
        descriptions: list[str] = []
        try:
            alert_summaries = "\n".join(
                f"{i+1}. {t['competitor_name']}: {t['type']} — {t['detail']}"
                for i, t in enumerate(triggered)
            )
            llm_result = await call_openrouter(
                system_prompt="Write brief, plain-English descriptions for competitive alerts. Each under 2 sentences. Be specific — mention competitor names and numbers. Respond as JSON: {\"descriptions\": [\"desc1\", \"desc2\"]}",
                user_prompt=f"Write descriptions for these {len(triggered)} alerts:\n{alert_summaries}",
                model="google/gemini-2.5-pro",
            )
            descriptions = llm_result.get("descriptions", [])
        except Exception as e:
            activity.logger.warning(f"Alert description LLM failed: {e}")
            descriptions = [t["detail"] for t in triggered]

        # Create Alert records
        for i, t in enumerate(triggered):
            try:
                alert_type = AlertType(t["type"])
            except ValueError:
                alert_type = AlertType.posting_spike
            try:
                severity = Severity(t["severity"])
            except ValueError:
                severity = Severity.medium

            alert = Alert(
                brand_profile_id=bp_uuid,
                competitor_id=uuid.UUID(t["competitor_id"]),
                alert_type=alert_type,
                severity=severity,
                title=f"{t['competitor_name']}: {t['type'].replace('_', ' ').title()}",
                description=descriptions[i] if i < len(descriptions) else t["detail"],
                evidence={"raw": t},
            )
            db.add(alert)

        await db.commit()

    return {"status": "ok", "alerts_created": len(triggered)}


# ─────────────────────────────────────────
# AGENT 3: Report Generation (1 LLM call)
# ─────────────────────────────────────────

@activity.defn
async def run_report_generation(
    brand_profile_id: str,
    filter_mode: str,
    period_start: str,
    period_end: str,
) -> dict:
    activity.logger.info(f"Report generation for brand {brand_profile_id}")
    bp_uuid = uuid.UUID(brand_profile_id)
    p_start = datetime.fromisoformat(period_start)
    p_end = datetime.fromisoformat(period_end)

    async with async_session() as db:
        # Gather all data
        # KPI snapshots
        stmt = select(KpiSnapshot).where(
            KpiSnapshot.brand_profile_id == bp_uuid,
            KpiSnapshot.period_start >= p_start,
        )
        result = await db.execute(stmt)
        snapshots = list(result.scalars().all())

        # Alerts
        stmt = select(Alert).where(
            Alert.brand_profile_id == bp_uuid,
        ).order_by(desc(Alert.triggered_at)).limit(20)
        result = await db.execute(stmt)
        alerts = list(result.scalars().all())

        # SOV
        stmt = (
            select(ShareOfVoice)
            .where(ShareOfVoice.brand_profile_id == bp_uuid)
            .order_by(desc(ShareOfVoice.period_start))
            .limit(1)
        )
        result = await db.execute(stmt)
        sov = result.scalar_one_or_none()

        # Messaging themes
        stmt = select(MessageTheme).join(
            Competitor, MessageTheme.competitor_id == Competitor.id
        ).where(
            Competitor.brand_profile_id == bp_uuid,
        ).order_by(desc(MessageTheme.frequency)).limit(20)
        result = await db.execute(stmt)
        themes = list(result.scalars().all())

        # Competitors
        stmt = select(Competitor).where(
            Competitor.brand_profile_id == bp_uuid, Competitor.active == True
        )
        result = await db.execute(stmt)
        competitors = list(result.scalars().all())

        # Build structured report data (deterministic)
        report_data: dict = {
            "period": {"start": period_start, "end": period_end, "filter_mode": filter_mode},
            "competitors_analyzed": [{"id": str(c.id), "name": c.name, "tier": c.tier.value} for c in competitors],
            "kpi_summary": {},
            "messaging_landscape": [{"theme": t.theme, "frequency": t.frequency, "source": t.source.value} for t in themes[:10]],
            "alerts": [{"type": a.alert_type.value, "severity": a.severity.value, "title": a.title, "description": a.description} for a in alerts[:10]],
            "share_of_voice": sov.entries if sov else [],
        }

        # Group KPIs by competitor
        for s in snapshots:
            comp_key = str(s.competitor_id) if s.competitor_id else "benchmark"
            if comp_key not in report_data["kpi_summary"]:
                report_data["kpi_summary"][comp_key] = {}
            report_data["kpi_summary"][comp_key][s.kpi_key] = {
                "value": float(s.kpi_value) if s.kpi_value else 0,
                "delta_pct": float(s.delta_pct) if s.delta_pct else None,
                "label": s.kpi_label,
            }

        # ONE LLM call for narrative
        sov_leaders = ", ".join(
            "{} ({}%)".format(e["brand_name"], e["sov_pct"])
            for e in (sov.entries[:3] if sov else [])
        )
        data_summary = (
            f"Period: {filter_mode} {period_start} to {period_end}\n"
            f"Competitors analyzed: {len(competitors)}\n"
            f"Alerts triggered: {len(alerts)}\n"
            f"Top themes: {', '.join(t.theme for t in themes[:5])}\n"
            f"SOV leaders: {sov_leaders}"
        )

        try:
            narrative = await call_openrouter(
                system_prompt="You are a competitive intelligence analyst writing for a marketing executive. Write in simple, professional language. Be specific — always name competitors and cite numbers. No jargon. Respond as JSON: {\"executive_summary\": \"3-4 sentences\", \"opportunities\": [{\"title\": \"...\", \"description\": \"...\"}], \"key_takeaways\": [\"takeaway1\", \"takeaway2\", \"takeaway3\"]}",
                user_prompt=f"Generate the narrative sections for this competitive intelligence report:\n\n{data_summary}\n\nAlert details:\n" + "\n".join(f"- {a.title}: {a.description}" for a in alerts[:5]),
                model="google/gemini-2.5-pro",
            )
        except Exception as e:
            activity.logger.warning(f"Report LLM failed: {e}")
            narrative = {
                "executive_summary": "Report generation in progress. Narrative will be updated when analysis completes.",
                "opportunities": [],
                "key_takeaways": [],
            }

        report_data["executive_summary"] = narrative.get("executive_summary", "")
        report_data["opportunities"] = narrative.get("opportunities", [])
        report_data["key_takeaways"] = narrative.get("key_takeaways", [])

        # Save Report
        report = Report(
            brand_profile_id=bp_uuid,
            filter_mode=filter_mode,
            period_start=p_start,
            period_end=p_end,
            executive_summary=narrative.get("executive_summary", ""),
            report_data=report_data,
        )
        db.add(report)
        await db.commit()

    return {"status": "ok", "report_id": str(report.id)}
