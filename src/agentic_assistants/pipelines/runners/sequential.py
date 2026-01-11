"""
Sequential pipeline runner.

Executes nodes one at a time in topological order.
"""

from datetime import datetime
from typing import Any, Dict, Optional
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


class SequentialRunner(AbstractRunner):
    """
    Execute pipeline nodes sequentially in topological order.
    
    This is the default and safest runner, executing one node at a time.
    It's suitable for:
    - Debugging and development
    - When parallelization isn't beneficial
    - When resources are limited
    
    Example:
        >>> runner = SequentialRunner()
        >>> result = runner.run(pipeline, catalog)
        >>> print(f"Completed in {result.duration_seconds:.2f}s")
    """
    
    def __init__(self, is_async: bool = False):
        """
        Initialize the sequential runner.
        
        Args:
            is_async: Not used (sequential runner is always synchronous)
        """
        super().__init__(is_async=False)
    
    def run(
        self,
        pipeline: Pipeline,
        catalog: Any,
        run_id: Optional[str] = None,
        hook_manager: Optional[Any] = None,
    ) -> PipelineRunResult:
        """
        Run the pipeline sequentially.
        
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
        
        # Call before_pipeline_run hook
        if self._hook_manager:
            self._call_hook("before_pipeline_run", pipeline=pipeline, catalog=catalog)
        
        logger.info(f"Starting pipeline run: {run_id}")
        logger.info(f"Pipeline has {len(pipeline)} nodes")
        
        # Data store for intermediate results
        data_store: Dict[str, Any] = {}
        node_results: list[NodeRunResult] = []
        errors: list[str] = []
        
        # Execute nodes in topological order
        sorted_nodes = pipeline.topological_sort()
        
        for i, node in enumerate(sorted_nodes, 1):
            logger.info(f"[{i}/{len(sorted_nodes)}] Running node: {node.name}")
            
            result = self._run_node(node, catalog, data_store)
            node_results.append(result)
            
            if not result.success:
                errors.append(f"Node '{node.name}' failed: {result.error}")
                logger.error(f"Pipeline failed at node: {node.name}")
                break
            
            logger.debug(f"Node '{node.name}' completed in {result.duration_seconds:.3f}s")
        
        # Save final outputs
        if not errors:
            self._save_outputs(catalog, data_store, pipeline.outputs)
        
        end_time = datetime.utcnow()
        success = len(errors) == 0
        
        # Call after_pipeline_run hook
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
