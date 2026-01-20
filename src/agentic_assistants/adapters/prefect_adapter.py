"""
Prefect framework adapter with integrated observability.

This adapter wraps Prefect flows and tasks to provide:
- MLFlow experiment tracking for flow runs
- OpenTelemetry tracing for task execution
- Standardized metrics and logging
- Integration with Agentic Assistants pipelines

Example:
    >>> from agentic_assistants.adapters import PrefectAdapter
    >>> 
    >>> adapter = PrefectAdapter()
    >>> 
    >>> # Define a flow using the adapter
    >>> @adapter.flow(name="data_pipeline")
    >>> def my_pipeline(inputs: dict):
    ...     data = adapter.task("extract")(extract_data)(inputs)
    ...     processed = adapter.task("transform")(transform_data)(data)
    ...     return adapter.task("load")(load_data)(processed)
    >>> 
    >>> # Run with tracking
    >>> result = adapter.run_flow(my_pipeline, {"source": "db"})
"""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar

from agentic_assistants.adapters.base import BaseAdapter
from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")
FlowFunc = TypeVar("FlowFunc", bound=Callable[..., Any])
TaskFunc = TypeVar("TaskFunc", bound=Callable[..., Any])


class PrefectAdapter(BaseAdapter):
    """
    Adapter for Prefect workflow orchestration framework.
    
    This adapter provides observability wrappers for Prefect flows and tasks,
    tracking execution, state transitions, and performance metrics.
    
    Attributes:
        config: Agentic configuration instance
        prefect_available: Whether Prefect is installed
    """
    
    framework_name = "prefect"
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        **kwargs,
    ):
        """
        Initialize the Prefect adapter.
        
        Args:
            config: Configuration instance
            **kwargs: Additional arguments passed to BaseAdapter
        """
        super().__init__(config, name="Prefect", **kwargs)
        self._prefect_available = self._check_prefect()
        self._registered_flows: Dict[str, Any] = {}
        self._registered_tasks: Dict[str, Any] = {}
    
    def _check_prefect(self) -> bool:
        """Check if Prefect is available."""
        try:
            import prefect
            return True
        except ImportError:
            logger.warning("Prefect not installed. Install with: pip install prefect")
            return False
    
    @property
    def prefect_available(self) -> bool:
        """Whether Prefect is installed."""
        return self._prefect_available
    
    def run(self, flow: Any, inputs: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        Run a Prefect flow with tracking.
        
        This is a convenience method that calls run_flow.
        
        Args:
            flow: The Prefect flow to run
            inputs: Input parameters for the flow
            **kwargs: Additional arguments passed to run_flow
        
        Returns:
            Flow execution result
        """
        return self.run_flow(flow, inputs, **kwargs)
    
    def run_flow(
        self,
        flow: Any,
        inputs: Optional[Dict[str, Any]] = None,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Run a Prefect flow with full observability.
        
        Args:
            flow: The Prefect flow to run
            inputs: Input parameters for the flow
            experiment_name: MLFlow experiment name (optional)
            run_name: Name for this run
            tags: Additional tags for the run
        
        Returns:
            The flow execution result
        
        Example:
            >>> @prefect.flow
            >>> def my_flow(x: int) -> int:
            ...     return x * 2
            >>> 
            >>> result = adapter.run_flow(my_flow, {"x": 5})
        """
        if not self._prefect_available:
            raise RuntimeError("Prefect is not installed")
        
        # Set experiment if specified
        if experiment_name:
            self.tracker.experiment_name = experiment_name
        
        # Build run name
        actual_run_name = run_name or f"prefect-{time.strftime('%Y%m%d-%H%M%S')}"
        
        # Get flow name if available
        flow_name = getattr(flow, "name", getattr(flow, "__name__", "unknown"))
        
        # Build parameters
        params = {
            "framework": "prefect",
            "flow_name": flow_name,
            "input_keys": list(inputs.keys()) if inputs else [],
        }
        
        # Build tags
        all_tags = {"framework": "prefect", "flow_name": flow_name}
        if tags:
            all_tags.update(tags)
        
        with self.track_run(actual_run_name, tags=all_tags, params=params):
            start_time = time.time()
            
            try:
                logger.info(f"Starting Prefect flow: {flow_name}")
                
                # Run the flow
                if inputs:
                    result = flow(**inputs)
                else:
                    result = flow()
                
                duration = time.time() - start_time
                
                # Log success metrics
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)
                
                logger.info(f"Flow {flow_name} completed in {duration:.2f}s")
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                logger.error(f"Flow {flow_name} failed after {duration:.2f}s: {e}")
                raise
    
    def flow(
        self,
        name: Optional[str] = None,
        retries: int = 0,
        retry_delay_seconds: int = 30,
        timeout_seconds: Optional[int] = None,
        **prefect_kwargs,
    ) -> Callable[[FlowFunc], FlowFunc]:
        """
        Decorator to create an observable Prefect flow.
        
        Args:
            name: Flow name
            retries: Number of retries on failure
            retry_delay_seconds: Delay between retries
            timeout_seconds: Flow timeout
            **prefect_kwargs: Additional Prefect flow kwargs
        
        Returns:
            Decorated flow function
        
        Example:
            >>> @adapter.flow(name="my_pipeline", retries=2)
            >>> def pipeline(data: dict) -> dict:
            ...     return process(data)
        """
        def decorator(func: FlowFunc) -> FlowFunc:
            flow_name = name or func.__name__
            
            if self._prefect_available:
                import prefect
                
                # Create Prefect flow
                prefect_flow = prefect.flow(
                    name=flow_name,
                    retries=retries,
                    retry_delay_seconds=retry_delay_seconds,
                    timeout_seconds=timeout_seconds,
                    **prefect_kwargs,
                )(func)
                
                # Wrap with observability
                @wraps(func)
                def wrapped(*args, **kwargs):
                    with self.track_run(flow_name, tags={"type": "flow"}):
                        start_time = time.time()
                        try:
                            result = prefect_flow(*args, **kwargs)
                            self.tracker.log_metric("duration_seconds", time.time() - start_time)
                            self.tracker.log_metric("success", 1)
                            return result
                        except Exception as e:
                            self.tracker.log_metric("duration_seconds", time.time() - start_time)
                            self.tracker.log_metric("success", 0)
                            raise
                
                self._registered_flows[flow_name] = wrapped
                return wrapped  # type: ignore
            else:
                # Fallback: just run the function without Prefect
                self._registered_flows[flow_name] = func
                return func
        
        return decorator
    
    def task(
        self,
        name: Optional[str] = None,
        retries: int = 3,
        retry_delay_seconds: int = 10,
        cache_key_fn: Optional[Callable[..., str]] = None,
        timeout_seconds: Optional[int] = None,
        **prefect_kwargs,
    ) -> Callable[[TaskFunc], TaskFunc]:
        """
        Decorator to create an observable Prefect task.
        
        Args:
            name: Task name
            retries: Number of retries on failure
            retry_delay_seconds: Delay between retries
            cache_key_fn: Cache key function for result caching
            timeout_seconds: Task timeout
            **prefect_kwargs: Additional Prefect task kwargs
        
        Returns:
            Decorated task function
        
        Example:
            >>> @adapter.task(name="extract", retries=3)
            >>> def extract_data(source: str) -> list:
            ...     return fetch_from(source)
        """
        def decorator(func: TaskFunc) -> TaskFunc:
            task_name = name or func.__name__
            
            if self._prefect_available:
                import prefect
                
                # Create Prefect task
                prefect_task = prefect.task(
                    name=task_name,
                    retries=retries,
                    retry_delay_seconds=retry_delay_seconds,
                    cache_key_fn=cache_key_fn,
                    timeout_seconds=timeout_seconds,
                    **prefect_kwargs,
                )(func)
                
                # Wrap with observability
                @wraps(func)
                def wrapped(*args, **kwargs):
                    with self.track_step(task_name, attributes={"task_name": task_name}):
                        start_time = time.time()
                        try:
                            result = prefect_task(*args, **kwargs)
                            duration = time.time() - start_time
                            
                            # Log task metrics
                            if self.usage_tracker:
                                self.usage_tracker.track_agent_run(
                                    agent_name=task_name,
                                    framework="prefect",
                                    model="task",
                                    duration_seconds=duration,
                                    success=True,
                                )
                            
                            return result
                        except Exception as e:
                            if self.usage_tracker:
                                self.usage_tracker.track_agent_run(
                                    agent_name=task_name,
                                    framework="prefect",
                                    model="task",
                                    duration_seconds=time.time() - start_time,
                                    success=False,
                                    error_message=str(e),
                                )
                            raise
                
                self._registered_tasks[task_name] = wrapped
                return wrapped  # type: ignore
            else:
                # Fallback: just run the function
                self._registered_tasks[task_name] = func
                return func
        
        return decorator
    
    def create_flow_from_nodes(
        self,
        nodes: List["BaseFlowNode"],
        name: str = "generated_flow",
    ) -> Any:
        """
        Create a Prefect flow from Agentic Assistants flow nodes.
        
        Args:
            nodes: List of flow nodes to compose
            name: Name for the generated flow
        
        Returns:
            Prefect flow function
        """
        from agentic_assistants.pipelines.nodes import BaseFlowNode
        
        if not self._prefect_available:
            raise RuntimeError("Prefect is not installed")
        
        import prefect
        
        @prefect.flow(name=name)
        def generated_flow(initial_inputs: Dict[str, Any]) -> Dict[str, Any]:
            current_inputs = initial_inputs
            
            for node in nodes:
                # Create a task for each node
                @prefect.task(name=node.config.label or node.node_type)
                def execute_node(inputs: Dict[str, Any], n: BaseFlowNode = node) -> Dict[str, Any]:
                    result = n.run(inputs)
                    return result.outputs
                
                current_inputs = execute_node(current_inputs)
            
            return current_inputs
        
        return generated_flow
    
    def list_registered_flows(self) -> List[str]:
        """List all registered flows."""
        return list(self._registered_flows.keys())
    
    def list_registered_tasks(self) -> List[str]:
        """List all registered tasks."""
        return list(self._registered_tasks.keys())
    
    def get_flow(self, name: str) -> Optional[Any]:
        """Get a registered flow by name."""
        return self._registered_flows.get(name)
    
    def get_task(self, name: str) -> Optional[Any]:
        """Get a registered task by name."""
        return self._registered_tasks.get(name)


# Convenience function to create adapter
def get_prefect_adapter(**kwargs) -> PrefectAdapter:
    """Create a PrefectAdapter instance."""
    return PrefectAdapter(**kwargs)
