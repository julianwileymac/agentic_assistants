"""
RL experiment management.

This module provides classes for tracking and managing RL experiments.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_assistants.rl.config import RLConfig, RLMethod
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class RLExperimentStatus(str, Enum):
    """Status of an RL experiment."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RLExperiment:
    """
    Represents an RL experiment.
    
    An experiment tracks the full lifecycle of RL training including
    configuration, status, metrics, and results.
    """
    
    id: str
    name: str
    method: RLMethod
    config: Dict[str, Any]
    
    # Status
    status: RLExperimentStatus = RLExperimentStatus.PENDING
    
    # Model references
    base_model: str = ""
    reward_model_id: Optional[str] = None
    output_model_id: Optional[str] = None
    
    # Dataset references
    preference_dataset_id: Optional[str] = None
    prompt_dataset_id: Optional[str] = None
    
    # Metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Timing
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # Logs and errors
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    
    # MLFlow tracking
    mlflow_experiment_id: Optional[str] = None
    mlflow_run_id: Optional[str] = None
    
    # Tags and metadata
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "method": self.method.value,
            "config": self.config,
            "status": self.status.value,
            "base_model": self.base_model,
            "reward_model_id": self.reward_model_id,
            "output_model_id": self.output_model_id,
            "preference_dataset_id": self.preference_dataset_id,
            "prompt_dataset_id": self.prompt_dataset_id,
            "metrics": self.metrics,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "logs": self.logs[-100:],
            "error_message": self.error_message,
            "mlflow_experiment_id": self.mlflow_experiment_id,
            "mlflow_run_id": self.mlflow_run_id,
            "tags": self.tags,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RLExperiment":
        return cls(
            id=data["id"],
            name=data["name"],
            method=RLMethod(data["method"]),
            config=data.get("config", {}),
            status=RLExperimentStatus(data.get("status", "pending")),
            base_model=data.get("base_model", ""),
            reward_model_id=data.get("reward_model_id"),
            output_model_id=data.get("output_model_id"),
            preference_dataset_id=data.get("preference_dataset_id"),
            prompt_dataset_id=data.get("prompt_dataset_id"),
            metrics=data.get("metrics", {}),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            logs=data.get("logs", []),
            error_message=data.get("error_message"),
            mlflow_experiment_id=data.get("mlflow_experiment_id"),
            mlflow_run_id=data.get("mlflow_run_id"),
            tags=data.get("tags", []),
            description=data.get("description"),
        )
    
    def add_log(self, message: str) -> None:
        """Add a log message."""
        timestamp = datetime.utcnow().isoformat()
        self.logs.append(f"[{timestamp}] {message}")
    
    def update_metrics(self, metrics: Dict[str, float]) -> None:
        """Update metrics."""
        self.metrics.update(metrics)


