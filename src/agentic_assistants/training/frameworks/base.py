"""
Base training framework adapter.

This module defines the abstract base class for training framework adapters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.training.config import TrainingConfig


@dataclass
class TrainingResult:
    """Result of a training run."""
    
    success: bool
    model_path: Optional[str] = None
    error: Optional[str] = None
    
    # Final metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Checkpoints
    checkpoints: List[str] = field(default_factory=list)
    
    # Training info
    total_steps: int = 0
    total_epochs: float = 0
    training_time_seconds: float = 0
    
    # Resource usage
    peak_memory_mb: Optional[float] = None
    gpu_utilization: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "model_path": self.model_path,
            "error": self.error,
            "metrics": self.metrics,
            "checkpoints": self.checkpoints,
            "total_steps": self.total_steps,
            "total_epochs": self.total_epochs,
            "training_time_seconds": self.training_time_seconds,
            "peak_memory_mb": self.peak_memory_mb,
            "gpu_utilization": self.gpu_utilization,
        }


class BaseTrainingFramework(ABC):
    """
    Abstract base class for training framework adapters.
    
    Training frameworks (Llama Factory, Unsloth, Axolotl) are wrapped with
    this adapter pattern to provide a consistent interface for training jobs.
    
    Subclasses must implement:
    - train(): Main training method
    - validate_config(): Config validation
    - get_capabilities(): Framework capabilities
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Framework name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Framework version."""
        pass
    
    @abstractmethod
    async def train(
        self,
        config: TrainingConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> TrainingResult:
        """
        Run training with the given configuration.
        
        Args:
            config: Training configuration
            metrics_callback: Optional callback for streaming metrics updates
        
        Returns:
            TrainingResult with model path and metrics
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: TrainingConfig) -> List[str]:
        """
        Validate training configuration.
        
        Args:
            config: Training configuration to validate
        
        Returns:
            List of validation error messages (empty if valid)
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get framework capabilities.
        
        Returns:
            Dictionary of capability flags and supported features
        """
        pass
    
    def prepare_dataset(
        self,
        config: TrainingConfig,
    ) -> str:
        """
        Prepare dataset for training.
        
        Args:
            config: Training configuration
        
        Returns:
            Path to prepared dataset
        """
        # Default implementation - subclasses can override
        return config.dataset_id
    
    def cleanup(self, config: TrainingConfig) -> None:
        """
        Cleanup after training.
        
        Args:
            config: Training configuration
        """
        # Default implementation - subclasses can override
        pass
    
    @abstractmethod
    def estimate_resources(
        self,
        config: TrainingConfig,
    ) -> Dict[str, Any]:
        """
        Estimate resource requirements for training.
        
        Args:
            config: Training configuration
        
        Returns:
            Dictionary with estimated GPU memory, time, etc.
        """
        pass
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values for this framework.
        
        Returns:
            Dictionary of default config values
        """
        return {}
    
    def is_available(self) -> bool:
        """
        Check if the framework is available/installed.
        
        Returns:
            True if framework can be used
        """
        return True
