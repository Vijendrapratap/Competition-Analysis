import asyncio
from datetime import timedelta
from uuid import UUID

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.workers.activities.collect_website import collect_website_data
    from app.workers.activities.collect_facebook import collect_facebook_data
    from app.workers.activities.collect_instagram import collect_instagram_data
    from app.workers.activities.collect_linkedin import collect_linkedin_data
    from app.workers.activities.collect_ad_library import collect_ad_library_data
    from app.workers.activities.collect_seo import collect_seo_data
    from app.workers.activities.collect_pricing import collect_pricing_data
    from app.workers.activities.collect_reviews import collect_review_data
    from app.workers.activities.data_hygiene import run_data_hygiene
    from app.workers.activities.job_status import update_job_status, mark_competitor_complete


RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=5.0,
    maximum_interval=timedelta(seconds=25),
    maximum_attempts=3,
)

ACTIVITY_TIMEOUT = timedelta(minutes=5)
WORKFLOW_TIMEOUT = timedelta(minutes=30)


@workflow.defn
class FullCollectionWorkflow:
    """Collects data for all competitors in a brand profile."""

    @workflow.run
    async def run(
        self,
        brand_profile_id: str,
        competitor_configs: list[dict],
        collection_job_id: str,
        collection_type: str = "full",
    ) -> dict:
        # Mark job as running
        await workflow.execute_activity(
            update_job_status,
            args=[collection_job_id, "running"],
            start_to_close_timeout=timedelta(seconds=30),
        )

        completed = 0
        failed = 0
        errors: list[dict] = []

        # Process competitors with max 5 concurrent
        semaphore_count = 5
        batches = [
            competitor_configs[i:i + semaphore_count]
            for i in range(0, len(competitor_configs), semaphore_count)
        ]

        for batch in batches:
            tasks = [
                self._collect_single_competitor(
                    brand_profile_id, comp, collection_job_id, collection_type
                )
                for comp in batch
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for comp, result in zip(batch, results):
                if isinstance(result, Exception):
                    failed += 1
                    errors.append({
                        "competitor_id": comp["id"],
                        "competitor_name": comp["name"],
                        "error": str(result),
                    })
                else:
                    completed += 1

                # Update progress
                await workflow.execute_activity(
                    mark_competitor_complete,
                    args=[collection_job_id, completed + failed],
                    start_to_close_timeout=timedelta(seconds=30),
                )

        # Mark job complete
        final_status = "completed" if failed == 0 else ("partial" if completed > 0 else "failed")
        await workflow.execute_activity(
            update_job_status,
            args=[collection_job_id, final_status, errors if errors else None],
            start_to_close_timeout=timedelta(seconds=30),
        )

        return {
            "completed": completed,
            "failed": failed,
            "errors": errors,
        }

    async def _collect_single_competitor(
        self,
        brand_profile_id: str,
        comp: dict,
        collection_job_id: str,
        collection_type: str,
    ) -> None:
        competitor_id = comp["id"]
        social = comp.get("social_profiles") or {}

        # Run collection activities in parallel
        collection_tasks = []

        if comp.get("website"):
            collection_tasks.append(
                workflow.execute_activity(
                    collect_website_data,
                    args=[competitor_id, comp["website"]],
                    start_to_close_timeout=ACTIVITY_TIMEOUT,
                    retry_policy=RETRY_POLICY,
                )
            )

        if social.get("facebook_url"):
            collection_tasks.append(
                workflow.execute_activity(
                    collect_facebook_data,
                    args=[competitor_id, social["facebook_url"]],
                    start_to_close_timeout=ACTIVITY_TIMEOUT,
                    retry_policy=RETRY_POLICY,
                )
            )

        if social.get("instagram_handle"):
            collection_tasks.append(
                workflow.execute_activity(
                    collect_instagram_data,
                    args=[competitor_id, social["instagram_handle"]],
                    start_to_close_timeout=ACTIVITY_TIMEOUT,
                    retry_policy=RETRY_POLICY,
                )
            )

        if comp.get("ad_library_url"):
            collection_tasks.append(
                workflow.execute_activity(
                    collect_ad_library_data,
                    args=[competitor_id, comp["ad_library_url"]],
                    start_to_close_timeout=ACTIVITY_TIMEOUT,
                    retry_policy=RETRY_POLICY,
                )
            )

        social = comp.get("social_profiles") or {}
        if social.get("linkedin_url"):
            collection_tasks.append(
                workflow.execute_activity(
                    collect_linkedin_data,
                    args=[competitor_id, social["linkedin_url"]],
                    start_to_close_timeout=ACTIVITY_TIMEOUT,
                    retry_policy=RETRY_POLICY,
                )
            )

        if collection_tasks:
            await asyncio.gather(*collection_tasks, return_exceptions=True)

        # Run data hygiene after social/ad collection
        await workflow.execute_activity(
            run_data_hygiene,
            args=[competitor_id, collection_job_id],
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        # SEO data collection (lower priority, longer timeout)
        if comp.get("website"):
            await workflow.execute_activity(
                collect_seo_data,
                args=[competitor_id, brand_profile_id, comp["website"], comp.get("seed_keywords", [])],
                start_to_close_timeout=timedelta(minutes=8),
                retry_policy=RETRY_POLICY,
            )

        # Pricing page collection
        if comp.get("website"):
            await workflow.execute_activity(
                collect_pricing_data,
                args=[competitor_id, brand_profile_id, comp["website"]],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RETRY_POLICY,
            )

        # Review collection (if slugs configured)
        if comp.get("g2_slug") or comp.get("capterra_slug"):
            await workflow.execute_activity(
                collect_review_data,
                args=[
                    competitor_id,
                    brand_profile_id,
                    comp.get("name", ""),
                    comp.get("g2_slug"),
                    comp.get("capterra_slug"),
                ],
                start_to_close_timeout=timedelta(minutes=8),
                retry_policy=RETRY_POLICY,
            )
