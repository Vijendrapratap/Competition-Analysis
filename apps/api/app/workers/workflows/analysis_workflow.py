import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.workers.activities.analysis_activities import (
        run_social_analysis,
        run_paid_media_analysis,
        run_website_change_analysis,
        run_messaging_analysis,
    )


RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=2),
    maximum_attempts=2,
)
ACTIVITY_TIMEOUT = timedelta(minutes=5)


@workflow.defn
class CompetitorAnalysisWorkflow:
    """Runs analysis agents for a single competitor after data collection."""

    @workflow.run
    async def run(
        self,
        brand_profile_id: str,
        competitor_id: str,
        filter_mode: str,
        period_start: str,
        period_end: str,
    ) -> dict:
        # Step 1: Run social, paid media, and website analysis in parallel
        social_task = workflow.execute_activity(
            run_social_analysis,
            args=[competitor_id, filter_mode, period_start, period_end],
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )
        paid_task = workflow.execute_activity(
            run_paid_media_analysis,
            args=[competitor_id, filter_mode, period_start, period_end],
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )
        website_task = workflow.execute_activity(
            run_website_change_analysis,
            args=[competitor_id],
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        social_result, paid_result, website_result = await asyncio.gather(
            social_task, paid_task, website_task
        )

        # Step 2: Messaging analysis depends on the above
        messaging_result = await workflow.execute_activity(
            run_messaging_analysis,
            args=[competitor_id, filter_mode, period_start, period_end],
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        return {
            "competitor_id": competitor_id,
            "social": social_result,
            "paid": paid_result,
            "website": website_result,
            "messaging": messaging_result,
        }
