"""
MLFlow experiment tracking integration.

This module provides:
- Context managers for experiment tracking
- Auto-logging for agent interactions
- Runtime enable/disable support

Example:
    >>> from agentic_assistants import AgenticConfig
    >>> from agentic_assistants.core import MLFlowTracker, track_experiment
    >>> 
    >>> config = AgenticConfig(mlflow_enabled=True)
    >>> tracker = MLFlowTracker(config)
    >>> 
    >>> with tracker.start_run(run_name="my-experiment"):
    ...     tracker.log_param("model", "llama3.2")
    ...     result = run_agent()
    ...     tracker.log_metric("accuracy", 0.95)
    
    >>> # Or use the decorator
    >>> @track_experiment("my-experiment")
    >>> def my_agent_task():
    ...     pass
"""

import functools
import os
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Optional, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

# Lazy import mlflow to avoid import errors when disabled
_mlflow = None


def _get_mlflow():
    """Lazy load MLFlow module."""
    global _mlflow
    if _mlflow is None:
        import mlflow

        _mlflow = mlflow
    return _mlflow


class MLFlowTracker:
    """
    MLFlow experiment tracking manager.
    
    This class wraps MLFlow functionality and respects the runtime
    enable/disable configuration. When disabled, all operations
    become no-ops.
    
    Attributes:
        config: Agentic configuration instance
        enabled: Whether tracking is enabled
        experiment_name: Current experiment name
    """

    def __init__(self, config: Optional[AgenticConfig] = None):
        """
        Initialize the MLFlow tracker.
        
        Args:
            config: Configuration instance. If None, uses default config.
        """
        self.config = config or AgenticConfig()
        self.enabled = self.config.mlflow_enabled
        self.experiment_name = self.config.mlflow.experiment_name
        self._active_run = None
        self._initialized = False

    def _initialize(self) -> None:
        """Initialize MLFlow connection and experiment."""
        if self._initialized or not self.enabled:
            return

        try:
            mlflow = _get_mlflow()
            mlflow.set_tracking_uri(self.config.mlflow.tracking_uri)

            # Create or get experiment
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                mlflow.create_experiment(
                    self.experiment_name,
                    artifact_location=self.config.mlflow.artifact_location,
                )
            mlflow.set_experiment(self.experiment_name)

            self._initialized = True
            logger.info(
                f"MLFlow initialized - tracking URI: {self.config.mlflow.tracking_uri}, "
                f"experiment: {self.experiment_name}"
            )

        except Exception as e:
            logger.warning(f"Failed to initialize MLFlow: {e}. Tracking disabled.")
            self.enabled = False

    @contextmanager
    def start_run(
        self,
        run_name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
        nested: bool = False,
    ):
        """
        Start an MLFlow run as a context manager.
        
        Args:
            run_name: Name for the run
            tags: Optional tags to apply to the run
            nested: Whether this is a nested run
        
        Yields:
            The active run object (or None if disabled)
        
        Example:
            >>> with tracker.start_run(run_name="agent-run") as run:
            ...     tracker.log_param("model", "llama3.2")
            ...     result = agent.run()
            ...     tracker.log_metric("duration", 10.5)
        """
        if not self.enabled:
            yield None
            return

        self._initialize()
        mlflow = _get_mlflow()

        run_name = run_name or f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        all_tags = {"framework": "agentic-assistants"}
        if tags:
            all_tags.update(tags)

        try:
            with mlflow.start_run(run_name=run_name, tags=all_tags, nested=nested) as run:
                self._active_run = run
                logger.debug(f"Started MLFlow run: {run_name} (ID: {run.info.run_id})")
                yield run

        except Exception as e:
            logger.error(f"Error in MLFlow run: {e}")
            raise
        finally:
            self._active_run = None

    def log_param(self, key: str, value: Any) -> None:
        """
        Log a parameter to the active run.
        
        Args:
            key: Parameter name
            value: Parameter value
        """
        if not self.enabled:
            return

        try:
            mlflow = _get_mlflow()
            mlflow.log_param(key, value)
        except Exception as e:
            logger.warning(f"Failed to log param {key}: {e}")

    def log_params(self, params: dict[str, Any]) -> None:
        """
        Log multiple parameters to the active run.
        
        Args:
            params: Dictionary of parameter names and values
        """
        if not self.enabled:
            return

        try:
            mlflow = _get_mlflow()
            mlflow.log_params(params)
        except Exception as e:
            logger.warning(f"Failed to log params: {e}")

    def log_metric(self, key: str, value: float, step: Optional[int] = None) -> None:
        """
        Log a metric to the active run.
        
        Args:
            key: Metric name
            value: Metric value
            step: Optional step number for the metric
        """
        if not self.enabled:
            return

        try:
            mlflow = _get_mlflow()
            mlflow.log_metric(key, value, step=step)
        except Exception as e:
            logger.warning(f"Failed to log metric {key}: {e}")

    def log_metrics(self, metrics: dict[str, float], step: Optional[int] = None) -> None:
        """
        Log multiple metrics to the active run.
        
        Args:
            metrics: Dictionary of metric names and values
            step: Optional step number
        """
        if not self.enabled:
            return

        try:
            mlflow = _get_mlflow()
            mlflow.log_metrics(metrics, step=step)
        except Exception as e:
            logger.warning(f"Failed to log metrics: {e}")

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        """
        Log a local file or directory as an artifact.
        
        Args:
            local_path: Path to the file or directory
            artifact_path: Optional path within the artifact store
        """
        if not self.enabled:
            return

        try:
            mlflow = _get_mlflow()
            mlflow.log_artifact(local_path, artifact_path)
        except Exception as e:
            logger.warning(f"Failed to log artifact {local_path}: {e}")

    def log_text(self, text: str, artifact_file: str) -> None:
        """
        Log text content as an artifact.
        
        Args:
            text: Text content to log
            artifact_file: Name of the artifact file
        """
        if not self.enabled:
            return

        try:
            mlflow = _get_mlflow()
            mlflow.log_text(text, artifact_file)
        except Exception as e:
            logger.warning(f"Failed to log text artifact {artifact_file}: {e}")

    def log_dict(self, dictionary: dict, artifact_file: str) -> None:
        """
        Log a dictionary as a JSON artifact.
        
        Args:
            dictionary: Dictionary to log
            artifact_file: Name of the artifact file (should end in .json)
        """
        if not self.enabled:
            return

        try:
            mlflow = _get_mlflow()
            mlflow.log_dict(dictionary, artifact_file)
        except Exception as e:
            logger.warning(f"Failed to log dict artifact {artifact_file}: {e}")

    def set_tag(self, key: str, value: str) -> None:
        """
        Set a tag on the active run.
        
        Args:
            key: Tag name
            value: Tag value
        """
        if not self.enabled:
            return

        try:
            mlflow = _get_mlflow()
            mlflow.set_tag(key, value)
        except Exception as e:
            logger.warning(f"Failed to set tag {key}: {e}")

    def log_agent_interaction(
        self,
        agent_name: str,
        input_text: str,
        output_text: str,
        model: str,
        duration_seconds: float,
        tokens_used: Optional[int] = None,
        step: Optional[int] = None,
    ) -> None:
        """
        Log an agent interaction with standardized metrics and artifacts.
        
        Args:
            agent_name: Name of the agent
            input_text: Input provided to the agent
            output_text: Output generated by the agent
            model: Model used for inference
            duration_seconds: Time taken for the interaction
            tokens_used: Optional token count
            step: Optional step number
        """
        if not self.enabled:
            return

        # Log metrics
        metrics = {"duration_seconds": duration_seconds}
        if tokens_used:
            metrics["tokens_used"] = tokens_used
        self.log_metrics(metrics, step=step)

        # Log interaction details as artifact
        interaction = {
            "agent": agent_name,
            "model": model,
            "input": input_text,
            "output": output_text,
            "duration": duration_seconds,
            "tokens": tokens_used,
            "timestamp": datetime.now().isoformat(),
        }
        artifact_name = f"interactions/step_{step or 0}_{agent_name}.json"
        self.log_dict(interaction, artifact_name)

    def get_run_url(self) -> Optional[str]:
        """
        Get the URL for the current run in the MLFlow UI.
        
        Returns:
            URL string or None if no active run
        """
        if not self.enabled or not self._active_run:
            return None

        run_id = self._active_run.info.run_id
        tracking_uri = self.config.mlflow.tracking_uri
        return f"{tracking_uri}/#/experiments/{self._active_run.info.experiment_id}/runs/{run_id}"


