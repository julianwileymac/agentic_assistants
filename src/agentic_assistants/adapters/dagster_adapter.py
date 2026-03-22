"""
Dagster framework adapter with integrated observability.

This adapter wraps Dagster jobs, ops, and assets to provide:
- MLFlow experiment tracking for job runs
- OpenTelemetry tracing for op execution
- Standardized metrics and logging
- Integration with Agentic Assistants pipelines

Example:
    >>> from agentic_assistants.adapters import DagsterAdapter
    >>>
    >>> adapter = DagsterAdapter()
    >>>
    >>> # Define an asset using the adapter
    >>> @adapter.asset(name="cleaned_data")
    >>> def cleaned_data(raw_data):
    ...     return raw_data.dropna()
    >>>
    >>> # Define a job using the adapter
    >>> @adapter.job(name="etl_pipeline")
    >>> def etl_pipeline():
    ...     extract() >> transform() >> load()
    >>>
    >>> # Run with tracking
    >>> result = adapter.run_job(etl_pipeline, run_config={})
"""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar

from agentic_assistants.adapters.base import BaseAdapter
from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")
JobFunc = TypeVar("JobFunc", bound=Callable[..., Any])
OpFunc = TypeVar("OpFunc", bound=Callable[..., Any])
AssetFunc = TypeVar("AssetFunc", bound=Callable[..., Any])

try:
    import dagster as dg
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False
    dg = None  # type: ignore


