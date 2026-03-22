"""
Orchestration layer for workflow management.

Provides unified interface for workflow orchestration with Prefect and Dagster integration.
"""

from agentic_assistants.orchestration.prefect_bridge import (
    pipeline_to_flow,
    task_wrapper,
)
from agentic_assistants.orchestration.dagster_bridge import (
    pipeline_to_job,
    pipeline_to_assets,
    node_to_op,
    node_to_asset,
    create_schedule_from_trigger,
    create_sensor_for_pipeline,
    migrate_apscheduler_job,
)

__all__ = [
    # Prefect
    "pipeline_to_flow",
    "task_wrapper",
    # Dagster
    "pipeline_to_job",
    "pipeline_to_assets",
    "node_to_op",
    "node_to_asset",
    "create_schedule_from_trigger",
    "create_sensor_for_pipeline",
    "migrate_apscheduler_job",
]
