from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.workers.activities.synthesis_activities import (
        run_benchmark_and_sov,
        run_alert_evaluation,
        run_report_generation,
    )

RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=2),
    maximum_attempts=2,
)
ACTIVITY_TIMEOUT = timedelta(minutes=5)


@workflow.defn
class SynthesisWorkflow:
    """Runs after all competitor analyses complete. Produces benchmarks, alerts, and reports."""

    @workflow.run
    async def run(
        self,
        brand_profile_id: str,
        filter_mode: str,
        period_start: str,
        period_end: str,
    ) -> dict:
        # Step 1: Benchmark & SOV (deterministic)
        benchmark_result = await workflow.execute_activity(
            run_benchmark_and_sov,
            args=[brand_profile_id, filter_mode, period_start, period_end],
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        # Step 2: Alert evaluation (rule-based + 1 LLM call)
        alert_result = await workflow.execute_activity(
            run_alert_evaluation,
            args=[brand_profile_id, filter_mode],
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        # Step 3: Report generation (1 LLM call)
        report_result = await workflow.execute_activity(
            run_report_generation,
            args=[brand_profile_id, filter_mode, period_start, period_end],
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        return {
            "benchmark": benchmark_result,
            "alerts": alert_result,
            "report": report_result,
        }
