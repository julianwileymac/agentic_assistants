"""
Bridge layer between existing pipelines and Prefect flows.

Converts pipeline nodes to Prefect tasks and DAGs to flows.
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional

try:
    from prefect import flow, task
    from prefect.task_runners import ConcurrentTaskRunner, SequentialTaskRunner
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False
    # Create dummy decorators if Prefect not available
    def task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else decorator(args[0])
    
    def flow(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else decorator(args[0])

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


def task_wrapper(
    func: Callable,
    name: Optional[str] = None,
    retries: int = 0,
    retry_delay_seconds: int = 0,
    cache_key_fn: Optional[Callable] = None,
    timeout_seconds: Optional[int] = None,
) -> Callable:
    """
    Wrap a function as a Prefect task.
    
    Args:
        func: The function to wrap
        name: Optional task name
        retries: Number of retries on failure
        retry_delay_seconds: Delay between retries
        cache_key_fn: Function to generate cache key
        timeout_seconds: Task timeout
        
    Returns:
        Prefect task-wrapped function
    """
    if not PREFECT_AVAILABLE:
        logger.warning("Prefect not available, returning unwrapped function")
        return func
    
    @task(
        name=name or func.__name__,
        retries=retries,
        retry_delay_seconds=retry_delay_seconds,
        cache_key_fn=cache_key_fn,
        timeout_seconds=timeout_seconds,
    )
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    return wrapper


def pipeline_to_flow(
    pipeline: Any,
    name: Optional[str] = None,
    runner: str = "concurrent",
    description: Optional[str] = None,
) -> Callable:
    """
    Convert a Pipeline to a Prefect flow.
    
    Args:
        pipeline: Pipeline instance
        name: Flow name
        runner: Task runner type ("concurrent" or "sequential")
        description: Flow description
        
    Returns:
        Prefect flow function
    """
    if not PREFECT_AVAILABLE:
        logger.error("Prefect not available, cannot convert pipeline")
        raise ImportError("Prefect is required for flow conversion")
    
    # Select task runner
    task_runner = (
        ConcurrentTaskRunner() if runner == "concurrent"
        else SequentialTaskRunner()
    )
    
    @flow(
        name=name or pipeline.name,
        description=description or f"Converted from pipeline: {pipeline.name}",
        task_runner=task_runner,
    )
    def pipeline_flow(catalog: Any = None, **kwargs) -> Dict[str, Any]:
        """
        Execute pipeline as Prefect flow.
        
        Args:
            catalog: Data catalog
            **kwargs: Additional parameters
            
        Returns:
            Dict of results by node name
        """
        from collections import defaultdict
        
        results = {}
        node_outputs = defaultdict(dict)
        
        # Get execution order (topological sort)
        execution_order = pipeline.get_execution_order()
        
        # Convert nodes to tasks and execute
        for node_name in execution_order:
            node = pipeline.nodes[node_name]
            
            # Wrap node function as task
            node_task = task_wrapper(
                node.func,
                name=node_name,
                retries=getattr(node, 'retries', 0),
            )
            
            # Prepare inputs
            inputs = {}
            for input_name in node.inputs:
                if input_name in results:
                    inputs[input_name] = results[input_name]
                elif catalog and hasattr(catalog, 'load'):
                    try:
                        inputs[input_name] = catalog.load(input_name)
                    except:
                        pass
            
            # Execute task
            try:
                result = node_task(**inputs, **kwargs)
                
                # Store outputs
                if len(node.outputs) == 1:
                    results[node.outputs[0]] = result
                elif isinstance(result, dict):
                    for output_name in node.outputs:
                        if output_name in result:
                            results[output_name] = result[output_name]
                elif isinstance(result, (list, tuple)) and len(result) == len(node.outputs):
                    for output_name, value in zip(node.outputs, result):
                        results[output_name] = value
                
                node_outputs[node_name] = result
                
            except Exception as e:
                logger.error(f"Error executing node {node_name}: {e}")
                raise
        
        return dict(node_outputs)
    
    return pipeline_flow


def convert_remote_fetcher(fetcher_class: type) -> type:
    """
    Convert RemoteFetcher class methods to Prefect tasks.
    
    Args:
        fetcher_class: RemoteFetcher subclass
        
    Returns:
        Modified class with Prefect task decorators
    """
    if not PREFECT_AVAILABLE:
        return fetcher_class
    
    # Wrap the fetch method
    original_fetch = fetcher_class.fetch
    
    @task(name=f"{fetcher_class.__name__}.fetch", retries=3, retry_delay_seconds=5)
    async def fetch_task(self, *args, **kwargs):
        return await original_fetch(self, *args, **kwargs)
    
    fetcher_class.fetch = fetch_task
    return fetcher_class


def create_flow_from_function(
    func: Callable,
    name: Optional[str] = None,
    description: Optional[str] = None,
    retries: int = 0,
    retry_delay_seconds: int = 0,
    timeout_seconds: Optional[int] = None,
) -> Callable:
    """
    Create a simple Prefect flow from a single function.
    
    Args:
        func: Function to convert
        name: Flow name
        description: Flow description
        retries: Number of retries
        retry_delay_seconds: Delay between retries
        timeout_seconds: Flow timeout
        
    Returns:
        Prefect flow function
    """
    if not PREFECT_AVAILABLE:
        logger.warning("Prefect not available, returning original function")
        return func
    
    @flow(name=name or func.__name__, description=description)
    def flow_wrapper(*args, **kwargs):
        # Wrap the function as a task within the flow
        func_task = task(
            func,
            retries=retries,
            retry_delay_seconds=retry_delay_seconds,
            timeout_seconds=timeout_seconds,
        )
        return func_task(*args, **kwargs)
    
    return flow_wrapper


def migrate_apscheduler_job(job_func: Callable, schedule: str) -> None:
    """
    Migrate an APScheduler job to Prefect deployment.
    
    Args:
        job_func: Job function
        schedule: Cron or interval schedule string
    """
    if not PREFECT_AVAILABLE:
        logger.error("Prefect not available for job migration")
        return
    
    # Create flow from function
    migrated_flow = create_flow_from_function(job_func)
    
    logger.info(f"Migrated job {job_func.__name__} to Prefect flow")
    logger.info(f"To deploy: prefect deployment build {migrated_flow.__name__}:{job_func.__name__} --cron '{schedule}'")