class DagsterAdapter(BaseAdapter):
    """
    Adapter for Dagster workflow orchestration framework.

    This adapter provides observability wrappers for Dagster jobs, ops,
    assets, schedules, and sensors, tracking execution, state transitions,
    and performance metrics.

    Attributes:
        config: Agentic configuration instance
        dagster_available: Whether Dagster is installed
    """

    framework_name = "dagster"

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        **kwargs,
    ):
        """
        Initialize the Dagster adapter.

        Args:
            config: Configuration instance
            **kwargs: Additional arguments passed to BaseAdapter
        """
        super().__init__(config, name="Dagster", **kwargs)
        self._dagster_available = DAGSTER_AVAILABLE
        self._registered_jobs: Dict[str, Any] = {}
        self._registered_ops: Dict[str, Any] = {}
        self._registered_assets: Dict[str, Any] = {}
        self._registered_schedules: Dict[str, Any] = {}
        self._registered_sensors: Dict[str, Any] = {}

    @property
    def dagster_available(self) -> bool:
        """Whether Dagster is installed."""
        return self._dagster_available

    def run(self, job: Any, run_config: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        Run a Dagster job with tracking.

        This is a convenience method that calls run_job.

        Args:
            job: The Dagster job to run
            run_config: Run configuration for the job
            **kwargs: Additional arguments passed to run_job

        Returns:
            Job execution result
        """
        return self.run_job(job, run_config, **kwargs)

    def run_job(
        self,
        job: Any,
        run_config: Optional[Dict[str, Any]] = None,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Run a Dagster job with full observability.

        Args:
            job: The Dagster job to run
            run_config: Run configuration for the job
            experiment_name: MLFlow experiment name (optional)
            run_name: Name for this run
            tags: Additional tags for the run

        Returns:
            The job execution result

        Example:
            >>> result = adapter.run_job(my_job, run_config={"ops": {"extract": {"config": {}}}})
        """
        if not self._dagster_available:
            raise RuntimeError("Dagster is not installed. Install with: pip install dagster")

        # Set experiment if specified
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        # Build run name
        actual_run_name = run_name or f"dagster-{time.strftime('%Y%m%d-%H%M%S')}"

        # Get job name if available
        job_name = getattr(job, "name", getattr(job, "__name__", "unknown"))

        # Build parameters
        params = {
            "framework": "dagster",
            "job_name": job_name,
            "has_run_config": run_config is not None,
        }

        # Build tags
        all_tags = {"framework": "dagster", "job_name": job_name}
        if tags:
            all_tags.update(tags)

        with self.track_run(actual_run_name, tags=all_tags, params=params):
            start_time = time.time()

            try:
                logger.info(f"Starting Dagster job: {job_name}")

                # Execute the job in-process
                result = job.execute_in_process(run_config=run_config or {})

                duration = time.time() - start_time

                # Log success metrics
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1 if result.success else 0)

                if result.success:
                    logger.info(f"Job {job_name} completed in {duration:.2f}s")
                else:
                    logger.warning(f"Job {job_name} finished with errors in {duration:.2f}s")

                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                logger.error(f"Job {job_name} failed after {duration:.2f}s: {e}")
                raise

    def materialize_assets(
        self,
        assets: List[Any],
        run_config: Optional[Dict[str, Any]] = None,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Materialize Dagster assets with full observability.

        Args:
            assets: List of Dagster assets to materialize
            run_config: Run configuration
            experiment_name: MLFlow experiment name (optional)
            run_name: Name for this run
            tags: Additional tags for the run

        Returns:
            Materialization result
        """
        if not self._dagster_available:
            raise RuntimeError("Dagster is not installed")

        if experiment_name:
            self.tracker.experiment_name = experiment_name

        actual_run_name = run_name or f"dagster-materialize-{time.strftime('%Y%m%d-%H%M%S')}"
        asset_names = [getattr(a, "key", str(a)) for a in assets]

        params = {
            "framework": "dagster",
            "operation": "materialize",
            "asset_count": len(assets),
            "asset_names": str(asset_names[:5]),  # Truncate for logging
        }

        all_tags = {"framework": "dagster", "operation": "materialize"}
        if tags:
            all_tags.update(tags)

        with self.track_run(actual_run_name, tags=all_tags, params=params):
            start_time = time.time()

            try:
                logger.info(f"Materializing {len(assets)} Dagster assets")

                result = dg.materialize(assets, run_config=run_config or {})

                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1 if result.success else 0)
                self.tracker.log_metric("assets_materialized", len(assets))

                logger.info(f"Materialization completed in {duration:.2f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                logger.error(f"Materialization failed after {duration:.2f}s: {e}")
                raise

    def job(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        **dagster_kwargs,
    ) -> Callable[[JobFunc], JobFunc]:
        """
        Decorator to create an observable Dagster job.

        Args:
            name: Job name
            description: Job description
            tags: Tags for the job
            **dagster_kwargs: Additional Dagster job kwargs

        Returns:
            Decorated job function

        Example:
            >>> @adapter.job(name="data_pipeline")
            >>> def pipeline():
            ...     extract() >> transform() >> load()
        """
        def decorator(func: JobFunc) -> JobFunc:
            job_name = name or func.__name__

            if self._dagster_available:
                # Create Dagster job
                dagster_job = dg.job(
                    name=job_name,
                    description=description,
                    tags=tags,
                    **dagster_kwargs,
                )(func)

                # Wrap with observability for in-process execution
                @wraps(func)
                def wrapped(*args, **kwargs):
                    with self.track_run(job_name, tags={"type": "job"}):
                        start_time = time.time()
                        try:
                            result = dagster_job.execute_in_process()
                            self.tracker.log_metric(
                                "duration_seconds", time.time() - start_time
                            )
                            self.tracker.log_metric(
                                "success", 1 if result.success else 0
                            )
                            return result
                        except Exception as e:
                            self.tracker.log_metric(
                                "duration_seconds", time.time() - start_time
                            )
                            self.tracker.log_metric("success", 0)
                            raise

                # Store both the dagster job and the tracked wrapper
                wrapped._dagster_job = dagster_job  # type: ignore
                self._registered_jobs[job_name] = dagster_job
                return wrapped  # type: ignore
            else:
                self._registered_jobs[job_name] = func
                return func

        return decorator

    def op(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        retry_policy: Optional[Any] = None,
        tags: Optional[Dict[str, str]] = None,
        **dagster_kwargs,
    ) -> Callable[[OpFunc], OpFunc]:
        """
        Decorator to create an observable Dagster op.

        Args:
            name: Op name
            description: Op description
            retry_policy: Dagster RetryPolicy instance
            tags: Tags for the op
            **dagster_kwargs: Additional Dagster op kwargs

        Returns:
            Decorated op function

        Example:
            >>> @adapter.op(name="extract_data")
            >>> def extract(context):
            ...     return fetch_data()
        """
        def decorator(func: OpFunc) -> OpFunc:
            op_name = name or func.__name__

            if self._dagster_available:
                # Build retry policy if not provided
                op_kwargs: Dict[str, Any] = {
                    "name": op_name,
                    "description": description,
                    "tags": tags,
                    **dagster_kwargs,
                }
                if retry_policy is not None:
                    op_kwargs["retry_policy"] = retry_policy

                # Filter None values
                op_kwargs = {k: v for k, v in op_kwargs.items() if v is not None}

                dagster_op = dg.op(**op_kwargs)(func)

                self._registered_ops[op_name] = dagster_op
                return dagster_op  # type: ignore
            else:
                self._registered_ops[op_name] = func
                return func

        return decorator

    def asset(
        self,
        name: Optional[str] = None,
        key_prefix: Optional[List[str]] = None,
        description: Optional[str] = None,
        group_name: Optional[str] = None,
        deps: Optional[List[Any]] = None,
        **dagster_kwargs,
    ) -> Callable[[AssetFunc], AssetFunc]:
        """
        Decorator to create an observable Dagster asset.

        Args:
            name: Asset name
            key_prefix: Asset key prefix
            description: Asset description
            group_name: Asset group name for UI organization
            deps: Asset dependencies
            **dagster_kwargs: Additional Dagster asset kwargs

        Returns:
            Decorated asset function

        Example:
            >>> @adapter.asset(name="clean_data", group_name="etl")
            >>> def clean_data(raw_data):
            ...     return raw_data.dropna()
        """
        def decorator(func: AssetFunc) -> AssetFunc:
            asset_name = name or func.__name__

            if self._dagster_available:
                asset_kwargs: Dict[str, Any] = {
                    "name": asset_name,
                    "key_prefix": key_prefix,
                    "description": description,
                    "group_name": group_name,
                    "deps": deps,
                    **dagster_kwargs,
                }
                # Filter None values
                asset_kwargs = {k: v for k, v in asset_kwargs.items() if v is not None}

                dagster_asset = dg.asset(**asset_kwargs)(func)

                self._registered_assets[asset_name] = dagster_asset
                return dagster_asset  # type: ignore
            else:
                self._registered_assets[asset_name] = func
                return func

        return decorator

    def schedule(
        self,
        cron_schedule: str,
        job: Optional[Any] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        default_status: Optional[Any] = None,
    ) -> Any:
        """
        Create a Dagster schedule.

        Args:
            cron_schedule: Cron expression (e.g., "0 * * * *" for hourly)
            job: The Dagster job to schedule
            name: Schedule name
            description: Schedule description
            default_status: Default schedule status (RUNNING or STOPPED)

        Returns:
            Dagster ScheduleDefinition

        Example:
            >>> schedule = adapter.schedule("0 */6 * * *", job=my_job, name="six_hourly")
        """
        if not self._dagster_available:
            logger.warning("Dagster not available, schedule not created")
            return None

        schedule_name = name or f"schedule_{cron_schedule.replace(' ', '_')}"

        # Resolve the underlying dagster job if wrapped
        actual_job = getattr(job, "_dagster_job", job) if job else None

        sched_kwargs: Dict[str, Any] = {
            "cron_schedule": cron_schedule,
            "name": schedule_name,
        }
        if actual_job is not None:
            sched_kwargs["job"] = actual_job
        if description:
            sched_kwargs["description"] = description
        if default_status is not None:
            sched_kwargs["default_status"] = default_status

        schedule_def = dg.ScheduleDefinition(**sched_kwargs)
        self._registered_schedules[schedule_name] = schedule_def

        logger.info(f"Created Dagster schedule '{schedule_name}': {cron_schedule}")
        return schedule_def

    def sensor(
        self,
        name: Optional[str] = None,
        job: Optional[Any] = None,
        minimum_interval_seconds: int = 30,
        description: Optional[str] = None,
    ) -> Callable:
        """
        Decorator to create a Dagster sensor.

        Args:
            name: Sensor name
            job: Target job
            minimum_interval_seconds: Minimum interval between evaluations
            description: Sensor description

        Returns:
            Decorated sensor function

        Example:
            >>> @adapter.sensor(name="new_files", job=process_job)
            >>> def new_files_sensor(context):
            ...     if new_files_exist():
            ...         yield dg.RunRequest(run_key="new_files")
        """
        def decorator(func):
            sensor_name = name or func.__name__

            if self._dagster_available:
                actual_job = getattr(job, "_dagster_job", job) if job else None

                sensor_kwargs: Dict[str, Any] = {
                    "name": sensor_name,
                    "minimum_interval_seconds": minimum_interval_seconds,
                }
                if actual_job is not None:
                    sensor_kwargs["job"] = actual_job
                if description:
                    sensor_kwargs["description"] = description

                dagster_sensor = dg.sensor(**sensor_kwargs)(func)
                self._registered_sensors[sensor_name] = dagster_sensor
                return dagster_sensor
            else:
                self._registered_sensors[sensor_name] = func
                return func

        return decorator

    def create_definitions(
        self,
        extra_assets: Optional[List[Any]] = None,
        extra_jobs: Optional[List[Any]] = None,
        extra_schedules: Optional[List[Any]] = None,
        extra_sensors: Optional[List[Any]] = None,
        resources: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Assemble a Dagster Definitions object from all registered components.

        Args:
            extra_assets: Additional assets to include
            extra_jobs: Additional jobs to include
            extra_schedules: Additional schedules to include
            extra_sensors: Additional sensors to include
            resources: Dagster resources (database connections, etc.)

        Returns:
            Dagster Definitions object
        """
        if not self._dagster_available:
            raise RuntimeError("Dagster is not installed")

        all_assets = list(self._registered_assets.values())
        if extra_assets:
            all_assets.extend(extra_assets)

        all_jobs = list(self._registered_jobs.values())
        if extra_jobs:
            all_jobs.extend(extra_jobs)

        all_schedules = list(self._registered_schedules.values())
        if extra_schedules:
            all_schedules.extend(extra_schedules)

        all_sensors = list(self._registered_sensors.values())
        if extra_sensors:
            all_sensors.extend(extra_sensors)

        defs_kwargs: Dict[str, Any] = {}
        if all_assets:
            defs_kwargs["assets"] = all_assets
        if all_jobs:
            defs_kwargs["jobs"] = all_jobs
        if all_schedules:
            defs_kwargs["schedules"] = all_schedules
        if all_sensors:
            defs_kwargs["sensors"] = all_sensors
        if resources:
            defs_kwargs["resources"] = resources

        definitions = dg.Definitions(**defs_kwargs)

        logger.info(
            f"Created Dagster Definitions with {len(all_assets)} assets, "
            f"{len(all_jobs)} jobs, {len(all_schedules)} schedules, "
            f"{len(all_sensors)} sensors"
        )
        return definitions

    def list_registered_jobs(self) -> List[str]:
        """List all registered jobs."""
        return list(self._registered_jobs.keys())

    def list_registered_ops(self) -> List[str]:
        """List all registered ops."""
        return list(self._registered_ops.keys())

    def list_registered_assets(self) -> List[str]:
        """List all registered assets."""
        return list(self._registered_assets.keys())

    def list_registered_schedules(self) -> List[str]:
        """List all registered schedules."""
        return list(self._registered_schedules.keys())

    def list_registered_sensors(self) -> List[str]:
        """List all registered sensors."""
        return list(self._registered_sensors.keys())

    def get_job(self, name: str) -> Optional[Any]:
        """Get a registered job by name."""
        return self._registered_jobs.get(name)

    def get_asset(self, name: str) -> Optional[Any]:
        """Get a registered asset by name."""
        return self._registered_assets.get(name)

    def get_schedule(self, name: str) -> Optional[Any]:
        """Get a registered schedule by name."""
        return self._registered_schedules.get(name)


# Convenience function to create adapter
def get_dagster_adapter(**kwargs) -> DagsterAdapter:
    """Create a DagsterAdapter instance."""
    return DagsterAdapter(**kwargs)
