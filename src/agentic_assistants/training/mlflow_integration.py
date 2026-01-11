"""
MLFlow integration for LLM training.

This module provides two-way integration between the training system and MLFlow:
- Track training runs and metrics in MLFlow
- Register trained models in MLFlow Model Registry
- Sync models from MLFlow Registry to local registry
- Deploy models from MLFlow

Example:
    >>> from agentic_assistants.training.mlflow_integration import TrainingMLFlowIntegration
    >>> 
    >>> integration = TrainingMLFlowIntegration()
    >>> 
    >>> # Start tracking a training run
    >>> with integration.start_training_run("llama-finetune", config) as run:
    ...     # Training happens here
    ...     integration.log_training_metrics({"loss": 0.5, "epoch": 1})
    >>> 
    >>> # Register model after training
    >>> model_version = integration.register_trained_model(
    ...     job_id="job-123",
    ...     model_path="./outputs/model",
    ...     model_name="my-llama-lora"
    ... )
"""

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.mlflow_tracker import MLFlowTracker, ModelStage, ModelVersion
from agentic_assistants.training.config import TrainingConfig, CustomModelInfo, TrainingMethod
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

# Lazy import mlflow
_mlflow = None


def _get_mlflow():
    """Lazy load MLFlow module."""
    global _mlflow
    if _mlflow is None:
        import mlflow
        _mlflow = mlflow
    return _mlflow


@dataclass
class TrainingRunInfo:
    """Information about a training run in MLFlow."""
    
    run_id: str
    experiment_id: str
    run_name: str
    status: str
    
    # Training info
    job_id: Optional[str] = None
    model_name: Optional[str] = None
    base_model: Optional[str] = None
    training_method: Optional[str] = None
    
    # Metrics
    final_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Artifacts
    model_uri: Optional[str] = None
    artifact_uri: Optional[str] = None
    
    # Timestamps
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "experiment_id": self.experiment_id,
            "run_name": self.run_name,
            "status": self.status,
            "job_id": self.job_id,
            "model_name": self.model_name,
            "base_model": self.base_model,
            "training_method": self.training_method,
            "final_metrics": self.final_metrics,
            "model_uri": self.model_uri,
            "artifact_uri": self.artifact_uri,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }


