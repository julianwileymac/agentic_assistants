"""
Abstract base class for pipeline runners.

This module defines the interface that all runners must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from agentic_assistants.core.foundation.types import (
    DataCatalogProtocol,
    HookManagerProtocol,
    NodeOutputs,
)

from agentic_assistants.pipelines.node import Node
from agentic_assistants.pipelines.pipeline import Pipeline, PipelineOutput
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class RunnerError(Exception):
    """Exception raised for runner-related errors."""
    pass


@dataclass
class NodeRunResult:
    """Result of running a single node."""
    node_name: str
    outputs: NodeOutputs
    start_time: datetime
    end_time: datetime
    success: bool
    error: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()


@dataclass
class PipelineRunResult:
    """Result of running a pipeline."""
    pipeline: Pipeline
    node_results: List[NodeRunResult]
    outputs: NodeOutputs
    start_time: datetime
    end_time: datetime
    success: bool
    errors: List[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def execution_order(self) -> List[str]:
        return [r.node_name for r in self.node_results]


class AbstractRunner(ABC):
    """
    Abstract base class for pipeline runners.
    
    All runners must implement the run() method to execute a pipeline
    with a data catalog.
    
    Attributes:
        is_async: Whether the runner supports async execution
    
    Subclasses:
        - SequentialRunner: Execute nodes sequentially
        - ParallelRunner: Execute independent nodes in parallel
        - ThreadRunner: Execute with thread pool
    """
    
    is_async: bool = False
    
    def __init__(
        self,
        is_async: bool = False,
    ):
        """
        Initialize the runner.
        
        Args:
            is_async: Whether to run asynchronously
        """
        self.is_async = is_async
        self._hook_manager: Optional[HookManagerProtocol] = None
    
    def set_hook_manager(self, hook_manager: HookManagerProtocol) -> None:
        """
        Set the hook manager for lifecycle callbacks.
        
        Args:
            hook_manager: Hook manager instance
        """
        self._hook_manager = hook_manager
    
    @abstractmethod
    def run(
        self,
        pipeline: Pipeline,
        catalog: DataCatalogProtocol,
        run_id: Optional[str] = None,
        hook_manager: Optional[HookManagerProtocol] = None,
    ) -> PipelineRunResult:
        """
        Run a pipeline with the given catalog.
        
        Args:
            pipeline: Pipeline to execute
            catalog: Data catalog for loading/saving datasets
            run_id: Optional unique run identifier
            hook_manager: Optional hook manager for callbacks
            
        Returns:
            PipelineRunResult with execution details
        """
        pass
    
    def _run_node(
        self,
        node: Node,
        catalog: DataCatalogProtocol,
        data_store: Dict[str, Any],
    ) -> NodeRunResult:
        """
        Run a single node.
        
        Args:
            node: Node to execute
            catalog: Data catalog
            data_store: Dictionary of available data
            
        Returns:
            NodeRunResult with execution details
        """
        start_time = datetime.utcnow()
        
        try:
            # Gather inputs
            inputs = {}
            for input_name in node.input_names:
                if input_name in data_store:
                    inputs[input_name] = data_store[input_name]
                elif input_name.startswith("params:"):
                    # Parameter reference
                    param_name = input_name[7:]  # Remove "params:" prefix
                    inputs[input_name] = self._load_params(catalog, param_name)
                else:
                    # Load from catalog
                    inputs[input_name] = catalog.load(input_name)
            
            # Call before_node_run hook
            if self._hook_manager:
                self._call_hook("before_node_run", node=node, inputs=inputs)
            
            # Execute node
            outputs = dict(node.run(inputs))
            
            # Store outputs
            for output_name, output_value in outputs.items():
                data_store[output_name] = output_value
            
            # Call after_node_run hook
            if self._hook_manager:
                self._call_hook("after_node_run", node=node, outputs=outputs)
            
            end_time = datetime.utcnow()
            
            return NodeRunResult(
                node_name=node.name,
                outputs=outputs,
                start_time=start_time,
                end_time=end_time,
                success=True,
            )
            
        except Exception as e:
            end_time = datetime.utcnow()
            
            # Call on_node_error hook
            if self._hook_manager:
                self._call_hook("on_node_error", node=node, error=e)
            
            logger.error(f"Node '{node.name}' failed: {e}")
            
            return NodeRunResult(
                node_name=node.name,
                outputs={},
                start_time=start_time,
                end_time=end_time,
                success=False,
                error=str(e),
            )
    
    def _load_params(self, catalog: DataCatalogProtocol, param_path: str) -> Any:
        """
        Load parameters from the catalog.
        
        Args:
            catalog: Data catalog
            param_path: Parameter path (e.g., "model.learning_rate")
            
        Returns:
            Parameter value
        """
        # Try to load from "parameters" dataset
        try:
            params = catalog.load("parameters")
            
            # Navigate nested path
            value = params
            for key in param_path.split("."):
                value = value[key]
            return value
        except Exception:
            raise RunnerError(f"Could not load parameter: params:{param_path}")
    
    def _call_hook(self, hook_name: str, **kwargs) -> None:
        """Call a hook if the hook manager is set."""
        if self._hook_manager and hasattr(self._hook_manager.hook, hook_name):
            getattr(self._hook_manager.hook, hook_name)(**kwargs)
    
    def _save_outputs(
        self,
        catalog: DataCatalogProtocol,
        data_store: Dict[str, Any],
        output_names: Set[str],
    ) -> None:
        """
        Save pipeline outputs to the catalog.
        
        Args:
            catalog: Data catalog
            data_store: Dictionary of computed data
            output_names: Names of outputs to save
        """
        for name in output_names:
            if name in data_store:
                try:
                    catalog.save(name, data_store[name])
                except Exception as e:
                    logger.warning(f"Could not save output '{name}': {e}")
    
    def create_default_data_set(self, name: str) -> Any:
        """
        Create a default in-memory dataset for unregistered outputs.
        
        Args:
            name: Dataset name
            
        Returns:
            In-memory dataset instance
        """
        # Return a simple dict-based storage
        return {"_name": name, "_data": None}