class RLExperimentManager:
    """
    Manager for RL experiments.
    
    Provides:
    - Experiment CRUD operations
    - Experiment execution
    - Metrics tracking
    - Integration with MLFlow
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the experiment manager.
        
        Args:
            storage_path: Path to store experiment data
        """
        self.storage_path = Path(storage_path or "./data/rl/experiments")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._experiments: Dict[str, RLExperiment] = {}
        self._load_experiments()
    
    def _load_experiments(self) -> None:
        """Load experiments from disk."""
        for exp_file in self.storage_path.glob("*.json"):
            try:
                with open(exp_file, "r") as f:
                    data = json.load(f)
                experiment = RLExperiment.from_dict(data)
                self._experiments[experiment.id] = experiment
            except Exception as e:
                logger.warning(f"Failed to load experiment from {exp_file}: {e}")
    
    def _save_experiment(self, experiment: RLExperiment) -> None:
        """Save experiment to disk."""
        exp_file = self.storage_path / f"{experiment.id}.json"
        with open(exp_file, "w") as f:
            json.dump(experiment.to_dict(), f, indent=2)
    
    def create_experiment(
        self,
        name: str,
        config: RLConfig,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> RLExperiment:
        """
        Create a new RL experiment.
        
        Args:
            name: Experiment name
            config: RL configuration
            description: Optional description
            tags: Optional tags
        
        Returns:
            Created RLExperiment
        """
        experiment_id = f"rl-exp-{uuid.uuid4().hex[:8]}"
        
        experiment = RLExperiment(
            id=experiment_id,
            name=name,
            method=config.method,
            config=config.model_dump() if hasattr(config, 'model_dump') else {},
            base_model=config.base_model,
            preference_dataset_id=config.preference_dataset_id,
            prompt_dataset_id=config.prompt_dataset_id,
            description=description,
            tags=tags or config.tags,
        )
        
        self._experiments[experiment_id] = experiment
        self._save_experiment(experiment)
        
        logger.info(f"Created RL experiment {name} with ID {experiment_id}")
        return experiment
    
    def get_experiment(self, experiment_id: str) -> Optional[RLExperiment]:
        """Get an experiment by ID."""
        return self._experiments.get(experiment_id)
    
    def list_experiments(
        self,
        status: Optional[RLExperimentStatus] = None,
        method: Optional[RLMethod] = None,
        limit: int = 100,
    ) -> List[RLExperiment]:
        """
        List experiments with optional filters.
        
        Args:
            status: Filter by status
            method: Filter by RL method
            limit: Maximum experiments to return
        
        Returns:
            List of experiments
        """
        experiments = list(self._experiments.values())
        
        if status:
            experiments = [e for e in experiments if e.status == status]
        
        if method:
            experiments = [e for e in experiments if e.method == method]
        
        # Sort by created_at (newest first)
        experiments.sort(key=lambda e: e.created_at, reverse=True)
        
        return experiments[:limit]
    
    def update_experiment(
        self,
        experiment_id: str,
        status: Optional[RLExperimentStatus] = None,
        metrics: Optional[Dict[str, float]] = None,
        output_model_id: Optional[str] = None,
        reward_model_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[RLExperiment]:
        """Update an experiment."""
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            return None
        
        if status:
            experiment.status = status
            if status == RLExperimentStatus.RUNNING:
                experiment.started_at = datetime.utcnow().isoformat()
            elif status in [RLExperimentStatus.COMPLETED, RLExperimentStatus.FAILED]:
                experiment.completed_at = datetime.utcnow().isoformat()
        
        if metrics:
            experiment.update_metrics(metrics)
        
        if output_model_id:
            experiment.output_model_id = output_model_id
        
        if reward_model_id:
            experiment.reward_model_id = reward_model_id
        
        if error_message:
            experiment.error_message = error_message
        
        self._save_experiment(experiment)
        return experiment
    
    def delete_experiment(self, experiment_id: str) -> bool:
        """Delete an experiment."""
        if experiment_id not in self._experiments:
            return False
        
        experiment = self._experiments.pop(experiment_id)
        
        # Remove file
        exp_file = self.storage_path / f"{experiment_id}.json"
        if exp_file.exists():
            exp_file.unlink()
        
        return True
    
    def get_experiment_logs(
        self,
        experiment_id: str,
        tail: int = 100,
    ) -> List[str]:
        """Get experiment logs."""
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            return []
        return experiment.logs[-tail:]
    
    def add_experiment_log(
        self,
        experiment_id: str,
        message: str,
    ) -> bool:
        """Add a log message to an experiment."""
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            return False
        
        experiment.add_log(message)
        self._save_experiment(experiment)
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get experiment statistics."""
        experiments = list(self._experiments.values())
        
        stats = {
            "total_experiments": len(experiments),
            "by_status": {
                status.value: len([e for e in experiments if e.status == status])
                for status in RLExperimentStatus
            },
            "by_method": {
                method.value: len([e for e in experiments if e.method == method])
                for method in RLMethod
            },
        }
        
        return stats
    
    def compare_experiments(
        self,
        experiment_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Compare multiple experiments.
        
        Args:
            experiment_ids: Experiments to compare
        
        Returns:
            Comparison data
        """
        experiments = []
        all_metrics = set()
        
        for exp_id in experiment_ids:
            exp = self._experiments.get(exp_id)
            if exp:
                experiments.append(exp)
                all_metrics.update(exp.metrics.keys())
        
        comparison = {
            "experiments": [
                {
                    "id": e.id,
                    "name": e.name,
                    "method": e.method.value,
                    "status": e.status.value,
                    "metrics": e.metrics,
                }
                for e in experiments
            ],
            "metrics_comparison": {
                metric: [e.metrics.get(metric) for e in experiments]
                for metric in all_metrics
            },
        }
        
        return comparison
