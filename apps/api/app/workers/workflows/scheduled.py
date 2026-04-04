"""Scheduled collection workflow — runs on cron based on filter mode."""

from datetime import datetime, timedelta, timezone

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.workers.activities.scheduled_activities import (
        get_brands_for_schedule,
        get_competitor_configs,
        send_failure_notification,
    )

RETRY_POLICY = RetryPolicy(initial_interval=timedelta(seconds=5), maximum_attempts=2)


@workflow.defn
class ScheduledCollectionWorkflow:
    """Cron-triggered workflow that runs collection + analysis + synthesis for all matching brands."""

    @workflow.run
    async def run(self, filter_mode: str) -> dict:
        # Get all active brand profiles with this filter mode
        brands = await workflow.execute_activity(
            get_brands_for_schedule,
            args=[filter_mode],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RETRY_POLICY,
        )

        if not brands:
            return {"status": "no_brands", "filter_mode": filter_mode}

        results = []

        for brand in brands:
            brand_id = brand["id"]
            try:
                # Get competitor configs
                competitor_configs = await workflow.execute_activity(
                    get_competitor_configs,
                    args=[brand_id],
                    start_to_close_timeout=timedelta(seconds=30),
                )

                if not competitor_configs:
                    results.append({"brand_id": brand_id, "status": "no_competitors"})
                    continue

                # Calculate period
                now = datetime.now(timezone.utc)
                if filter_mode == "daily":
                    period_start = (now - timedelta(days=1)).isoformat()
                elif filter_mode == "weekly":
                    period_start = (now - timedelta(weeks=1)).isoformat()
                else:
                    period_start = (now - timedelta(days=30)).isoformat()
                period_end = now.isoformat()

                # Step 1: Collection
                collection_result = await workflow.execute_child_workflow(
                    "FullCollectionWorkflow",
                    args=[brand_id, competitor_configs, "", "incremental"],
                    id=f"scheduled-collection-{brand_id}-{now.strftime('%Y%m%d%H%M')}",
                )

                # Step 2: Analysis for each competitor
                for comp in competitor_configs:
                    try:
                        await workflow.execute_child_workflow(
                            "CompetitorAnalysisWorkflow",
                            args=[brand_id, comp["id"], filter_mode, period_start, period_end],
                            id=f"scheduled-analysis-{comp['id']}-{now.strftime('%Y%m%d%H%M')}",
                        )
                    except Exception:
                        # Continue with other competitors if one fails
                        pass

                # Step 3: Synthesis
                await workflow.execute_child_workflow(
                    "SynthesisWorkflow",
                    args=[brand_id, filter_mode, period_start, period_end],
                    id=f"scheduled-synthesis-{brand_id}-{now.strftime('%Y%m%d%H%M')}",
                )

                results.append({"brand_id": brand_id, "status": "completed"})

            except Exception as e:
                results.append({"brand_id": brand_id, "status": "failed", "error": str(e)})
                # Send failure notification
                await workflow.execute_activity(
                    send_failure_notification,
                    args=[brand_id, str(e)],
                    start_to_close_timeout=timedelta(seconds=30),
                )

        return {"filter_mode": filter_mode, "brands_processed": len(results), "results": results}
