"""
Base RL adapter class.

Defines the interface for RL framework adapters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.rl.config import RLConfig, RLMethod


@dataclass
class RLTrainingResult:
    """Result of an RL training run."""
    
    success: bool
    model_path: Optional[str] = None
    error: Optional[str] = None
    
    # Method used
    method: Optional[RLMethod] = None
    
    # Metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Training details
    total_steps: int = 0
    total_episodes: int = 0
    training_time_seconds: float = 0.0
    
    # Reward model metrics (if applicable)
    reward_model_path: Optional[str] = None
    reward_model_accuracy: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "model_path": self.model_path,
            "error": self.error,
            "method": self.method.value if self.method else None,
            "metrics": self.metrics,
            "total_steps": self.total_steps,
            "total_episodes": self.total_episodes,
            "training_time_seconds": self.training_time_seconds,
            "reward_model_path": self.reward_model_path,
            "reward_model_accuracy": self.reward_model_accuracy,
        }


class BaseRLAdapter(ABC):
    """
    Abstract base class for RL framework adapters.
    
    RL frameworks (TRL, Ray RLlib) are wrapped with this adapter pattern
    to provide a consistent interface for RL training.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Adapter name."""
        pass
    
    @property
    @abstractmethod
    def supported_methods(self) -> List[RLMethod]:
        """List of supported RL methods."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the framework is available."""
        pass
    
    @abstractmethod
    async def train_dpo(
        self,
        config: RLConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """
        Train using Direct Preference Optimization.
        
        Args:
            config: RL configuration
            metrics_callback: Optional callback for metrics
        
        Returns:
            RLTrainingResult
        """
        pass
    
    @abstractmethod
    async def train_ppo(
        self,
        config: RLConfig,
        reward_model_path: str,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """
        Train using PPO with a reward model.
        
        Args:
            config: RL configuration
            reward_model_path: Path to reward model
            metrics_callback: Optional callback for metrics
        
        Returns:
            RLTrainingResult
        """
        pass
    
    @abstractmethod
    async def train_reward_model(
        self,
        config: RLConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """
        Train a reward model.
        
        Args:
            config: RL configuration
            metrics_callback: Optional callback for metrics
        
        Returns:
            RLTrainingResult
        """
        pass
    
    def validate_config(self, config: RLConfig) -> List[str]:
        """
        Validate RL configuration.
        
        Args:
            config: Configuration to validate
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not config.base_model:
            errors.append("base_model is required")
        
        if not config.output_name:
            errors.append("output_name is required")
        
        if not config.preference_dataset_id:
            errors.append("preference_dataset_id is required")
        
        if config.method not in self.supported_methods:
            errors.append(f"Method {config.method} not supported by {self.name}")
        
        return errors
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get adapter capabilities."""
        return {
            "name": self.name,
            "available": self.is_available(),
            "supported_methods": [m.value for m in self.supported_methods],
        }
