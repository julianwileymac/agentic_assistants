"""
Dagster repository / definitions assembly.

Auto-discovers and registers all jobs, assets, schedules, and sensors
from the Agentic Assistants framework into a single ``Definitions`` object.
"""

from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

try:
    import dagster as dg
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False
    dg = None  # type: ignore


def _collect_assets() -> List[Any]:
    """Collect all pre-built assets from dagster_components and dagster_datasets."""
    assets = []

    try:
        from agentic_assistants.orchestration.dagster_components import (
            knowledge_base_asset,
            repo_ingestion_asset,
            crew_analysis_asset,
            document_ingestion_asset,
        )
        assets.extend([
            repo_ingestion_asset,
            knowledge_base_asset,
            crew_analysis_asset,
            document_ingestion_asset,
        ])
    except ImportError:
        logger.warning("Could not import dagster_components assets")

    try:
        from agentic_assistants.orchestration.dagster_datasets import (
            raw_dataset_asset,
            processed_dataset_asset,
            formatted_dataset_asset,
            dataset_stats_asset,
        )
        assets.extend([
            raw_dataset_asset,
            processed_dataset_asset,
            formatted_dataset_asset,
            dataset_stats_asset,
        ])
    except ImportError:
        logger.warning("Could not import dagster_datasets assets")

    return assets


def _collect_jobs() -> List[Any]:
    """Collect all pre-built jobs from dagster_components and dagster_datasets."""
    jobs = []
    try:
        from agentic_assistants.orchestration.dagster_components import (
            maintenance_job,
            web_search_job,
        )
        jobs.extend([maintenance_job, web_search_job])
    except ImportError:
        logger.warning("Could not import dagster_components jobs")

    try:
        from agentic_assistants.orchestration.dagster_datasets import (
            dataset_curation_job,
            dataset_refresh_job,
        )
        jobs.extend([dataset_curation_job, dataset_refresh_job])
    except ImportError:
        logger.warning("Could not import dagster_datasets jobs")

    return jobs


def _collect_schedules(jobs: List[Any]) -> List[Any]:
    """Create default schedules for collected jobs."""
    if not DAGSTER_AVAILABLE:
        return []

    schedules = []

    for job in jobs:
        if getattr(job, "name", "") == "maintenance_job":
            schedules.append(
                dg.ScheduleDefinition(
                    job=job,
                    cron_schedule="0 2 * * *",
                    name="daily_maintenance",
                    description="Run workspace maintenance daily at 2 AM",
                )
            )

    try:
        from agentic_assistants.orchestration.dagster_datasets import (
            daily_dataset_refresh,
        )
        schedules.append(daily_dataset_refresh)
    except ImportError:
        logger.warning("Could not import dagster_datasets schedules")

    return schedules


def _collect_sensors() -> List[Any]:
    """Collect all sensors. Placeholder for user-defined sensors."""
    return []


def _collect_hooks() -> List[Any]:
    """Collect Dagster hooks for observability."""
    hooks = []
    try:
        from agentic_assistants.orchestration.dagster_callbacks import (
            otel_success_hook,
            otel_failure_hook,
        )
        hooks.extend([otel_success_hook, otel_failure_hook])
    except ImportError:
        logger.warning("Could not import dagster_callbacks hooks")
    return hooks


def _get_resources() -> Dict[str, Any]:
    """
    Build Dagster resource definitions from framework configuration.

    Returns configured resources for database connections, storage, etc.
    """
    from agentic_assistants.orchestration.dagster_code.resources import (
        get_default_resources,
    )
    resources = get_default_resources()

    try:
        from agentic_assistants.orchestration.dagster_datasets import (
            DatasetCatalogResource,
        )
        resources["dataset_catalog"] = DatasetCatalogResource(
            project_id="agentic-assistants",
        )
    except ImportError:
        logger.warning("Could not import DatasetCatalogResource")

    return resources


def get_definitions() -> Any:
    """
    Build and return the complete Dagster Definitions object.

    This is the main entry point for the Dagster code location.
    It assembles all assets, jobs, schedules, sensors, resources,
    and observability hooks from the entire framework.

    Returns:
        Dagster Definitions object
    """
    if not DAGSTER_AVAILABLE:
        raise ImportError("Dagster is required. Install with: pip install dagster")

    assets = _collect_assets()
    jobs = _collect_jobs()
    schedules = _collect_schedules(jobs)
    sensors = _collect_sensors()
    resources = _get_resources()
    hooks = _collect_hooks()

    # Attach OTel hooks to all jobs for automatic observability
    if hooks:
        hooked_jobs = []
        for job in jobs:
            try:
                hooked_jobs.append(job.with_hooks(set(hooks)))
            except Exception:
                hooked_jobs.append(job)
        jobs = hooked_jobs

    logger.info(
        f"Dagster Definitions: {len(assets)} assets, {len(jobs)} jobs, "
        f"{len(schedules)} schedules, {len(sensors)} sensors, "
        f"{len(hooks)} hooks"
    )

    return dg.Definitions(
        assets=assets,
        jobs=jobs,
        schedules=schedules,
        sensors=sensors,
        resources=resources,
    )
