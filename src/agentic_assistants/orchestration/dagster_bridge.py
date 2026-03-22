"""
Bridge layer between existing pipelines and Dagster jobs/assets.

Converts pipeline nodes to Dagster ops and DAGs to jobs or software-defined assets.
Mirrors the Prefect bridge (prefect_bridge.py) for consistency.
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional

try:
    import dagster as dg
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False
    dg = None  # type: ignore

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


def node_to_op(
    node: Any,
    retries: int = 0,
    timeout: Optional[int] = None,
    tags: Optional[Dict[str, str]] = None,
) -> Any:
    """
    Wrap a single pipeline Node as a Dagster op.

    Args:
        node: Pipeline Node instance
        retries: Number of retries on failure
        timeout: Op timeout in seconds
        tags: Optional tags for the op

    Returns:
        Dagster op wrapping the node's function
    """
    if not DAGSTER_AVAILABLE:
        logger.warning("Dagster not available, returning unwrapped function")
        return node.func

    op_kwargs: Dict[str, Any] = {
        "name": node.name.replace(".", "_").replace("-", "_"),
        "description": f"Pipeline node: {node.name}",
    }
    if retries > 0:
        op_kwargs["retry_policy"] = dg.RetryPolicy(max_retries=retries)
    if tags:
        op_kwargs["tags"] = tags

    @dg.op(**op_kwargs)
    @wraps(node.func)
    def wrapped_op(context: dg.OpExecutionContext, **kwargs):
        context.log.info(f"Executing pipeline node: {node.name}")
        inputs = {}
        for input_name in node.input_names:
            if input_name in kwargs:
                inputs[input_name] = kwargs[input_name]
        result = node.func(**inputs) if inputs else node.func()
        return result

    return wrapped_op


def node_to_asset(
    node: Any,
    group_name: Optional[str] = None,
    key_prefix: Optional[List[str]] = None,
    deps: Optional[List[str]] = None,
) -> Any:
    """
    Wrap a single pipeline Node as a Dagster software-defined asset.

    Args:
        node: Pipeline Node instance
        group_name: Asset group for UI organization
        key_prefix: Asset key prefix
        deps: Upstream asset dependencies

    Returns:
        Dagster asset wrapping the node's function
    """
    if not DAGSTER_AVAILABLE:
        logger.warning("Dagster not available, returning unwrapped function")
        return node.func

    asset_name = node.name.replace(".", "_").replace("-", "_")
    asset_kwargs: Dict[str, Any] = {
        "name": asset_name,
        "description": f"Pipeline node: {node.name}",
    }
    if group_name:
        asset_kwargs["group_name"] = group_name
    if key_prefix:
        asset_kwargs["key_prefix"] = key_prefix
    if deps:
        asset_kwargs["deps"] = [dg.AssetKey(d) for d in deps]

    @dg.asset(**asset_kwargs)
    def wrapped_asset(context: dg.AssetExecutionContext):
        context.log.info(f"Materializing asset from node: {node.name}")
        return node.func()

    return wrapped_asset


def pipeline_to_job(
    pipeline: Any,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
) -> Any:
    """
    Convert a Pipeline DAG to a Dagster job.

    Nodes become ops and their dependency graph is preserved via
    topological sort.

    Args:
        pipeline: Pipeline instance
        name: Job name
        description: Job description
        tags: Tags for the job

    Returns:
        Dagster job definition
    """
    if not DAGSTER_AVAILABLE:
        logger.error("Dagster not available, cannot convert pipeline")
        raise ImportError("Dagster is required for job conversion")

    job_name = name or pipeline.name.replace(".", "_").replace("-", "_")

    # Convert all nodes to ops
    node_ops = {}
    for node_name, node in pipeline.nodes.items():
        op_name = node_name.replace(".", "_").replace("-", "_")
        node_ops[node_name] = node_to_op(node)

    @dg.job(
        name=job_name,
        description=description or f"Converted from pipeline: {pipeline.name}",
        tags=tags,
    )
    def pipeline_job():
        """Execute pipeline as a Dagster job."""
        execution_order = pipeline.get_execution_order()
        results = {}
        for node_name in execution_order:
            op_func = node_ops[node_name]
            node = pipeline.nodes[node_name]

            # Gather inputs from previous op results
            kwargs = {}
            for input_name in node.input_names:
                if input_name in results:
                    kwargs[input_name] = results[input_name]

            result = op_func(**kwargs) if kwargs else op_func()

            # Store outputs for downstream nodes
            if len(node.output_names) == 1:
                results[node.output_names[0]] = result
            elif isinstance(result, dict):
                for output_name in node.output_names:
                    if output_name in result:
                        results[output_name] = result[output_name]

    return pipeline_job


def pipeline_to_assets(
    pipeline: Any,
    group_name: Optional[str] = None,
    key_prefix: Optional[List[str]] = None,
) -> List[Any]:
    """
    Convert Pipeline nodes to Dagster software-defined assets.

    Each node becomes an asset with its inputs/outputs defining
    the asset dependency graph.

    Args:
        pipeline: Pipeline instance
        group_name: Asset group name for all assets
        key_prefix: Asset key prefix for all assets

    Returns:
        List of Dagster asset definitions
    """
    if not DAGSTER_AVAILABLE:
        logger.error("Dagster not available, cannot convert pipeline")
        raise ImportError("Dagster is required for asset conversion")

    assets = []
    group = group_name or pipeline.name.replace(".", "_").replace("-", "_")

    # Build reverse mapping: output_name -> node_name
    output_to_node: Dict[str, str] = {}
    for node_name, node in pipeline.nodes.items():
        for output_name in node.output_names:
            output_to_node[output_name] = node_name

    for node_name, node in pipeline.nodes.items():
        # Determine upstream dependencies
        upstream_deps = []
        for input_name in node.input_names:
            if input_name in output_to_node:
                dep_node = output_to_node[input_name]
                upstream_deps.append(dep_node.replace(".", "_").replace("-", "_"))

        asset = node_to_asset(
            node,
            group_name=group,
            key_prefix=key_prefix,
            deps=upstream_deps if upstream_deps else None,
        )
        assets.append(asset)

    logger.info(
        f"Converted pipeline '{pipeline.name}' to {len(assets)} Dagster assets"
    )
    return assets


def create_schedule_from_trigger(
    trigger: Any,
    job: Any,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Any:
    """
    Convert an existing IntervalTrigger or CronTrigger to a Dagster schedule.

    Args:
        trigger: IntervalTrigger or CronTrigger instance
        job: The Dagster job to schedule
        name: Schedule name
        description: Schedule description

    Returns:
        Dagster ScheduleDefinition
    """
    if not DAGSTER_AVAILABLE:
        logger.error("Dagster not available")
        return None

    from agentic_assistants.scheduling.triggers import (
        CronTrigger,
        IntervalTrigger,
    )

    cron_expression = None

    if isinstance(trigger, CronTrigger):
        # Build cron expression from CronTrigger fields
        parts = [
            str(trigger.minute or "*"),
            str(trigger.hour or "*"),
            str(trigger.day or "*"),
            str(trigger.month or "*"),
            str(trigger.day_of_week or "*"),
        ]
        cron_expression = " ".join(parts)

    elif isinstance(trigger, IntervalTrigger):
        # Convert interval to approximate cron expression
        total_seconds = (
            trigger.weeks * 7 * 24 * 3600
            + trigger.days * 24 * 3600
            + trigger.hours * 3600
            + trigger.minutes * 60
            + trigger.seconds
        )

        if total_seconds <= 60:
            cron_expression = "* * * * *"  # Every minute
        elif total_seconds <= 3600:
            minutes = max(1, total_seconds // 60)
            cron_expression = f"*/{minutes} * * * *"
        elif total_seconds <= 86400:
            hours = max(1, total_seconds // 3600)
            cron_expression = f"0 */{hours} * * *"
        elif total_seconds <= 604800:
            days = max(1, total_seconds // 86400)
            cron_expression = f"0 0 */{days} * *"
        else:
            cron_expression = "0 0 * * 0"  # Weekly fallback

    else:
        logger.warning(f"Unsupported trigger type: {type(trigger)}")
        return None

    schedule_name = name or f"schedule_{cron_expression.replace(' ', '_').replace('/', '_')}"

    schedule = dg.ScheduleDefinition(
        job=job,
        cron_schedule=cron_expression,
        name=schedule_name,
        description=description or f"Converted from {type(trigger).__name__}",
    )

    logger.info(f"Created Dagster schedule '{schedule_name}': {cron_expression}")
    return schedule


def create_sensor_for_pipeline(
    pipeline: Any,
    job: Any,
    name: Optional[str] = None,
    check_fn: Optional[Callable] = None,
    minimum_interval_seconds: int = 60,
) -> Any:
    """
    Create a Dagster sensor that monitors for pipeline trigger conditions.

    Args:
        pipeline: Pipeline instance to monitor
        job: Dagster job to trigger
        name: Sensor name
        check_fn: Function that returns True when the job should run
        minimum_interval_seconds: Minimum interval between evaluations

    Returns:
        Dagster SensorDefinition
    """
    if not DAGSTER_AVAILABLE:
        logger.error("Dagster not available")
        return None

    sensor_name = name or f"sensor_{pipeline.name.replace('.', '_').replace('-', '_')}"

    @dg.sensor(
        name=sensor_name,
        job=job,
        minimum_interval_seconds=minimum_interval_seconds,
        description=f"Sensor for pipeline: {pipeline.name}",
    )
    def pipeline_sensor(context: dg.SensorEvaluationContext):
        if check_fn and check_fn():
            yield dg.RunRequest(
                run_key=f"{pipeline.name}_{context.cursor or 'initial'}",
                run_config={},
            )
            context.update_cursor(str(int(context.cursor or "0") + 1))

    return pipeline_sensor


def migrate_apscheduler_job(
    job_func: Callable,
    schedule: str,
    name: Optional[str] = None,
) -> Any:
    """
    Migrate an APScheduler job to a Dagster schedule.

    Args:
        job_func: Job function to migrate
        schedule: Cron or interval schedule string
        name: Optional name for the resulting Dagster job

    Returns:
        Tuple of (Dagster job, Dagster schedule) or None if Dagster unavailable
    """
    if not DAGSTER_AVAILABLE:
        logger.error("Dagster not available for job migration")
        return None

    job_name = name or job_func.__name__

    @dg.op(name=f"{job_name}_op")
    def migrated_op(context: dg.OpExecutionContext):
        context.log.info(f"Running migrated APScheduler job: {job_name}")
        return job_func()

    @dg.job(name=job_name)
    def migrated_job():
        migrated_op()

    migrated_schedule = dg.ScheduleDefinition(
        job=migrated_job,
        cron_schedule=schedule,
        name=f"{job_name}_schedule",
        description=f"Migrated from APScheduler: {job_func.__name__}",
    )

    logger.info(f"Migrated job '{job_func.__name__}' to Dagster job+schedule")
    return migrated_job, migrated_schedule
