"""
Abstract training lifecycle for the Agentic Assistants framework.

Provides base classes for model training with checkpointing, early stopping,
metric accumulation, and extensible callbacks. Inspired by the BaseTrainer
pattern described in "Architectural Foundations for Agentic Data and MLOps
Platforms".

Usage:
    >>> class MyTrainer(BaseTrainer):
    ...     def _train_epoch(self, epoch: int) -> dict[str, float]:
    ...         return {"loss": 0.5}
    ...     def _valid_epoch(self, epoch: int) -> dict[str, float]:
    ...         return {"val_loss": 0.4}
    >>> trainer = MyTrainer(TrainingConfig(epochs=10))
    >>> trainer.train()
"""

from __future__ import annotations

import json
import logging
import math
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Literal, Optional, Protocol, runtime_checkable

from pydantic import Field

from agentic_assistants.core.base_models import AgenticBaseModel

logger = logging.getLogger(__name__)


class TrainingConfig(AgenticBaseModel):
    """Configuration for a training run."""

    epochs: int = Field(default=10, ge=1)
    learning_rate: float = Field(default=1e-3, gt=0)
    batch_size: int = Field(default=32, ge=1)
    device: str = "cpu"
    checkpoint_dir: str = "./checkpoints"
    save_every: int = Field(default=1, ge=1, description="Save checkpoint every N epochs")
    log_every: int = Field(default=1, ge=1, description="Log metrics every N epochs")
    early_stopping_patience: int = Field(default=0, ge=0, description="0 disables early stopping")
    early_stopping_delta: float = Field(default=0.0, ge=0)
    early_stopping_metric: str = "val_loss"
    early_stopping_mode: Literal["min", "max"] = "min"
    resume_from: Optional[str] = None
    metric_modes: dict[str, Literal["min", "max"]] = Field(
        default_factory=dict,
        description="Per-metric direction: 'min' means lower is better, 'max' means higher.",
    )


class TrainingMetrics(AgenticBaseModel):
    """Accumulates per-epoch metrics with mode-aware best tracking."""

    history: dict[str, list[float]] = Field(default_factory=dict)
    best_values: dict[str, float] = Field(default_factory=dict)
    best_epochs: dict[str, int] = Field(default_factory=dict)
    metric_modes: dict[str, Literal["min", "max"]] = Field(default_factory=dict)
    total_epochs: int = 0
    total_time_seconds: float = 0.0

    def _is_better(self, key: str, value: float, prev_best: float) -> bool:
        mode = self.metric_modes.get(key, "min")
        if mode == "max":
            return value > prev_best
        return value < prev_best

    def record(self, epoch: int, metrics: dict[str, float]) -> None:
        for key, value in metrics.items():
            if key not in self.history:
                self.history[key] = []
            self.history[key].append(value)

            prev_best = self.best_values.get(key)
            if prev_best is None or self._is_better(key, value, prev_best):
                self.best_values[key] = value
                self.best_epochs[key] = epoch
        self.total_epochs = epoch

    def get_last(self, metric: str) -> Optional[float]:
        values = self.history.get(metric)
        return values[-1] if values else None

    def summary(self) -> dict[str, Any]:
        return {
            "total_epochs": self.total_epochs,
            "total_time_seconds": round(self.total_time_seconds, 2),
            "best_values": self.best_values,
            "best_epochs": self.best_epochs,
        }


class EarlyStopping:
    """Monitors a metric and signals when training should stop."""

    def __init__(
        self,
        patience: int = 5,
        delta: float = 0.0,
        mode: Literal["min", "max"] = "min",
    ) -> None:
        self.patience = patience
        self.delta = delta
        self.mode = mode
        self.best: Optional[float] = None
        self.counter: int = 0
        self.should_stop: bool = False

    def _is_improvement(self, current: float) -> bool:
        if self.best is None:
            return True
        if self.mode == "min":
            return current < self.best - self.delta
        return current > self.best + self.delta

    def step(self, value: float) -> bool:
        if self._is_improvement(value):
            self.best = value
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
        return self.should_stop

    def reset(self) -> None:
        self.best = None
        self.counter = 0
        self.should_stop = False


