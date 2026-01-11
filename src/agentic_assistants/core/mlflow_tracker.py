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
import subprocess
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


# ============================================================================
# Enhanced MLFlow Manager
# ============================================================================

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class ModelStage(str, Enum):
    """Model lifecycle stages."""
    NONE = "None"
    STAGING = "Staging"
    PRODUCTION = "Production"
    ARCHIVED = "Archived"


class DeploymentTarget(str, Enum):
    """Deployment target types."""
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    SAGEMAKER = "sagemaker"


@dataclass
class ModelVersion:
    """Information about a model version."""
    name: str
    version: str
    stage: ModelStage
    run_id: str
    source: str
    status: str
    created_at: str
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class DeploymentInfo:
    """Information about a model deployment."""
    model_name: str
    model_version: str
    target: DeploymentTarget
    endpoint: str = ""
    status: str = "pending"
    config: Dict[str, Any] = field(default_factory=dict)


class MLFlowManager:
    """
    Enhanced MLFlow management for project-level experiments.
    
    This class provides:
    - Project-level experiment management
    - Model registry operations
    - Model deployment helpers
    - Run comparison and analysis
    
    Attributes:
        config: AgenticConfig instance
        tracker: MLFlowTracker for tracking operations
    """
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """
        Initialize the MLFlow manager.
        
        Args:
            config: Configuration instance
        """
        self.config = config or AgenticConfig()
        self.tracker = MLFlowTracker(config)
        self._client = None
    
    @property
    def client(self):
        """Get MLFlow tracking client."""
        if not self.config.mlflow_enabled:
            return None
        
        if self._client is None:
            mlflow = _get_mlflow()
            self._client = mlflow.tracking.MlflowClient(
                tracking_uri=self.config.mlflow.tracking_uri
            )
        return self._client
    
    # =========================================================================
    # Project Experiment Management
    # =========================================================================
    
    def create_project_experiment(
        self,
        project_id: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Create an experiment for a project.
        
        Args:
            project_id: Project ID
            description: Optional experiment description
            tags: Optional experiment tags
        
        Returns:
            Experiment ID
        """
        if not self.config.mlflow_enabled:
            return ""
        
        mlflow = _get_mlflow()
        experiment_name = f"project-{project_id}"
        
        # Check if experiment exists
        existing = mlflow.get_experiment_by_name(experiment_name)
        if existing:
            return existing.experiment_id
        
        # Create new experiment
        artifact_location = self.config.mlflow.artifact_location
        if artifact_location:
            artifact_location = f"{artifact_location}/{project_id}"
        
        experiment_id = mlflow.create_experiment(
            name=experiment_name,
            artifact_location=artifact_location,
            tags=tags or {},
        )
        
        logger.info(f"Created experiment for project {project_id}: {experiment_id}")
        return experiment_id
    
    def get_project_runs(
        self,
        project_id: str,
        max_results: int = 100,
        filter_string: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all runs for a project.
        
        Args:
            project_id: Project ID
            max_results: Maximum number of runs to return
            filter_string: Optional MLFlow filter string
        
        Returns:
            List of run information dictionaries
        """
        if not self.config.mlflow_enabled or not self.client:
            return []
        
        experiment_name = f"project-{project_id}"
        mlflow = _get_mlflow()
        
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if not experiment:
            return []
        
        runs = self.client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string=filter_string or "",
            max_results=max_results,
        )
        
        return [
            {
                "run_id": run.info.run_id,
                "run_name": run.info.run_name,
                "status": run.info.status,
                "start_time": run.info.start_time,
                "end_time": run.info.end_time,
                "metrics": run.data.metrics,
                "params": run.data.params,
                "tags": run.data.tags,
            }
            for run in runs
        ]
    
    def compare_runs(
        self,
        run_ids: List[str],
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compare multiple runs.
        
        Args:
            run_ids: List of run IDs to compare
            metrics: Optional list of metrics to compare
        
        Returns:
            Comparison data dictionary
        """
        if not self.config.mlflow_enabled or not self.client:
            return {"runs": [], "comparison": {}}
        
        runs = []
        all_metrics = set()
        all_params = set()
        
        for run_id in run_ids:
            try:
                run = self.client.get_run(run_id)
                runs.append({
                    "run_id": run_id,
                    "run_name": run.info.run_name,
                    "metrics": run.data.metrics,
                    "params": run.data.params,
                })
                all_metrics.update(run.data.metrics.keys())
                all_params.update(run.data.params.keys())
            except Exception as e:
                logger.warning(f"Failed to get run {run_id}: {e}")
        
        # Build comparison matrix
        if metrics:
            compare_metrics = [m for m in metrics if m in all_metrics]
        else:
            compare_metrics = list(all_metrics)
        
        comparison = {
            "metrics": {
                metric: [
                    r["metrics"].get(metric)
                    for r in runs
                ]
                for metric in compare_metrics
            },
            "params": {
                param: [
                    r["params"].get(param)
                    for r in runs
                ]
                for param in all_params
            },
        }
        
        return {
            "runs": runs,
            "comparison": comparison,
        }
    
    # =========================================================================
    # Model Registry
    # =========================================================================
    
    def register_model(
        self,
        run_id: str,
        model_path: str,
        model_name: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> Optional[ModelVersion]:
        """
        Register a model from a run to the model registry.
        
        Args:
            run_id: Run ID containing the model
            model_path: Path to model within run artifacts
            model_name: Name to register the model under
            tags: Optional tags for the model version
        
        Returns:
            ModelVersion or None if failed
        """
        if not self.config.mlflow_enabled or not self.client:
            return None
        
        mlflow = _get_mlflow()
        
        try:
            # Create registered model if it doesn't exist
            try:
                self.client.create_registered_model(model_name)
            except Exception:
                pass  # Model already exists
            
            # Create model version
            source = f"runs:/{run_id}/{model_path}"
            version = self.client.create_model_version(
                name=model_name,
                source=source,
                run_id=run_id,
                tags=tags,
            )
            
            logger.info(f"Registered model {model_name} version {version.version}")
            
            return ModelVersion(
                name=model_name,
                version=version.version,
                stage=ModelStage(version.current_stage),
                run_id=run_id,
                source=source,
                status=version.status,
                created_at=str(version.creation_timestamp),
                tags=tags or {},
            )
            
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            return None
    
    def transition_model_stage(
        self,
        model_name: str,
        version: str,
        stage: ModelStage,
        archive_existing: bool = True,
    ) -> bool:
        """
        Transition a model version to a new stage.
        
        Args:
            model_name: Registered model name
            version: Model version
            stage: Target stage
            archive_existing: Whether to archive existing models in that stage
        
        Returns:
            True if successful
        """
        if not self.config.mlflow_enabled or not self.client:
            return False
        
        try:
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage.value,
                archive_existing_versions=archive_existing,
            )
            
            logger.info(f"Transitioned {model_name} v{version} to {stage.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to transition model stage: {e}")
            return False
    
    def get_model_versions(
        self,
        model_name: str,
        stages: Optional[List[ModelStage]] = None,
    ) -> List[ModelVersion]:
        """
        Get all versions of a registered model.
        
        Args:
            model_name: Registered model name
            stages: Optional filter by stages
        
        Returns:
            List of ModelVersion instances
        """
        if not self.config.mlflow_enabled or not self.client:
            return []
        
        try:
            filter_str = f"name='{model_name}'"
            if stages:
                stage_filter = " OR ".join([f"current_stage='{s.value}'" for s in stages])
                filter_str = f"{filter_str} AND ({stage_filter})"
            
            versions = self.client.search_model_versions(filter_str)
            
            return [
                ModelVersion(
                    name=v.name,
                    version=v.version,
                    stage=ModelStage(v.current_stage),
                    run_id=v.run_id,
                    source=v.source,
                    status=v.status,
                    created_at=str(v.creation_timestamp),
                    tags=v.tags or {},
                )
                for v in versions
            ]
            
        except Exception as e:
            logger.error(f"Failed to get model versions: {e}")
            return []
    
    def list_registered_models(self) -> List[Dict[str, Any]]:
        """
        List all registered models.
        
        Returns:
            List of registered model info dictionaries
        """
        if not self.config.mlflow_enabled or not self.client:
            return []
        
        try:
            models = self.client.search_registered_models()
            
            return [
                {
                    "name": m.name,
                    "creation_timestamp": m.creation_timestamp,
                    "last_updated_timestamp": m.last_updated_timestamp,
                    "description": m.description,
                    "latest_versions": [
                        {
                            "version": v.version,
                            "stage": v.current_stage,
                            "run_id": v.run_id,
                        }
                        for v in (m.latest_versions or [])
                    ],
                }
                for m in models
            ]
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    # =========================================================================
    # Model Deployment
    # =========================================================================
    
    def deploy_model(
        self,
        model_name: str,
        target: DeploymentTarget,
        version: Optional[str] = None,
        stage: Optional[ModelStage] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> DeploymentInfo:
        """
        Deploy a model to a target environment.
        
        Args:
            model_name: Registered model name
            target: Deployment target
            version: Specific version to deploy (or use stage)
            stage: Stage to deploy from (e.g., Production)
            config: Deployment configuration
        
        Returns:
            DeploymentInfo with status
        """
        if not self.config.mlflow_enabled:
            return DeploymentInfo(
                model_name=model_name,
                model_version=version or "unknown",
                target=target,
                status="disabled",
            )
        
        mlflow = _get_mlflow()
        
        # Determine model version
        if version:
            model_uri = f"models:/{model_name}/{version}"
            model_version = version
        elif stage:
            model_uri = f"models:/{model_name}/{stage.value}"
            # Get actual version for the stage
            versions = self.get_model_versions(model_name, stages=[stage])
            model_version = versions[0].version if versions else "unknown"
        else:
            # Default to latest production
            model_uri = f"models:/{model_name}/Production"
            versions = self.get_model_versions(model_name, stages=[ModelStage.PRODUCTION])
            model_version = versions[0].version if versions else "unknown"
        
        deployment = DeploymentInfo(
            model_name=model_name,
            model_version=model_version,
            target=target,
            config=config or {},
        )
        
        try:
            if target == DeploymentTarget.LOCAL:
                # Local deployment using MLFlow's built-in serve
                deployment.endpoint = f"http://127.0.0.1:5001/invocations"
                deployment.status = "ready"
                deployment.config["command"] = f"mlflow models serve -m {model_uri} -p 5001"
                
            elif target == DeploymentTarget.DOCKER:
                # Build Docker image
                deployment.config["image_name"] = f"{model_name}:{model_version}"
                deployment.config["command"] = f"mlflow models build-docker -m {model_uri} -n {model_name}:{model_version}"
                deployment.status = "pending"
                
            elif target == DeploymentTarget.SAGEMAKER:
                # SageMaker deployment config
                deployment.config["app_name"] = f"{model_name}-{model_version}"
                deployment.status = "pending"
                logger.info("SageMaker deployment requires additional AWS configuration")
                
            else:
                deployment.status = "unsupported"
                logger.warning(f"Deployment target {target} not fully implemented")
            
            logger.info(f"Prepared deployment for {model_name} v{model_version} to {target.value}")
            
        except Exception as e:
            deployment.status = "error"
            deployment.config["error"] = str(e)
            logger.error(f"Failed to prepare deployment: {e}")
        
        return deployment
    
    def get_model_serving_input_example(
        self,
        model_name: str,
        version: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get an input example for a registered model.
        
        Args:
            model_name: Model name
            version: Optional version
        
        Returns:
            Input example dict or None
        """
        if not self.config.mlflow_enabled:
            return None
        
        mlflow = _get_mlflow()
        
        try:
            if version:
                model_uri = f"models:/{model_name}/{version}"
            else:
                model_uri = f"models:/{model_name}/Production"
            
            model_info = mlflow.models.get_model_info(model_uri)
            
            if hasattr(model_info, 'signature') and model_info.signature:
                inputs = model_info.signature.inputs
                if inputs:
                    return {"inputs": inputs.to_dict()}
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get input example: {e}")
            return None

