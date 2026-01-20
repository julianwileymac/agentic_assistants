"""
Base classes for flow nodes.

This module provides abstract base classes for all flow nodes,
ensuring consistent interfaces for execution, configuration,
and observability (including RL metric emission).

Example:
    >>> from agentic_assistants.pipelines.nodes import BaseFlowNode
    >>> 
    >>> class MyCustomNode(BaseFlowNode):
    ...     node_type = "my_custom"
    ...     
    ...     def execute(self, inputs: dict) -> dict:
    ...         result = self.process(inputs["data"])
    ...         self.emit_rl_metric("quality_score", 0.95)
    ...         return {"output": result}
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class NodeConfig:
    """Base configuration for flow nodes."""
    
    # Unique identifier for this node instance
    node_id: str = ""
    
    # Human-readable label
    label: str = ""
    
    # Optional description
    description: str = ""
    
    # Whether to emit execution metrics
    emit_metrics: bool = True
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeExecutionResult:
    """Result of node execution."""
    
    success: bool
    outputs: Dict[str, Any]
    duration_ms: float
    metrics: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "outputs": self.outputs,
            "duration_ms": self.duration_ms,
            "metrics": self.metrics,
            "error_message": self.error_message,
        }


class BaseFlowNode(ABC):
    """
    Abstract base class for all flow nodes.
    
    This class provides:
    - Standardized execution interface
    - Configuration schema generation
    - RL metric emission support
    - Execution timing and logging
    - Error handling
    
    Attributes:
        node_type: String identifier for the node type
        config: Node configuration instance
        _metrics: Collected metrics during execution
        _ml_tracker: Optional MLFlow tracker for logging
    """
    
    # Override in subclasses
    node_type: str = "base"
    
    # Config class to use (override in subclasses)
    config_class: Type[NodeConfig] = NodeConfig
    
    def __init__(
        self,
        config: Optional[NodeConfig] = None,
        ml_tracker: Optional[Any] = None,
    ):
        """
        Initialize the node.
        
        Args:
            config: Node configuration. If None, uses defaults.
            ml_tracker: Optional MLFlow tracker for metric logging.
        """
        self.config = config or self.config_class()
        self._ml_tracker = ml_tracker
        self._metrics: Dict[str, float] = {}
        self._execution_count = 0
    
    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node logic.
        
        This method should be implemented by subclasses to perform
        the actual node operation.
        
        Args:
            inputs: Dictionary of input values keyed by input name
            
        Returns:
            Dictionary of output values keyed by output name
            
        Raises:
            Exception: If execution fails
        """
        pass
    
    def run(self, inputs: Dict[str, Any]) -> NodeExecutionResult:
        """
        Run the node with full observability.
        
        This method wraps execute() with timing, error handling,
        and metric collection.
        
        Args:
            inputs: Dictionary of input values
            
        Returns:
            NodeExecutionResult with outputs and metrics
        """
        self._metrics = {}
        self._execution_count += 1
        start_time = time.time()
        
        try:
            logger.debug(f"Executing node {self.config.label or self.node_type}")
            outputs = self.execute(inputs)
            duration_ms = (time.time() - start_time) * 1000
            
            # Record execution metric
            self._metrics["execution_time_ms"] = duration_ms
            
            # Log to MLFlow if available
            if self._ml_tracker and self.config.emit_metrics:
                self._log_metrics_to_mlflow()
            
            return NodeExecutionResult(
                success=True,
                outputs=outputs,
                duration_ms=duration_ms,
                metrics=self._metrics.copy(),
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Node {self.node_type} execution failed: {e}")
            
            return NodeExecutionResult(
                success=False,
                outputs={},
                duration_ms=duration_ms,
                metrics=self._metrics.copy(),
                error_message=str(e),
            )
    
    def emit_rl_metric(self, metric_name: str, value: float) -> None:
        """
        Emit a metric for reinforcement learning optimization.
        
        These metrics can be used to train reward models or
        for direct policy optimization.
        
        Args:
            metric_name: Name of the metric (e.g., "response_quality")
            value: Metric value (typically normalized 0-1 or score)
        """
        full_name = f"rl/{self.node_type}/{metric_name}"
        self._metrics[full_name] = value
        logger.debug(f"RL metric emitted: {full_name} = {value}")
        
        # Log immediately to MLFlow if available
        if self._ml_tracker:
            try:
                self._ml_tracker.log_metric(full_name, value)
            except Exception as e:
                logger.warning(f"Failed to log RL metric to MLFlow: {e}")
    
    def emit_metric(self, metric_name: str, value: float) -> None:
        """
        Emit a general execution metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        self._metrics[metric_name] = value
    
    def _log_metrics_to_mlflow(self) -> None:
        """Log collected metrics to MLFlow."""
        if not self._ml_tracker:
            return
        
        try:
            for name, value in self._metrics.items():
                self._ml_tracker.log_metric(name, value)
        except Exception as e:
            logger.warning(f"Failed to log metrics to MLFlow: {e}")
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for node configuration.
        
        Returns:
            JSON schema dictionary describing the configuration fields
        """
        # Base schema from NodeConfig
        schema = {
            "type": "object",
            "properties": {
                "node_id": {"type": "string", "description": "Unique node identifier"},
                "label": {"type": "string", "description": "Human-readable label"},
                "description": {"type": "string", "description": "Node description"},
                "emit_metrics": {"type": "boolean", "default": True},
            },
            "required": [],
        }
        return schema
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for node inputs.
        
        Override in subclasses to define expected inputs.
        
        Returns:
            JSON schema dictionary describing the input fields
        """
        return {"type": "object", "properties": {}}
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for node outputs.
        
        Override in subclasses to define expected outputs.
        
        Returns:
            JSON schema dictionary describing the output fields
        """
        return {"type": "object", "properties": {}}
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> List[str]:
        """
        Validate input data against schema.
        
        Args:
            inputs: Input dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        # Basic validation - subclasses can override for specific checks
        errors = []
        schema = self.get_input_schema()
        required = schema.get("required", [])
        
        for field in required:
            if field not in inputs:
                errors.append(f"Missing required input: {field}")
        
        return errors
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.node_type!r}, label={self.config.label!r})"


# Type variable for node subclasses
NodeT = TypeVar("NodeT", bound=BaseFlowNode)


def create_node_factory(
    node_class: Type[NodeT],
    default_config: Optional[Dict[str, Any]] = None,
) -> Callable[..., NodeT]:
    """
    Create a factory function for a node class.
    
    Args:
        node_class: The node class to create instances of
        default_config: Default configuration values
        
    Returns:
        Factory function that creates node instances
    """
    def factory(**kwargs) -> NodeT:
        config_dict = {**(default_config or {}), **kwargs}
        config = node_class.config_class(**config_dict)
        return node_class(config=config)
    
    return factory
