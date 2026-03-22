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
    """Collect all pre-built assets from dagster_components."""
    assets = []
    try:
        from agentic_assistants.orchestration.dagster_components import (
            knowledge_base_asset,
            repo_ingestion_asset,
        )
        assets.extend([repo_ingestion_asset, knowledge_base_asset])
    except ImportError:
        logger.warning("Could not import dagster_components assets")
    return assets


def _collect_jobs() -> List[Any]:
    """Collect all pre-built jobs."""
    jobs = []
    try:
        from agentic_assistants.orchestration.dagster_components import (
            maintenance_job,
            web_search_job,
        )
        jobs.extend([maintenance_job, web_search_job])
    except ImportError:
        logger.warning("Could not import dagster_components jobs")
    return jobs


def _collect_schedules(jobs: List[Any]) -> List[Any]:
    """Create default schedules for collected jobs."""
    if not DAGSTER_AVAILABLE:
        return []

    schedules = []

    # Find maintenance job and create a daily schedule
    for job in jobs:
        if getattr(job, "name", "") == "maintenance_job":
            schedules.append(
                dg.ScheduleDefinition(
                    job=job,
                    cron_schedule="0 2 * * *",  # Daily at 2 AM
                    name="daily_maintenance",
                    description="Run workspace maintenance daily at 2 AM",
                )
            )

    return schedules


def _collect_sensors() -> List[Any]:
    """Collect all sensors. Placeholder for user-defined sensors."""
    return []


def _get_resources() -> Dict[str, Any]:
    """
    Build Dagster resource definitions from framework configuration.

    Returns configured resources for database connections, storage, etc.
    """
    from agentic_assistants.orchestration.dagster_code.resources import (
        get_default_resources,
    )
    return get_default_resources()


def get_definitions() -> Any:
    """
    Build and return the complete Dagster Definitions object.

    This is the main entry point for the Dagster code location.
    It assembles all assets, jobs, schedules, sensors, and resources.

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

    logger.info(
        f"Dagster Definitions: {len(assets)} assets, {len(jobs)} jobs, "
        f"{len(schedules)} schedules, {len(sensors)} sensors"
    )

    return dg.Definitions(
        assets=assets,
        jobs=jobs,
        schedules=schedules,
        sensors=sensors,
        resources=resources,
    )