class CheckpointManager:
    """Handles saving and loading training checkpoints (JSON and torch)."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, epoch: int, state: dict[str, Any]) -> Path:
        path = self.directory / f"checkpoint_epoch_{epoch:04d}.json"
        payload = {"epoch": epoch, "state": state}
        path.write_text(json.dumps(payload, indent=2, default=str))
        logger.info("Saved checkpoint to %s", path)
        return path

    def load(self, path: str | Path) -> dict[str, Any]:
        data = json.loads(Path(path).read_text())
        logger.info("Loaded checkpoint from %s (epoch %d)", path, data.get("epoch", -1))
        return data

    def save_torch(self, epoch: int, state_dict: Any) -> Path:
        """Save a PyTorch state_dict checkpoint (falls back to JSON on import error)."""
        try:
            import torch
            path = self.directory / f"checkpoint_epoch_{epoch:04d}.pt"
            torch.save({"epoch": epoch, "state_dict": state_dict}, path)
            logger.info("Saved torch checkpoint to %s", path)
            return path
        except ImportError:
            logger.warning("torch not available, falling back to JSON checkpoint")
            return self.save(epoch, {"epoch": epoch, "note": "torch_unavailable"})

    def load_torch(self, path: str | Path) -> dict[str, Any]:
        """Load a PyTorch checkpoint."""
        import torch
        data = torch.load(Path(path), map_location="cpu", weights_only=False)
        logger.info("Loaded torch checkpoint from %s (epoch %d)", path, data.get("epoch", -1))
        return data

    def latest(self, suffix: str = ".json") -> Optional[Path]:
        checkpoints = sorted(self.directory.glob(f"checkpoint_epoch_*{suffix}"))
        return checkpoints[-1] if checkpoints else None

    def cleanup(self, keep_last: int = 3, suffix: str = ".json") -> list[Path]:
        checkpoints = sorted(self.directory.glob(f"checkpoint_epoch_*{suffix}"))
        removed: list[Path] = []
        for cp in checkpoints[:-keep_last] if len(checkpoints) > keep_last else []:
            cp.unlink()
            removed.append(cp)
        return removed


# ---------------------------------------------------------------------------
# Callback system
# ---------------------------------------------------------------------------


@runtime_checkable
class TrainerCallback(Protocol):
    """Protocol for training loop callbacks."""

    def on_train_begin(self, config: TrainingConfig) -> None: ...
    def on_train_end(self, metrics: TrainingMetrics) -> None: ...
    def on_epoch_end(self, epoch: int, metrics: dict[str, float]) -> None: ...
    def on_checkpoint(self, epoch: int, path: Path) -> None: ...
    def on_early_stop(self, epoch: int, metric_value: float) -> None: ...


class CallbackList:
    """Manages a list of ``TrainerCallback`` instances, dispatching events."""

    def __init__(self, callbacks: Optional[list[TrainerCallback]] = None) -> None:
        self._callbacks: list[TrainerCallback] = list(callbacks or [])

    def add(self, cb: TrainerCallback) -> None:
        self._callbacks.append(cb)

    def on_train_begin(self, config: TrainingConfig) -> None:
        for cb in self._callbacks:
            cb.on_train_begin(config)

    def on_train_end(self, metrics: TrainingMetrics) -> None:
        for cb in self._callbacks:
            cb.on_train_end(metrics)

    def on_epoch_end(self, epoch: int, metrics: dict[str, float]) -> None:
        for cb in self._callbacks:
            cb.on_epoch_end(epoch, metrics)

    def on_checkpoint(self, epoch: int, path: Path) -> None:
        for cb in self._callbacks:
            cb.on_checkpoint(epoch, path)

    def on_early_stop(self, epoch: int, metric_value: float) -> None:
        for cb in self._callbacks:
            cb.on_early_stop(epoch, metric_value)


class BaseTrainer(ABC):
    """Abstract base class for training loops.

    Subclasses must implement ``_train_epoch`` and ``_valid_epoch``.
    The base class handles the outer loop, early stopping, checkpointing,
    logging, and callback dispatch.
    """

    def __init__(
        self,
        config: TrainingConfig,
        callbacks: Optional[list[TrainerCallback]] = None,
    ) -> None:
        self.config = config
        self.metrics = TrainingMetrics(metric_modes=config.metric_modes)
        self.checkpointer = CheckpointManager(config.checkpoint_dir)
        self.callbacks = CallbackList(callbacks)
        self._early_stopping: Optional[EarlyStopping] = None
        if config.early_stopping_patience > 0:
            self._early_stopping = EarlyStopping(
                patience=config.early_stopping_patience,
                delta=config.early_stopping_delta,
                mode=config.early_stopping_mode,
            )
        self._start_epoch = 1

    @abstractmethod
    def _train_epoch(self, epoch: int) -> dict[str, float]:
        """Run one training epoch. Return a dict of metric_name -> value."""

    @abstractmethod
    def _valid_epoch(self, epoch: int) -> dict[str, float]:
        """Run one validation epoch. Return a dict of metric_name -> value."""

    def on_train_begin(self) -> None:
        """Hook called before the training loop starts."""

    def on_train_end(self) -> None:
        """Hook called after the training loop finishes."""

    def on_epoch_begin(self, epoch: int) -> None:
        """Hook called at the start of each epoch."""

    def on_epoch_end(self, epoch: int, metrics: dict[str, float]) -> None:
        """Hook called at the end of each epoch with combined metrics."""

    def get_state(self) -> dict[str, Any]:
        """Return serializable state for checkpointing. Override to add model weights etc."""
        return {"config": self.config.to_dict(), "metrics": self.metrics.to_dict()}

    def load_state(self, state: dict[str, Any]) -> None:
        """Restore state from a checkpoint. Override to load model weights etc."""

    def train(self) -> TrainingMetrics:
        if self.config.resume_from:
            data = self.checkpointer.load(self.config.resume_from)
            self._start_epoch = data["epoch"] + 1
            self.load_state(data.get("state", {}))
            logger.info("Resuming from epoch %d", self._start_epoch)

        self.on_train_begin()
        self.callbacks.on_train_begin(self.config)
        t0 = time.perf_counter()

        for epoch in range(self._start_epoch, self.config.epochs + 1):
            self.on_epoch_begin(epoch)

            train_metrics = self._train_epoch(epoch)
            val_metrics = self._valid_epoch(epoch)
            combined = {**train_metrics, **val_metrics}
            self.metrics.record(epoch, combined)

            if epoch % self.config.log_every == 0:
                logger.info("Epoch %d: %s", epoch, combined)

            if epoch % self.config.save_every == 0:
                cp_path = self.checkpointer.save(epoch, self.get_state())
                self.callbacks.on_checkpoint(epoch, cp_path)

            self.on_epoch_end(epoch, combined)
            self.callbacks.on_epoch_end(epoch, combined)

            if self._early_stopping:
                metric_val = combined.get(self.config.early_stopping_metric)
                if metric_val is not None and not math.isnan(metric_val):
                    if self._early_stopping.step(metric_val):
                        logger.info("Early stopping at epoch %d", epoch)
                        self.callbacks.on_early_stop(epoch, metric_val)
                        break

        self.metrics.total_time_seconds = time.perf_counter() - t0
        self.on_train_end()
        self.callbacks.on_train_end(self.metrics)
        return self.metrics


__all__ = [
    "TrainingConfig",
    "TrainingMetrics",
    "EarlyStopping",
    "CheckpointManager",
    "TrainerCallback",
    "CallbackList",
    "BaseTrainer",
]
