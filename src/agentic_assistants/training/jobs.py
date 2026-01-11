"""
Training job management.

This module provides classes for creating, tracking, and managing training jobs.
"""

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from agentic_assistants.training.config import TrainingConfig, CustomModelInfo, TrainingMethod
from agentic_assistants.utils.logging import get_logger

if TYPE_CHECKING:
    from agentic_assistants.training.frameworks.base import BaseTrainingFramework

logger = get_logger(__name__)


class TrainingJobStatus(str, Enum):
    """Training job status."""
    PENDING = "pending"
    QUEUED = "queued"
    PREPARING = "preparing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TrainingMetrics:
    """Training metrics collected during training."""
    
    loss: Optional[float] = None
    eval_loss: Optional[float] = None
    learning_rate: Optional[float] = None
    epoch: Optional[float] = None
    step: int = 0
    total_steps: int = 0
    samples_per_second: Optional[float] = None
    
    # Additional metrics
    train_runtime: Optional[float] = None
    train_samples_per_second: Optional[float] = None
    total_flos: Optional[float] = None
    
    # Custom metrics
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "loss": self.loss,
            "eval_loss": self.eval_loss,
            "learning_rate": self.learning_rate,
            "epoch": self.epoch,
            "step": self.step,
            "total_steps": self.total_steps,
            "samples_per_second": self.samples_per_second,
            "train_runtime": self.train_runtime,
            "train_samples_per_second": self.train_samples_per_second,
            "total_flos": self.total_flos,
            **self.custom_metrics,
        }
    
    @property
    def progress(self) -> float:
        """Calculate training progress as percentage."""
        if self.total_steps == 0:
            return 0.0
        return min(100.0, (self.step / self.total_steps) * 100)


@dataclass
class TrainingJob:
    """
    Represents a training job.
    
    A training job encapsulates all information needed to train a model,
    including configuration, status, metrics, and logs.
    """
    
    id: str
    config: TrainingConfig
    status: TrainingJobStatus = TrainingJobStatus.PENDING
    
    # Timing
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # Progress and metrics
    progress: float = 0.0
    metrics: TrainingMetrics = field(default_factory=TrainingMetrics)
    
    # Logs
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    
    # Output
    output_model_path: Optional[str] = None
    output_model_id: Optional[str] = None
    
    # MLFlow tracking
    mlflow_run_id: Optional[str] = None
    mlflow_experiment_id: Optional[str] = None
    
    # Framework
    framework: str = "llama_factory"
    
    # Process tracking
    _process_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "config": self.config.model_dump() if hasattr(self.config, 'model_dump') else dict(self.config),
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "progress": self.progress,
            "metrics": self.metrics.to_dict(),
            "logs": self.logs[-100:],  # Keep last 100 log lines
            "error_message": self.error_message,
            "output_model_path": self.output_model_path,
            "output_model_id": self.output_model_id,
            "mlflow_run_id": self.mlflow_run_id,
            "mlflow_experiment_id": self.mlflow_experiment_id,
            "framework": self.framework,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainingJob":
        """Create from dictionary."""
        config_data = data.get("config", {})
        config = TrainingConfig(**config_data)
        
        metrics_data = data.get("metrics", {})
        metrics = TrainingMetrics(
            loss=metrics_data.get("loss"),
            eval_loss=metrics_data.get("eval_loss"),
            learning_rate=metrics_data.get("learning_rate"),
            epoch=metrics_data.get("epoch"),
            step=metrics_data.get("step", 0),
            total_steps=metrics_data.get("total_steps", 0),
        )
        
        return cls(
            id=data["id"],
            config=config,
            status=TrainingJobStatus(data.get("status", "pending")),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            progress=data.get("progress", 0.0),
            metrics=metrics,
            logs=data.get("logs", []),
            error_message=data.get("error_message"),
            output_model_path=data.get("output_model_path"),
            output_model_id=data.get("output_model_id"),
            mlflow_run_id=data.get("mlflow_run_id"),
            mlflow_experiment_id=data.get("mlflow_experiment_id"),
            framework=data.get("framework", "llama_factory"),
        )
    
    def add_log(self, message: str) -> None:
        """Add a log message."""
        timestamp = datetime.utcnow().isoformat()
        self.logs.append(f"[{timestamp}] {message}")
    
    def update_metrics(self, **kwargs) -> None:
        """Update training metrics."""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)
            else:
                self.metrics.custom_metrics[key] = value
        
        # Update progress
        self.progress = self.metrics.progress


