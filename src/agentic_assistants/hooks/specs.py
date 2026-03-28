"""
Hook specifications for lifecycle events.

This module defines the hook interfaces using pluggy-style specifications.
Hook implementations can be registered to receive callbacks during
pipeline, node, and dataset operations.

Example:
    >>> from agentic_assistants.hooks import hookimpl
    >>> 
    >>> class MyHook:
    ...     @hookimpl
    ...     def before_pipeline_run(self, pipeline, catalog):
    ...         print("Pipeline starting!")
    ...     
    ...     @hookimpl
    ...     def after_node_run(self, node, outputs):
    ...         print(f"Node {node.name} produced {len(outputs)} outputs")
"""

from typing import Any, Dict, Optional

from agentic_assistants.core.foundation.types import DataCatalogProtocol
from agentic_assistants.pipelines.node import Node
from agentic_assistants.pipelines.pipeline import Pipeline

# Try to import pluggy, fall back to simple implementation
try:
    import pluggy
    hookspec = pluggy.HookspecMarker("agentic")
    hookimpl = pluggy.HookimplMarker("agentic")
    HAS_PLUGGY = True
except ImportError:
    HAS_PLUGGY = False
    
    # Simple fallback decorators
    def hookspec(func=None, firstresult=False):
        """Mark a function as a hook specification."""
        if func is None:
            return lambda f: f
        return func
    
    def hookimpl(func=None, hookwrapper=False, optionalhook=False, tryfirst=False, trylast=False):
        """Mark a function as a hook implementation."""
        if func is None:
            return lambda f: f
        return func


class PipelineHookSpec:
    """
    Hook specification for pipeline lifecycle events.
    
    These hooks are called during pipeline execution at various stages.
    Implement these methods in your hook class to receive callbacks.
    """
    
    @hookspec
    def before_pipeline_run(
        self,
        pipeline: Pipeline,
        catalog: DataCatalogProtocol,
        run_id: Optional[str] = None,
    ) -> None:
        """
        Called before pipeline execution starts.
        
        Args:
            pipeline: The Pipeline instance
            catalog: The DataCatalog instance
            run_id: Optional unique run identifier
        """
        pass
    
    @hookspec
    def after_pipeline_run(
        self,
        pipeline: Pipeline,
        run_result: Dict[str, Any],
    ) -> None:
        """
        Called after pipeline execution completes.
        
        Args:
            pipeline: The Pipeline instance
            run_result: Dictionary with execution results
        """
        pass
    
    @hookspec
    def on_pipeline_error(
        self,
        pipeline: Pipeline,
        error: Exception,
    ) -> None:
        """
        Called when pipeline execution fails.
        
        Args:
            pipeline: The Pipeline instance
            error: The exception that occurred
        """
        pass


class NodeHookSpec:
    """
    Hook specification for node execution events.
    
    These hooks are called around individual node executions.
    """
    
    @hookspec
    def before_node_run(
        self,
        node: Node,
        inputs: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Called before a node executes.
        
        Args:
            node: The Node instance
            inputs: Dictionary of input data
            
        Returns:
            Optional modified inputs dictionary
        """
        pass
    
    @hookspec
    def after_node_run(
        self,
        node: Node,
        outputs: Dict[str, Any],
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Called after a node executes successfully.
        
        Args:
            node: The Node instance
            outputs: Dictionary of output data
            inputs: Optional dictionary of input data
            
        Returns:
            Optional modified outputs dictionary
        """
        pass
    
    @hookspec
    def on_node_error(
        self,
        node: Node,
        error: Exception,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Called when a node execution fails.
        
        Args:
            node: The Node instance
            error: The exception that occurred
            inputs: Optional dictionary of input data
        """
        pass


class DatasetHookSpec:
    """
    Hook specification for dataset operations.
    
    These hooks are called when datasets are loaded or saved.
    """
    
    @hookspec
    def before_dataset_loaded(
        self,
        dataset_name: str,
    ) -> None:
        """
        Called before a dataset is loaded.
        
        Args:
            dataset_name: Name of the dataset being loaded
        """
        pass
    
    @hookspec
    def after_dataset_loaded(
        self,
        dataset_name: str,
        data: Any,
    ) -> Optional[Any]:
        """
        Called after a dataset is loaded.
        
        Args:
            dataset_name: Name of the loaded dataset
            data: The loaded data
            
        Returns:
            Optional modified data
        """
        pass
    
    @hookspec
    def before_dataset_saved(
        self,
        dataset_name: str,
        data: Any,
    ) -> Optional[Any]:
        """
        Called before a dataset is saved.
        
        Args:
            dataset_name: Name of the dataset to save
            data: The data to save
            
        Returns:
            Optional modified data
        """
        pass
    
    @hookspec
    def after_dataset_saved(
        self,
        dataset_name: str,
        data: Any,
    ) -> None:
        """
        Called after a dataset is saved.
        
        Args:
            dataset_name: Name of the saved dataset
            data: The saved data
        """
        pass


class CatalogHookSpec:
    """
    Hook specification for catalog operations.
    """
    
    @hookspec
    def after_catalog_created(
        self,
        catalog: DataCatalogProtocol,
    ) -> None:
        """
        Called after a catalog is created.
        
        Args:
            catalog: The DataCatalog instance
        """
        pass
    
    @hookspec
    def on_catalog_error(
        self,
        error: Exception,
    ) -> None:
        """
        Called when a catalog operation fails.
        
        Args:
            error: The exception that occurred
        """
        pass
