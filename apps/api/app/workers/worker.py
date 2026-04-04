"""Temporal worker entrypoint. Run with: python -m app.workers.worker"""

import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from app.config import get_settings
from app.workers.workflows.collection_workflow import FullCollectionWorkflow
from app.workers.workflows.analysis_workflow import CompetitorAnalysisWorkflow
from app.workers.workflows.synthesis_workflow import SynthesisWorkflow
from app.workers.workflows.scheduled import ScheduledCollectionWorkflow
from app.workers.activities.collect_website import collect_website_data
from app.workers.activities.collect_facebook import collect_facebook_data
from app.workers.activities.collect_instagram import collect_instagram_data
from app.workers.activities.collect_ad_library import collect_ad_library_data
from app.workers.activities.data_hygiene import run_data_hygiene
from app.workers.activities.job_status import update_job_status, mark_competitor_complete
from app.workers.activities.analysis_activities import (
    run_social_analysis,
    run_paid_media_analysis,
    run_website_change_analysis,
    run_messaging_analysis,
)
from app.workers.activities.synthesis_activities import (
    run_benchmark_and_sov,
    run_alert_evaluation,
    run_report_generation,
)
from app.workers.activities.scheduled_activities import (
    get_brands_for_schedule,
    get_competitor_configs,
    send_failure_notification,
)

TASK_QUEUE = "competeiq-main"


async def main():
    settings = get_settings()
    client = await Client.connect(settings.TEMPORAL_HOST)

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[
            FullCollectionWorkflow,
            CompetitorAnalysisWorkflow,
            SynthesisWorkflow,
            ScheduledCollectionWorkflow,
        ],
        activities=[
            # Collection
            collect_website_data,
            collect_facebook_data,
            collect_instagram_data,
            collect_ad_library_data,
            run_data_hygiene,
            # Job status
            update_job_status,
            mark_competitor_complete,
            # Analysis
            run_social_analysis,
            run_paid_media_analysis,
            run_website_change_analysis,
            run_messaging_analysis,
            # Synthesis
            run_benchmark_and_sov,
            run_alert_evaluation,
            run_report_generation,
            # Scheduled
            get_brands_for_schedule,
            get_competitor_configs,
            send_failure_notification,
        ],
    )

    print(f"Worker started on queue: {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
