"""
Pricing data collection activity.

Strategy:
1. Crawl the competitor's /pricing page specifically (Firecrawl).
2. Use LLM to extract structured pricing tiers, prices, billing cycles.
3. Diff against the previous PricingPage snapshot to detect changes.
4. Store PricingTier records and PricingChange events when diffs found.
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from temporalio import activity
from sqlalchemy import select, desc

from app.database import async_session
from app.models.pricing import PricingPage, PricingTier, PricingChange, PricingModel, BillingCycle
from app.models.analytics import Alert, Severity as AlertSeverity
from app.utils.firecrawl import crawl_url
from app.utils.llm import call_openrouter


@activity.defn
async def collect_pricing_data(
    competitor_id: str,
    brand_profile_id: str,
    website_url: str,
) -> dict:
    """Crawl pricing page, extract tiers with LLM, detect changes."""
    activity.logger.info(f"Collecting pricing data for {competitor_id}: {website_url}")
    comp_uuid = uuid.UUID(competitor_id)
    brand_uuid = uuid.UUID(brand_profile_id)

    # Try common pricing page URLs
    pricing_urls = [
        website_url.rstrip("/") + "/pricing",
        website_url.rstrip("/") + "/plans",
        website_url.rstrip("/") + "/pricing-plans",
    ]

    pages = []
    pricing_url_used = None
    for url in pricing_urls:
        pages = await crawl_url(url, max_pages=1)
        if pages:
            pricing_url_used = url
            break

    if not pages:
        activity.logger.info(f"No pricing page found for {website_url}")
        return {"status": "no_pricing_page", "tiers": 0}

    page = pages[0]
    raw_text = page.get("markdown") or page.get("text") or ""

    if len(raw_text) < 100:
        return {"status": "insufficient_content", "tiers": 0}

    # Extract pricing structure via LLM
    try:
        pricing_data = await call_openrouter(
            system_prompt=(
                "You are a pricing analyst. Extract all pricing tiers from this page. "
                "Respond ONLY as JSON: "
                "{\"pricing_model\": \"subscription|usage|freemium|one_time|custom\", "
                "\"tiers\": [{\"name\": \"...\", \"price\": 29.00, \"billing_cycle\": \"monthly|annual|one_time\", "
                "\"features\": [\"...\"], \"highlighted\": false}], "
                "\"has_free_tier\": false, \"has_enterprise\": false, "
                "\"currency\": \"USD\", \"pricing_notes\": \"any special notes\"}"
            ),
            user_prompt=f"Pricing page content:\n\n{raw_text[:4000]}",
            model="google/gemini-2.0-flash",
        )
    except Exception as e:
        activity.logger.warning(f"Pricing LLM failed: {e}")
        return {"status": "llm_failed", "tiers": 0}

    # Get previous pricing snapshot for diff
    async with async_session() as db:
        stmt = (
            select(PricingPage)
            .where(PricingPage.competitor_id == comp_uuid)
            .order_by(desc(PricingPage.scraped_at))
            .limit(1)
        )
        result = await db.execute(stmt)
        prev_pricing = result.scalar_one_or_none()

        # Create new PricingPage
        try:
            pm = PricingModel(pricing_data.get("pricing_model", "subscription"))
        except ValueError:
            pm = PricingModel.subscription

        new_page = PricingPage(
            competitor_id=comp_uuid,
            url=pricing_url_used,
            raw_content=raw_text[:50000],
            pricing_model=pm,
            has_free_tier=pricing_data.get("has_free_tier", False),
            has_enterprise=pricing_data.get("has_enterprise", False),
            currency=pricing_data.get("currency", "USD"),
            pricing_notes=pricing_data.get("pricing_notes"),
            scraped_at=datetime.now(timezone.utc),
        )
        db.add(new_page)
        await db.flush()

        # Create PricingTier records
        tiers_created = 0
        new_tiers = pricing_data.get("tiers", [])

        for tier_data in new_tiers:
            try:
                bc = BillingCycle(tier_data.get("billing_cycle", "monthly"))
            except ValueError:
                bc = BillingCycle.monthly

            price_val = tier_data.get("price")
            price = Decimal(str(price_val)) if price_val is not None else None

            tier = PricingTier(
                pricing_page_id=new_page.id,
                competitor_id=comp_uuid,
                tier_name=tier_data.get("name", "Unknown"),
                price=price,
                billing_cycle=bc,
                features=tier_data.get("features", []),
                is_highlighted=tier_data.get("highlighted", False),
            )
            db.add(tier)
            tiers_created += 1

        # Detect changes vs previous snapshot
        changes_detected = 0
        if prev_pricing and new_tiers:
            prev_tiers = {t.tier_name: t for t in prev_pricing.tiers} if hasattr(prev_pricing, "tiers") else {}

            for tier_data in new_tiers:
                tier_name = tier_data.get("name", "")
                price_val = tier_data.get("price")
                if price_val is None:
                    continue

                new_price = Decimal(str(price_val))

                if tier_name in prev_tiers:
                    old_price = prev_tiers[tier_name].price
                    if old_price and old_price != new_price:
                        change = PricingChange(
                            competitor_id=comp_uuid,
                            tier_name=tier_name,
                            old_price=old_price,
                            new_price=new_price,
                            change_type="price_change",
                            detected_at=datetime.now(timezone.utc),
                        )
                        db.add(change)
                        changes_detected += 1

                        # Fire a high-severity alert for pricing changes
                        alert = Alert(
                            brand_profile_id=brand_uuid,
                            competitor_id=comp_uuid,
                            alert_type="pricing_change",
                            title=f"Pricing Change Detected",
                            message=(
                                f"'{tier_name}' plan changed from "
                                f"${old_price}/mo to ${new_price}/mo"
                            ),
                            severity=AlertSeverity.high,
                            metadata={
                                "tier_name": tier_name,
                                "old_price": str(old_price),
                                "new_price": str(new_price),
                            },
                        )
                        db.add(alert)

        await db.commit()

    return {
        "status": "ok",
        "tiers": tiers_created,
        "changes_detected": changes_detected,
        "pricing_url": pricing_url_used,
    }
