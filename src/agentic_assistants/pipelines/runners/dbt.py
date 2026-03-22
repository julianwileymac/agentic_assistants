"""
dbt pipeline runner -- executes dbt-tagged pipeline nodes as dbt model runs.

Follows the same interface as SequentialRunner and DagsterRunner
so it can be selected via the pipeline execution API.
"""

from typing import Any, Dict

from agentic_assistants.integrations.dbt import DbtClient, get_dbt_client
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class DbtRunner:
    """
    Pipeline runner that delegates tagged nodes to dbt-core.

    Nodes tagged with ``dbt`` are mapped to ``dbt run --select <node_name>``.
    Nodes tagged with ``dbt-test`` run ``dbt test --select <node_name>``.
    Remaining nodes are executed in-process using the standard callable.
    """

    def __init__(self, client: DbtClient | None = None):
        self.client = client or get_dbt_client()

    def run(self, pipeline, catalog: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Execute a pipeline, routing dbt-tagged nodes to dbt CLI."""
        catalog = catalog or {}
        results: Dict[str, Any] = {}

        sorted_nodes = pipeline.topological_sort()

        for node in sorted_nodes:
            tags = set(node.tags)

            if "dbt" in tags:
                logger.info("Running dbt model for node '%s'", node.name)
                result = self.client.run(select=node.name)
                results[node.name] = result
                if not result.get("success", False):
                    logger.error("dbt run failed for %s: %s", node.name, result.get("stderr", ""))
                    break

            elif "dbt-test" in tags:
                logger.info("Running dbt tests for node '%s'", node.name)
                result = self.client.test(select=node.name)
                results[node.name] = result

            else:
                logger.info("Running node '%s' in-process", node.name)
                inputs = {name: catalog.get(name) for name in node.inputs}
                try:
                    output = node.func(inputs)
                    if isinstance(output, dict):
                        catalog.update(output)
                    results[node.name] = {"success": True}
                except Exception as exc:
                    logger.error("Node '%s' failed: %s", node.name, exc)
                    results[node.name] = {"success": False, "error": str(exc)}
                    break

        return {
            "runner": "dbt",
            "nodes_executed": len(results),
            "results": results,
        }