class TrainingJobManager:
    """
    Manager for training jobs.
    
    Handles job creation, queuing, execution, and status tracking.
    Integrates with training frameworks and MLFlow for experiment tracking.
    """
    
    def __init__(
        self,
        jobs_dir: Optional[str] = None,
        max_concurrent_jobs: int = 1,
    ):
        """
        Initialize the job manager.
        
        Args:
            jobs_dir: Directory to store job state files
            max_concurrent_jobs: Maximum concurrent training jobs
        """
        self.jobs_dir = Path(jobs_dir or "./data/training/jobs")
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_concurrent_jobs = max_concurrent_jobs
        self._jobs: Dict[str, TrainingJob] = {}
        self._running_jobs: Dict[str, asyncio.Task] = {}
        self._frameworks: Dict[str, "BaseTrainingFramework"] = {}
        self._callbacks: List[Callable[[TrainingJob], None]] = []
        
        # Load existing jobs
        self._load_jobs()
    
    def _load_jobs(self) -> None:
        """Load jobs from disk."""
        for job_file in self.jobs_dir.glob("*.json"):
            try:
                with open(job_file, "r") as f:
                    data = json.load(f)
                job = TrainingJob.from_dict(data)
                self._jobs[job.id] = job
            except Exception as e:
                logger.warning(f"Failed to load job from {job_file}: {e}")
    
    def _save_job(self, job: TrainingJob) -> None:
        """Save job state to disk."""
        job_file = self.jobs_dir / f"{job.id}.json"
        with open(job_file, "w") as f:
            json.dump(job.to_dict(), f, indent=2)
    
    def register_framework(self, name: str, framework: "BaseTrainingFramework") -> None:
        """Register a training framework adapter."""
        self._frameworks[name] = framework
    
    def add_callback(self, callback: Callable[[TrainingJob], None]) -> None:
        """Add a callback for job status changes."""
        self._callbacks.append(callback)
    
    def _notify_callbacks(self, job: TrainingJob) -> None:
        """Notify all callbacks of job update."""
        for callback in self._callbacks:
            try:
                callback(job)
            except Exception as e:
                logger.warning(f"Callback error: {e}")
    
    def create_job(
        self,
        config: TrainingConfig,
        framework: Optional[str] = None,
    ) -> TrainingJob:
        """
        Create a new training job.
        
        Args:
            config: Training configuration
            framework: Framework to use (default: config.framework)
        
        Returns:
            Created TrainingJob
        """
        job_id = str(uuid.uuid4())
        
        # Set output directory if not specified
        if not config.output_dir:
            config.output_dir = str(self.jobs_dir.parent / "outputs" / job_id)
        
        job = TrainingJob(
            id=job_id,
            config=config,
            framework=framework or config.framework,
        )
        
        self._jobs[job_id] = job
        self._save_job(job)
        
        logger.info(f"Created training job {job_id} for {config.output_name}")
        return job
    
    def get_job(self, job_id: str) -> Optional[TrainingJob]:
        """Get a job by ID."""
        return self._jobs.get(job_id)
    
    def list_jobs(
        self,
        status: Optional[TrainingJobStatus] = None,
        limit: int = 100,
    ) -> List[TrainingJob]:
        """
        List training jobs.
        
        Args:
            status: Filter by status
            limit: Maximum number of jobs to return
        
        Returns:
            List of TrainingJob instances
        """
        jobs = list(self._jobs.values())
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        
        return jobs[:limit]
    
    async def start_job(self, job_id: str) -> bool:
        """
        Start a training job.
        
        Args:
            job_id: Job ID to start
        
        Returns:
            True if job started successfully
        """
        job = self._jobs.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return False
        
        if job.status not in [TrainingJobStatus.PENDING, TrainingJobStatus.PAUSED]:
            logger.warning(f"Job {job_id} cannot be started (status: {job.status})")
            return False
        
        # Check concurrent job limit
        running_count = len([
            j for j in self._jobs.values() 
            if j.status == TrainingJobStatus.RUNNING
        ])
        if running_count >= self.max_concurrent_jobs:
            job.status = TrainingJobStatus.QUEUED
            job.add_log("Job queued - waiting for available slot")
            self._save_job(job)
            return True
        
        # Get framework
        framework = self._frameworks.get(job.framework)
        if not framework:
            job.status = TrainingJobStatus.FAILED
            job.error_message = f"Framework {job.framework} not registered"
            job.add_log(f"Error: {job.error_message}")
            self._save_job(job)
            return False
        
        # Start training
        job.status = TrainingJobStatus.PREPARING
        job.started_at = datetime.utcnow().isoformat()
        job.add_log("Starting training job")
        self._save_job(job)
        
        # Run training in background task
        task = asyncio.create_task(self._run_training(job, framework))
        self._running_jobs[job_id] = task
        
        return True
    
    async def _run_training(
        self,
        job: TrainingJob,
        framework: "BaseTrainingFramework",
    ) -> None:
        """Run training in background."""
        try:
            job.status = TrainingJobStatus.RUNNING
            job.add_log("Training started")
            self._save_job(job)
            self._notify_callbacks(job)
            
            # Define metrics callback
            def metrics_callback(metrics: Dict[str, Any]) -> None:
                job.update_metrics(**metrics)
                self._save_job(job)
                self._notify_callbacks(job)
            
            # Run training
            result = await framework.train(job.config, metrics_callback)
            
            if result.success:
                job.status = TrainingJobStatus.COMPLETED
                job.output_model_path = result.model_path
                job.add_log(f"Training completed. Model saved to {result.model_path}")
                
                # Update final metrics
                if result.metrics:
                    job.update_metrics(**result.metrics)
            else:
                job.status = TrainingJobStatus.FAILED
                job.error_message = result.error
                job.add_log(f"Training failed: {result.error}")
            
        except asyncio.CancelledError:
            job.status = TrainingJobStatus.CANCELLED
            job.add_log("Training cancelled by user")
        except Exception as e:
            job.status = TrainingJobStatus.FAILED
            job.error_message = str(e)
            job.add_log(f"Training error: {e}")
            logger.exception(f"Training job {job.id} failed")
        finally:
            job.completed_at = datetime.utcnow().isoformat()
            job.progress = 100.0 if job.status == TrainingJobStatus.COMPLETED else job.progress
            self._save_job(job)
            self._notify_callbacks(job)
            
            # Remove from running jobs
            self._running_jobs.pop(job.id, None)
            
            # Check for queued jobs
            await self._process_queue()
    
    async def _process_queue(self) -> None:
        """Process queued jobs."""
        queued_jobs = [
            j for j in self._jobs.values() 
            if j.status == TrainingJobStatus.QUEUED
        ]
        
        for job in sorted(queued_jobs, key=lambda j: j.created_at):
            running_count = len([
                j for j in self._jobs.values() 
                if j.status == TrainingJobStatus.RUNNING
            ])
            if running_count < self.max_concurrent_jobs:
                await self.start_job(job.id)
            else:
                break
    
    async def stop_job(self, job_id: str) -> bool:
        """
        Stop a running training job.
        
        Args:
            job_id: Job ID to stop
        
        Returns:
            True if job was stopped
        """
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        if job_id in self._running_jobs:
            task = self._running_jobs[job_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            return True
        
        if job.status == TrainingJobStatus.QUEUED:
            job.status = TrainingJobStatus.CANCELLED
            job.add_log("Job cancelled while queued")
            self._save_job(job)
            return True
        
        return False
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a training job.
        
        Args:
            job_id: Job ID to delete
        
        Returns:
            True if job was deleted
        """
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        if job.status == TrainingJobStatus.RUNNING:
            logger.warning(f"Cannot delete running job {job_id}")
            return False
        
        # Remove job file
        job_file = self.jobs_dir / f"{job_id}.json"
        if job_file.exists():
            job_file.unlink()
        
        # Remove from memory
        del self._jobs[job_id]
        
        return True
    
    def get_job_logs(self, job_id: str, tail: int = 100) -> List[str]:
        """Get job logs."""
        job = self._jobs.get(job_id)
        if not job:
            return []
        return job.logs[-tail:]