def track_experiment(
    experiment_name: Optional[str] = None,
    run_name: Optional[str] = None,
    tags: Optional[dict[str, str]] = None,
    log_args: bool = True,
) -> Callable:
    """
    Decorator to track a function execution as an MLFlow experiment.
    
    Args:
        experiment_name: Name of the experiment (uses default if None)
        run_name: Name for the run (uses function name if None)
        tags: Optional tags to apply to the run
        log_args: Whether to log function arguments as parameters
    
    Returns:
        Decorated function
    
    Example:
        >>> @track_experiment("research-agent", log_args=True)
        >>> def research_task(topic: str, depth: int = 3):
        ...     # This will automatically log topic and depth as params
        ...     return perform_research(topic, depth)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            config = AgenticConfig()
            if not config.mlflow_enabled:
                return func(*args, **kwargs)

            tracker = MLFlowTracker(config)
            if experiment_name:
                tracker.experiment_name = experiment_name

            actual_run_name = run_name or func.__name__

            with tracker.start_run(run_name=actual_run_name, tags=tags):
                # Log function arguments as parameters
                if log_args:
                    # Log kwargs directly
                    for key, value in kwargs.items():
                        tracker.log_param(key, value)

                    # Log positional args with generic names
                    for i, arg in enumerate(args):
                        tracker.log_param(f"arg_{i}", arg)

                # Track execution time
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    tracker.log_metric("success", 1)
                    return result
                except Exception as e:
                    tracker.log_metric("success", 0)
                    tracker.set_tag("error", str(e))
                    raise
                finally:
                    duration = time.time() - start_time
                    tracker.log_metric("duration_seconds", duration)

        return wrapper

    return decorator


# Convenience function for starting tracking server
def start_mlflow_server(
    host: str = "127.0.0.1",
    port: int = 5000,
    backend_store_uri: str = "./mlruns",
    artifact_root: Optional[str] = None,
) -> subprocess.Popen:
    """
    Start the MLFlow tracking server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        backend_store_uri: URI for the backend store
        artifact_root: Root directory for artifacts
    
    Returns:
        Subprocess handle for the server
    """
    import subprocess

    cmd = [
        "mlflow",
        "server",
        "--host",
        host,
        "--port",
        str(port),
        "--backend-store-uri",
        backend_store_uri,
    ]

    if artifact_root:
        cmd.extend(["--default-artifact-root", artifact_root])

    logger.info(f"Starting MLFlow server on {host}:{port}")
    return subprocess.Popen(cmd)