class TrainingMLFlowIntegration:
    """
    MLFlow integration for training runs.
    
    Provides:
    - Experiment tracking for training jobs
    - Model registration in MLFlow Registry
    - Two-way sync between local and MLFlow registries
    - Model deployment from MLFlow
    """
    
    # Custom tags for training runs
    TAG_TRAINING_JOB_ID = "agentic.training.job_id"
    TAG_BASE_MODEL = "agentic.training.base_model"
    TAG_TRAINING_METHOD = "agentic.training.method"
    TAG_FRAMEWORK = "agentic.training.framework"
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """
        Initialize the MLFlow integration.
        
        Args:
            config: Configuration instance
        """
        self.config = config or AgenticConfig()
        self.tracker = MLFlowTracker(config)
        self._client = None
        self._active_run = None
    
    @property
    def enabled(self) -> bool:
        """Check if MLFlow is enabled."""
        return self.config.mlflow_enabled
    
    @property
    def client(self):
        """Get MLFlow tracking client."""
        if not self.enabled:
            return None
        
        if self._client is None:
            mlflow = _get_mlflow()
            mlflow.set_tracking_uri(self.config.mlflow.tracking_uri)
            self._client = mlflow.tracking.MlflowClient()
        return self._client
    
    def _ensure_experiment(self, experiment_name: str) -> str:
        """Ensure experiment exists and return its ID."""
        if not self.enabled:
            return ""
        
        mlflow = _get_mlflow()
        experiment = mlflow.get_experiment_by_name(experiment_name)
        
        if experiment is None:
            experiment_id = mlflow.create_experiment(
                name=experiment_name,
                artifact_location=self.config.mlflow.artifact_location,
            )
        else:
            experiment_id = experiment.experiment_id
        
        return experiment_id
    
    @contextmanager
    def start_training_run(
        self,
        run_name: str,
        config: TrainingConfig,
        experiment_name: Optional[str] = None,
    ) -> Generator[Optional[TrainingRunInfo], None, None]:
        """
        Start a training run context.
        
        Args:
            run_name: Name for the run
            config: Training configuration
            experiment_name: MLFlow experiment name (defaults to config or "training")
        
        Yields:
            TrainingRunInfo with run details
        """
        if not self.enabled:
            yield None
            return
        
        mlflow = _get_mlflow()
        
        # Determine experiment name
        exp_name = experiment_name or config.mlflow_experiment_name or "llm-training"
        self._ensure_experiment(exp_name)
        mlflow.set_experiment(exp_name)
        
        # Build tags
        tags = {
            self.TAG_BASE_MODEL: config.base_model,
            self.TAG_TRAINING_METHOD: config.method.value,
            self.TAG_FRAMEWORK: config.framework,
            "mlflow.runName": run_name,
        }
        
        try:
            with mlflow.start_run(run_name=run_name, tags=tags) as run:
                self._active_run = run
                
                # Log training parameters
                self._log_training_params(config)
                
                run_info = TrainingRunInfo(
                    run_id=run.info.run_id,
                    experiment_id=run.info.experiment_id,
                    run_name=run_name,
                    status="RUNNING",
                    model_name=config.output_name,
                    base_model=config.base_model,
                    training_method=config.method.value,
                    start_time=datetime.utcnow().isoformat(),
                )
                
                yield run_info
                
                # Update status on successful completion
                run_info.status = "FINISHED"
                run_info.end_time = datetime.utcnow().isoformat()
                run_info.artifact_uri = run.info.artifact_uri
                
        except Exception as e:
            logger.error(f"Training run failed: {e}")
            raise
        finally:
            self._active_run = None
    
    def _log_training_params(self, config: TrainingConfig) -> None:
        """Log training parameters to MLFlow."""
        if not self.enabled or not self._active_run:
            return
        
        mlflow = _get_mlflow()
        
        params = {
            "base_model": config.base_model,
            "output_name": config.output_name,
            "method": config.method.value,
            "framework": config.framework,
            "num_epochs": config.num_epochs,
            "batch_size": config.batch_size,
            "learning_rate": config.learning_rate,
            "max_seq_length": config.max_seq_length,
            "gradient_accumulation_steps": config.gradient_accumulation_steps,
            "bf16": config.bf16,
            "gradient_checkpointing": config.gradient_checkpointing,
        }
        
        # Add LoRA params if applicable
        lora_config = config.get_effective_lora_config()
        if lora_config:
            params["lora_r"] = lora_config.r
            params["lora_alpha"] = lora_config.lora_alpha
            params["lora_dropout"] = lora_config.lora_dropout
        
        mlflow.log_params(params)
    
    def log_training_metrics(
        self,
        metrics: Dict[str, float],
        step: Optional[int] = None,
    ) -> None:
        """
        Log training metrics.
        
        Args:
            metrics: Dictionary of metric names and values
            step: Optional step number
        """
        if not self.enabled or not self._active_run:
            return
        
        mlflow = _get_mlflow()
        mlflow.log_metrics(metrics, step=step)
    
    def log_training_artifact(
        self,
        local_path: str,
        artifact_path: Optional[str] = None,
    ) -> None:
        """
        Log a training artifact.
        
        Args:
            local_path: Path to local file or directory
            artifact_path: Path within artifacts
        """
        if not self.enabled or not self._active_run:
            return
        
        mlflow = _get_mlflow()
        mlflow.log_artifact(local_path, artifact_path)
    
    def log_model_config(
        self,
        config: Dict[str, Any],
        filename: str = "training_config.json",
    ) -> None:
        """Log model/training configuration as artifact."""
        if not self.enabled or not self._active_run:
            return
        
        mlflow = _get_mlflow()
        mlflow.log_dict(config, filename)
    
    def register_trained_model(
        self,
        job_id: str,
        model_path: str,
        model_name: str,
        config: Optional[TrainingConfig] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Optional[ModelVersion]:
        """
        Register a trained model in MLFlow Registry.
        
        Args:
            job_id: Training job ID
            model_path: Path to model directory
            model_name: Name to register under
            config: Training configuration used
            tags: Additional tags
        
        Returns:
            ModelVersion if successful
        """
        if not self.enabled:
            return None
        
        mlflow = _get_mlflow()
        
        try:
            # Create a run to log the model if not in active run
            if self._active_run:
                run_id = self._active_run.info.run_id
            else:
                # Start a new run for registration
                with mlflow.start_run(run_name=f"register-{model_name}") as run:
                    run_id = run.info.run_id
                    
                    # Log model
                    mlflow.log_artifacts(model_path, "model")
                    
                    if config:
                        mlflow.log_params({
                            "base_model": config.base_model,
                            "method": config.method.value,
                        })
            
            # Register the model
            model_uri = f"runs:/{run_id}/model"
            
            all_tags = {
                self.TAG_TRAINING_JOB_ID: job_id,
            }
            if config:
                all_tags[self.TAG_BASE_MODEL] = config.base_model
                all_tags[self.TAG_TRAINING_METHOD] = config.method.value
            if tags:
                all_tags.update(tags)
            
            # Create registered model if doesn't exist
            try:
                self.client.create_registered_model(model_name)
            except Exception:
                pass  # Model already exists
            
            # Create version
            version = self.client.create_model_version(
                name=model_name,
                source=model_uri,
                run_id=run_id,
                tags=all_tags,
            )
            
            logger.info(f"Registered model {model_name} version {version.version}")
            
            return ModelVersion(
                name=model_name,
                version=version.version,
                stage=ModelStage(version.current_stage),
                run_id=run_id,
                source=model_uri,
                status=version.status,
                created_at=str(version.creation_timestamp),
                tags=all_tags,
            )
            
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            return None
    
    def get_model_from_registry(
        self,
        model_name: str,
        version: Optional[str] = None,
        stage: Optional[ModelStage] = None,
    ) -> Optional[str]:
        """
        Get a model URI from the registry.
        
        Args:
            model_name: Registered model name
            version: Specific version
            stage: Specific stage (Production, Staging, etc.)
        
        Returns:
            Model URI or None
        """
        if not self.enabled:
            return None
        
        if version:
            return f"models:/{model_name}/{version}"
        elif stage:
            return f"models:/{model_name}/{stage.value}"
        else:
            return f"models:/{model_name}/latest"
    
    def sync_from_mlflow(self) -> List[CustomModelInfo]:
        """
        Sync models from MLFlow registry to local registry.
        
        Returns:
            List of synced model info
        """
        if not self.enabled or not self.client:
            return []
        
        synced_models = []
        
        try:
            # Get all registered models
            models = self.client.search_registered_models()
            
            for model in models:
                # Get latest version
                versions = self.client.search_model_versions(f"name='{model.name}'")
                
                for version in versions:
                    # Check if it's one of our training runs
                    tags = version.tags or {}
                    
                    if self.TAG_TRAINING_JOB_ID in tags:
                        model_info = CustomModelInfo(
                            id=f"mlflow-{version.name}-{version.version}",
                            name=f"{version.name}-v{version.version}",
                            base_model=tags.get(self.TAG_BASE_MODEL, "unknown"),
                            training_method=TrainingMethod(
                                tags.get(self.TAG_TRAINING_METHOD, "lora")
                            ),
                            training_job_id=tags.get(self.TAG_TRAINING_JOB_ID, ""),
                            local_path="",  # MLFlow managed
                            status="registered",
                            mlflow_run_id=version.run_id,
                            mlflow_model_uri=version.source,
                            created_at=str(version.creation_timestamp),
                        )
                        synced_models.append(model_info)
            
            logger.info(f"Synced {len(synced_models)} models from MLFlow")
            
        except Exception as e:
            logger.error(f"Failed to sync from MLFlow: {e}")
        
        return synced_models
    
    def list_training_runs(
        self,
        experiment_name: Optional[str] = None,
        max_results: int = 100,
    ) -> List[TrainingRunInfo]:
        """
        List training runs from MLFlow.
        
        Args:
            experiment_name: Filter by experiment
            max_results: Maximum runs to return
        
        Returns:
            List of training run info
        """
        if not self.enabled or not self.client:
            return []
        
        runs = []
        
        try:
            mlflow = _get_mlflow()
            
            # Get experiment IDs
            if experiment_name:
                experiment = mlflow.get_experiment_by_name(experiment_name)
                experiment_ids = [experiment.experiment_id] if experiment else []
            else:
                # Get all experiments
                experiments = mlflow.search_experiments()
                experiment_ids = [e.experiment_id for e in experiments]
            
            if not experiment_ids:
                return []
            
            # Search runs with training tags
            filter_string = f"tags.`{self.TAG_BASE_MODEL}` != ''"
            
            mlflow_runs = self.client.search_runs(
                experiment_ids=experiment_ids,
                filter_string=filter_string,
                max_results=max_results,
            )
            
            for run in mlflow_runs:
                tags = run.data.tags
                
                run_info = TrainingRunInfo(
                    run_id=run.info.run_id,
                    experiment_id=run.info.experiment_id,
                    run_name=tags.get("mlflow.runName", ""),
                    status=run.info.status,
                    job_id=tags.get(self.TAG_TRAINING_JOB_ID),
                    model_name=run.data.params.get("output_name"),
                    base_model=tags.get(self.TAG_BASE_MODEL),
                    training_method=tags.get(self.TAG_TRAINING_METHOD),
                    final_metrics=run.data.metrics,
                    artifact_uri=run.info.artifact_uri,
                    start_time=str(run.info.start_time) if run.info.start_time else None,
                    end_time=str(run.info.end_time) if run.info.end_time else None,
                )
                runs.append(run_info)
            
        except Exception as e:
            logger.error(f"Failed to list training runs: {e}")
        
        return runs
    
    def get_training_run(self, run_id: str) -> Optional[TrainingRunInfo]:
        """Get details of a specific training run."""
        if not self.enabled or not self.client:
            return None
        
        try:
            run = self.client.get_run(run_id)
            tags = run.data.tags
            
            return TrainingRunInfo(
                run_id=run.info.run_id,
                experiment_id=run.info.experiment_id,
                run_name=tags.get("mlflow.runName", ""),
                status=run.info.status,
                job_id=tags.get(self.TAG_TRAINING_JOB_ID),
                model_name=run.data.params.get("output_name"),
                base_model=tags.get(self.TAG_BASE_MODEL),
                training_method=tags.get(self.TAG_TRAINING_METHOD),
                final_metrics=run.data.metrics,
                artifact_uri=run.info.artifact_uri,
                start_time=str(run.info.start_time) if run.info.start_time else None,
                end_time=str(run.info.end_time) if run.info.end_time else None,
            )
            
        except Exception as e:
            logger.error(f"Failed to get run {run_id}: {e}")
            return None
    
    def compare_training_runs(
        self,
        run_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Compare multiple training runs.
        
        Args:
            run_ids: List of run IDs to compare
        
        Returns:
            Comparison data
        """
        if not self.enabled or not self.client:
            return {"runs": [], "comparison": {}}
        
        runs = []
        all_metrics = set()
        all_params = set()
        
        for run_id in run_ids:
            try:
                run = self.client.get_run(run_id)
                run_data = {
                    "run_id": run_id,
                    "run_name": run.data.tags.get("mlflow.runName", ""),
                    "metrics": run.data.metrics,
                    "params": run.data.params,
                    "status": run.info.status,
                }
                runs.append(run_data)
                all_metrics.update(run.data.metrics.keys())
                all_params.update(run.data.params.keys())
            except Exception as e:
                logger.warning(f"Failed to get run {run_id}: {e}")
        
        # Build comparison
        comparison = {
            "metrics": {
                metric: [r["metrics"].get(metric) for r in runs]
                for metric in all_metrics
            },
            "params": {
                param: [r["params"].get(param) for r in runs]
                for param in all_params
            },
        }
        
        return {
            "runs": runs,
            "comparison": comparison,
        }
    
    def download_model(
        self,
        model_uri: str,
        destination: str,
    ) -> str:
        """
        Download a model from MLFlow.
        
        Args:
            model_uri: MLFlow model URI
            destination: Local destination path
        
        Returns:
            Path to downloaded model
        """
        if not self.enabled:
            return ""
        
        mlflow = _get_mlflow()
        
        try:
            return mlflow.artifacts.download_artifacts(
                artifact_uri=model_uri,
                dst_path=destination,
            )
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            return ""
    
    def transition_model_stage(
        self,
        model_name: str,
        version: str,
        stage: ModelStage,
    ) -> bool:
        """
        Transition a model to a new stage.
        
        Args:
            model_name: Registered model name
            version: Model version
            stage: Target stage
        
        Returns:
            True if successful
        """
        if not self.enabled or not self.client:
            return False
        
        try:
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage.value,
            )
            logger.info(f"Transitioned {model_name} v{version} to {stage.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to transition model: {e}")
            return False


def create_training_metrics_callback(
    integration: TrainingMLFlowIntegration,
) -> Callable[[Dict[str, Any]], None]:
    """
    Create a metrics callback for training jobs.
    
    Args:
        integration: MLFlow integration instance
    
    Returns:
        Callback function for logging metrics
    """
    step_counter = [0]
    
    def callback(metrics: Dict[str, Any]) -> None:
        # Extract step if present
        step = metrics.pop("step", None) or step_counter[0]
        step_counter[0] = step + 1
        
        # Log metrics
        float_metrics = {
            k: float(v) for k, v in metrics.items()
            if isinstance(v, (int, float))
        }
        
        if float_metrics:
            integration.log_training_metrics(float_metrics, step=step)
    
    return callback
