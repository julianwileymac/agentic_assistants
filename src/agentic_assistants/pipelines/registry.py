"""
Pipeline registry for managing project pipelines.

The PipelineRegistry provides a central location for registering and
retrieving pipelines by name.

Example:
    >>> from agentic_assistants.pipelines import Pipeline, node
    >>> from agentic_assistants.pipelines.registry import PipelineRegistry
    >>> 
    >>> registry = PipelineRegistry()
    >>> 
    >>> # Register pipelines
    >>> registry.register("data_processing", data_pipeline)
    >>> registry.register("training", training_pipeline)
    >>> 
    >>> # Get a pipeline
    >>> pipe = registry.get("data_processing")
    >>> 
    >>> # Get the default pipeline (all combined)
    >>> default = registry.get_default_pipeline()
"""

from typing import Callable, Dict, List, Optional, Set, Union

from agentic_assistants.pipelines.pipeline import Pipeline
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class PipelineRegistryError(Exception):
    """Exception raised for pipeline registry errors."""
    pass


class PipelineRegistry:
    """
    Central registry for managing project pipelines.
    
    The registry allows:
    - Registering pipelines by name
    - Retrieving individual pipelines
    - Getting a combined default pipeline
    - Listing all registered pipelines
    
    Attributes:
        _pipelines: Dictionary mapping names to pipelines
        _default_key: Name of the default pipeline
    
    Example:
        >>> registry = PipelineRegistry()
        >>> registry.register("preprocessing", preprocess_pipe)
        >>> registry.register("training", training_pipe)
        >>> 
        >>> # Get individual pipeline
        >>> pipe = registry.get("preprocessing")
        >>> 
        >>> # Get all pipelines combined
        >>> all_pipes = registry.get_default_pipeline()
    """
    
    DEFAULT_PIPELINE_NAME = "__default__"
    
    def __init__(self):
        """Initialize an empty pipeline registry."""
        self._pipelines: Dict[str, Pipeline] = {}
        self._pipeline_factories: Dict[str, Callable[[], Pipeline]] = {}
    
    def register(
        self,
        name: str,
        pipeline: Union[Pipeline, Callable[[], Pipeline]],
        *,
        overwrite: bool = False,
    ) -> None:
        """
        Register a pipeline with the registry.
        
        Args:
            name: Pipeline name
            pipeline: Pipeline instance or factory function
            overwrite: Whether to overwrite existing pipeline
            
        Raises:
            PipelineRegistryError: If name exists and overwrite is False
        """
        if name in self._pipelines and not overwrite:
            raise PipelineRegistryError(
                f"Pipeline '{name}' already registered. Use overwrite=True to replace."
            )
        
        if callable(pipeline) and not isinstance(pipeline, Pipeline):
            # It's a factory function
            self._pipeline_factories[name] = pipeline
            logger.debug(f"Registered pipeline factory: {name}")
        else:
            self._pipelines[name] = pipeline
            logger.debug(f"Registered pipeline: {name}")
    
    def unregister(self, name: str) -> bool:
        """
        Remove a pipeline from the registry.
        
        Args:
            name: Pipeline name
            
        Returns:
            True if removed, False if not found
        """
        if name in self._pipelines:
            del self._pipelines[name]
            return True
        if name in self._pipeline_factories:
            del self._pipeline_factories[name]
            return True
        return False
    
    def get(self, name: str) -> Optional[Pipeline]:
        """
        Get a pipeline by name.
        
        Args:
            name: Pipeline name
            
        Returns:
            Pipeline instance or None if not found
        """
        # Check direct pipelines first
        if name in self._pipelines:
            return self._pipelines[name]
        
        # Check factories
        if name in self._pipeline_factories:
            # Create pipeline from factory and cache it
            pipeline = self._pipeline_factories[name]()
            self._pipelines[name] = pipeline
            return pipeline
        
        return None
    
    def get_or_raise(self, name: str) -> Pipeline:
        """
        Get a pipeline by name, raising if not found.
        
        Args:
            name: Pipeline name
            
        Returns:
            Pipeline instance
            
        Raises:
            PipelineRegistryError: If pipeline not found
        """
        pipeline = self.get(name)
        if pipeline is None:
            raise PipelineRegistryError(f"Pipeline not found: {name}")
        return pipeline
    
    def get_default_pipeline(self) -> Pipeline:
        """
        Get the default pipeline (all pipelines combined).
        
        If a pipeline named '__default__' is registered, it is returned.
        Otherwise, all registered pipelines are combined.
        
        Returns:
            Combined Pipeline
        """
        # Check for explicit default
        if self.DEFAULT_PIPELINE_NAME in self._pipelines:
            return self._pipelines[self.DEFAULT_PIPELINE_NAME]
        
        if self.DEFAULT_PIPELINE_NAME in self._pipeline_factories:
            return self.get(self.DEFAULT_PIPELINE_NAME)
        
        # Combine all pipelines
        all_pipelines = self.list_pipelines()
        if not all_pipelines:
            return Pipeline([])
        
        return sum(
            self.get_or_raise(name) for name in all_pipelines
        )
    
    def list_pipelines(self) -> List[str]:
        """
        List all registered pipeline names.
        
        Returns:
            List of pipeline names
        """
        names = set(self._pipelines.keys()) | set(self._pipeline_factories.keys())
        return sorted(names)
    
    def has_pipeline(self, name: str) -> bool:
        """Check if a pipeline is registered."""
        return name in self._pipelines or name in self._pipeline_factories
    
    def clear(self) -> None:
        """Remove all registered pipelines."""
        self._pipelines.clear()
        self._pipeline_factories.clear()
    
    def describe(self) -> str:
        """Get a description of all registered pipelines."""
        lines = [f"PipelineRegistry with {len(self.list_pipelines())} pipelines:"]
        
        for name in self.list_pipelines():
            pipe = self.get(name)
            if pipe:
                lines.append(f"  - {name}: {len(pipe)} nodes")
        
        return "\n".join(lines)
    
    def __len__(self) -> int:
        """Return number of registered pipelines."""
        return len(self.list_pipelines())
    
    def __contains__(self, name: str) -> bool:
        """Check if pipeline is registered."""
        return self.has_pipeline(name)
    
    def __repr__(self) -> str:
        return f"PipelineRegistry(pipelines={self.list_pipelines()})"


# Global registry instance
_global_registry: Optional[PipelineRegistry] = None


def get_pipeline_registry() -> PipelineRegistry:
    """Get the global pipeline registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = PipelineRegistry()
    return _global_registry


def set_pipeline_registry(registry: PipelineRegistry) -> None:
    """Set the global pipeline registry."""
    global _global_registry
    _global_registry = registry


def register_pipeline(
    name: str,
    pipeline: Union[Pipeline, Callable[[], Pipeline]],
) -> None:
    """
    Register a pipeline with the global registry.
    
    Convenience function for quick registration.
    
    Args:
        name: Pipeline name
        pipeline: Pipeline instance or factory
    """
    get_pipeline_registry().register(name, pipeline)


def find_pipelines() -> Dict[str, Pipeline]:
    """
    Get all registered pipelines as a dictionary.
    
    Returns:
        Dictionary mapping names to pipelines
    """
    registry = get_pipeline_registry()
    return {name: registry.get_or_raise(name) for name in registry.list_pipelines()}
