"""
Thread-based pipeline runner.

Executes independent nodes using a thread pool, suitable for I/O-bound tasks.
"""

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
import uuid

from agentic_assistants.pipelines.node import Node
from agentic_assistants.pipelines.pipeline import Pipeline
from agentic_assistants.pipelines.runners.base import (
    AbstractRunner,
    NodeRunResult,
    PipelineRunResult,
    RunnerError,
)
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class ThreadRunner(AbstractRunner):
    """
    Execute pipeline nodes using a thread pool.
    
    This runner is optimized for I/O-bound operations where threads
    can efficiently handle concurrent operations. Unlike ParallelRunner,
    ThreadRunner:
    - Doesn't require picklable functions
    - Has lower overhead for data passing
    - Shares memory between threads
    - Is affected by Python's GIL for CPU-bound tasks
    
    Best suited for:
    - API calls and network operations
    - File I/O operations
    - Database queries
    - External service integrations
    
    Example:
        >>> runner = ThreadRunner(max_workers=8)
        >>> result = runner.run(pipeline, catalog)
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        is_async: bool = False,
    ):
        """
        Initialize the thread runner.
        
        Args:
            max_workers: Maximum number of worker threads (default: min(32, cpu_count + 4))
            is_async: Not used (thread runner manages its own concurrency)
        """
        super().__init__(is_async=False)
        self.max_workers = max_workers
    
    def run(
        self,
        pipeline: Pipeline,
        catalog: Any,
        run_id: Optional[str] = None,
        hook_manager: Optional[Any] = None,
    ) -> PipelineRunResult:
        """
        Run the pipeline with thread-based parallelism.
        
        Args:
            pipeline: Pipeline to execute
            catalog: Data catalog for loading/saving datasets
            run_id: Optional unique run identifier
            hook_manager: Optional hook manager for callbacks
            
        Returns:
            PipelineRunResult with execution details
        """
        run_id = run_id or str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        if hook_manager:
            self.set_hook_manager(hook_manager)
        
        if self._hook_manager:
            self._call_hook("before_pipeline_run", pipeline=pipeline, catalog=catalog)
        
        logger.info(f"Starting threaded pipeline run: {run_id}")
        logger.info(f"Pipeline has {len(pipeline)} nodes, max_workers={self.max_workers}")
        
        # Data store for intermediate results (shared between threads)
        data_store: Dict[str, Any] = {}
        node_results: list[NodeRunResult] = []
        errors: list[str] = []
        
        # Build dependency information
        node_deps = self._build_dependencies(pipeline)
        completed: Set[str] = set()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while len(completed) < len(pipeline.nodes):
                # Find nodes that can run (all dependencies satisfied)
                ready_nodes = [
                    node for node in pipeline.nodes
                    if node.name not in completed
                    and all(dep in completed for dep in node_deps[node.name])
                ]
                
                if not ready_nodes:
                    if len(completed) < len(pipeline.nodes):
                        errors.append("Pipeline deadlock: no runnable nodes")
                    break
                
                logger.debug(f"Running {len(ready_nodes)} nodes in threads")
                
                # Submit ready nodes
                futures = {}
                for node in ready_nodes:
                    future = executor.submit(
                        self._run_node_in_thread,
                        node,
                        catalog,
                        data_store,
                    )
                    futures[future] = node
                
                # Wait for results
                for future in as_completed(futures):
                    node = futures[future]
                    
                    try:
                        result = future.result()
                        node_results.append(result)
                        
                        if result.success:
                            completed.add(node.name)
                            logger.debug(f"Node '{node.name}' completed in {result.duration_seconds:.3f}s")
                        else:
                            errors.append(f"Node '{node.name}' failed: {result.error}")
                            logger.error(f"Node '{node.name}' failed: {result.error}")
                    except Exception as e:
                        node_results.append(NodeRunResult(
                            node_name=node.name,
                            outputs={},
                            start_time=datetime.utcnow(),
                            end_time=datetime.utcnow(),
                            success=False,
                            error=str(e),
                        ))
                        errors.append(f"Node '{node.name}' execution error: {e}")
                
                # Stop if there were errors
                if errors:
                    break
        
        # Save final outputs
        if not errors:
            self._save_outputs(catalog, data_store, pipeline.outputs)
        
        end_time = datetime.utcnow()
        success = len(errors) == 0
        
        if self._hook_manager:
            self._call_hook(
                "after_pipeline_run",
                pipeline=pipeline,
                run_result={"success": success, "errors": errors},
            )
        
        if success:
            logger.info(f"Pipeline completed successfully in {(end_time - start_time).total_seconds():.2f}s")
        else:
            logger.error(f"Pipeline failed with {len(errors)} error(s)")
        
        return PipelineRunResult(
            pipeline=pipeline,
            node_results=node_results,
            outputs={name: data_store.get(name) for name in pipeline.outputs if name in data_store},
            start_time=start_time,
            end_time=end_time,
            success=success,
            errors=errors,
        )
    
    def _run_node_in_thread(
        self,
        node: Node,
        catalog: Any,
        data_store: Dict[str, Any],
    ) -> NodeRunResult:
        """
        Run a node in a thread.
        
        Args:
            node: Node to execute
            catalog: Data catalog
            data_store: Shared data store (thread-safe dict access)
            
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
                    param_name = input_name[7:]
                    inputs[input_name] = self._load_params(catalog, param_name)
                else:
                    inputs[input_name] = catalog.load(input_name)
            
            # Call before_node_run hook
            if self._hook_manager:
                self._call_hook("before_node_run", node=node, inputs=inputs)
            
            # Execute node
            outputs = node.run(inputs)
            
            # Store outputs (thread-safe for dict assignment in CPython)
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
            
            if self._hook_manager:
                self._call_hook("on_node_error", node=node, error=e)
            
            return NodeRunResult(
                node_name=node.name,
                outputs={},
                start_time=start_time,
                end_time=end_time,
                success=False,
                error=str(e),
            )
    
    def _build_dependencies(self, pipeline: Pipeline) -> Dict[str, Set[str]]:
        """Build dependency map for all nodes."""
        deps: Dict[str, Set[str]] = defaultdict(set)
        
        # Map outputs to producing nodes
        output_to_node: Dict[str, str] = {}
        for node in pipeline.nodes:
            for output in node.output_names:
                output_to_node[output] = node.name
        
        # Build dependencies
        for node in pipeline.nodes:
            for input_name in node.input_names:
                if input_name in output_to_node:
                    deps[node.name].add(output_to_node[input_name])
        
        return deps
