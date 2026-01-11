"""
Parallel pipeline runner using multiprocessing.

Executes independent nodes in parallel for improved performance.
"""

from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
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


def _run_node_in_process(
    node_name: str,
    func: Any,
    inputs: Dict[str, Any],
    input_names: List[str],
    output_names: List[str],
) -> Dict[str, Any]:
    """
    Execute a node in a separate process.
    
    This function is called by ProcessPoolExecutor and must be
    picklable. It returns a dictionary with results.
    """
    try:
        # Reconstruct inputs
        args = [inputs[name] for name in input_names]
        result = func(*args)
        
        # Package outputs
        if len(output_names) == 0:
            outputs = {}
        elif len(output_names) == 1:
            outputs = {output_names[0]: result}
        else:
            outputs = dict(zip(output_names, result))
        
        return {
            "success": True,
            "outputs": outputs,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "outputs": {},
            "error": str(e),
        }


class ParallelRunner(AbstractRunner):
    """
    Execute pipeline nodes in parallel using multiprocessing.
    
    This runner identifies independent nodes (nodes that don't depend
    on each other) and executes them simultaneously. This can significantly
    speed up pipelines with parallelizable stages.
    
    Note:
        - Node functions must be picklable (no lambdas, closures, etc.)
        - Data is serialized between processes, which has overhead
        - Best for CPU-bound operations with significant computation time
    
    Example:
        >>> runner = ParallelRunner(max_workers=4)
        >>> result = runner.run(pipeline, catalog)
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        is_async: bool = False,
    ):
        """
        Initialize the parallel runner.
        
        Args:
            max_workers: Maximum number of parallel processes (default: CPU count)
            is_async: Not used (parallel runner manages its own concurrency)
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
        Run the pipeline with parallel execution.
        
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
        
        logger.info(f"Starting parallel pipeline run: {run_id}")
        logger.info(f"Pipeline has {len(pipeline)} nodes, max_workers={self.max_workers}")
        
        # Data store for intermediate results
        data_store: Dict[str, Any] = {}
        node_results: list[NodeRunResult] = []
        errors: list[str] = []
        
        # Build dependency information
        node_deps = self._build_dependencies(pipeline)
        completed: Set[str] = set()
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
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
                
                logger.debug(f"Running {len(ready_nodes)} nodes in parallel")
                
                # Submit ready nodes
                futures = {}
                for node in ready_nodes:
                    # Gather inputs
                    inputs = self._gather_inputs(node, catalog, data_store)
                    
                    # Submit to executor
                    future = executor.submit(
                        _run_node_in_process,
                        node.name,
                        node.func,
                        inputs,
                        node.input_names,
                        node.output_names,
                    )
                    futures[future] = node
                
                # Wait for results
                for future in as_completed(futures):
                    node = futures[future]
                    node_start = datetime.utcnow()
                    
                    try:
                        result = future.result()
                        node_end = datetime.utcnow()
                        
                        if result["success"]:
                            # Store outputs
                            for name, value in result["outputs"].items():
                                data_store[name] = value
                            
                            node_results.append(NodeRunResult(
                                node_name=node.name,
                                outputs=result["outputs"],
                                start_time=node_start,
                                end_time=node_end,
                                success=True,
                            ))
                            completed.add(node.name)
                            logger.debug(f"Node '{node.name}' completed")
                        else:
                            node_results.append(NodeRunResult(
                                node_name=node.name,
                                outputs={},
                                start_time=node_start,
                                end_time=node_end,
                                success=False,
                                error=result["error"],
                            ))
                            errors.append(f"Node '{node.name}' failed: {result['error']}")
                            logger.error(f"Node '{node.name}' failed: {result['error']}")
                    except Exception as e:
                        node_end = datetime.utcnow()
                        node_results.append(NodeRunResult(
                            node_name=node.name,
                            outputs={},
                            start_time=node_start,
                            end_time=node_end,
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
    
    def _gather_inputs(
        self,
        node: Node,
        catalog: Any,
        data_store: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Gather inputs for a node."""
        inputs = {}
        for input_name in node.input_names:
            if input_name in data_store:
                inputs[input_name] = data_store[input_name]
            elif input_name.startswith("params:"):
                param_name = input_name[7:]
                inputs[input_name] = self._load_params(catalog, param_name)
            else:
                inputs[input_name] = catalog.load(input_name)
        return inputs
