"""
dbt pipeline runner -- executes dbt-tagged pipeline nodes as dbt model runs.

Follows the same interface as SequentialRunner and DagsterRunner
so it can be selected via the pipeline execution API.
"""

from datetime import datetime
from typing import Any, List, Optional

from agentic_assistants.integrations.dbt import DbtClient, get_dbt_client
from agentic_assistants.pipelines.pipeline import Pipeline
from agentic_assistants.pipelines.runners.base import (
    AbstractRunner,
    NodeRunResult,
    PipelineRunResult,
)
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class DbtRunner(AbstractRunner):
    """
    Pipeline runner that delegates tagged nodes to dbt-core.

    Nodes tagged with ``dbt`` are mapped to ``dbt run --select <node_name>``.
    Nodes tagged with ``dbt-test`` run ``dbt test --select <node_name>``.
    Remaining nodes are executed in-process using the standard callable.
    """

    def __init__(self, client: DbtClient | None = None):
        super().__init__(is_async=False)
        self.client = client or get_dbt_client()

    def run(
        self,
        pipeline: Pipeline,
        catalog: Any,
        run_id: Optional[str] = None,
        hook_manager: Optional[Any] = None,
    ) -> PipelineRunResult:
        """Execute a pipeline, routing dbt-tagged nodes to dbt CLI."""
        _ = run_id
        if hook_manager:
            self.set_hook_manager(hook_manager)

        start_time = datetime.utcnow()
        node_results: List[NodeRunResult] = []
        errors_list: List[str] = []
        data_store: dict[str, Any] = {}

        sorted_nodes = pipeline.topological_sort()

        for node in sorted_nodes:
            tags = set(node.tags)
            n_start = datetime.utcnow()

            if "dbt" in tags:
                logger.info("Running dbt model for node '%s'", node.name)
                result = self.client.run(select=node.name)
                n_end = datetime.utcnow()
                ok = bool(result.get("success", False))
                node_results.append(
                    NodeRunResult(
                        node_name=node.name,
                        outputs={},
                        start_time=n_start,
                        end_time=n_end,
                        success=ok,
                        error=None if ok else result.get("stderr", "dbt run failed"),
                    )
                )
                if not ok:
                    logger.error(
                        "dbt run failed for %s: %s",
                        node.name,
                        result.get("stderr", ""),
                    )
                    errors_list.append(
                        f"Node '{node.name}': {result.get('stderr', 'dbt run failed')}"
                    )
                    break

            elif "dbt-test" in tags:
                logger.info("Running dbt tests for node '%s'", node.name)
                result = self.client.test(select=node.name)
                n_end = datetime.utcnow()
                ok = bool(result.get("success", False))
                node_results.append(
                    NodeRunResult(
                        node_name=node.name,
                        outputs={},
                        start_time=n_start,
                        end_time=n_end,
                        success=ok,
                        error=None if ok else result.get("stderr", "dbt test failed"),
                    )
                )
                if not ok:
                    errors_list.append(
                        f"Node '{node.name}': {result.get('stderr', 'dbt test failed')}"
                    )
                    break

            else:
                logger.info("Running node '%s' in-process", node.name)
                nr = self._run_node(node, catalog, data_store)
                node_results.append(nr)
                if not nr.success:
                    errors_list.append(
                        f"Node '{node.name}': {nr.error or 'unknown error'}"
                    )
                    break

        end_time = datetime.utcnow()
        success = len(errors_list) == 0
        outputs = {
            name: data_store[name]
            for name in pipeline.outputs
            if name in data_store
        }

        return PipelineRunResult(
            pipeline=pipeline,
            node_results=node_results,
            outputs=outputs if success else {},
            start_time=start_time,
            end_time=end_time,
            success=success,
            errors=errors_list,
        )
