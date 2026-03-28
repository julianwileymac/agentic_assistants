"""
Dagster Pipeline Runner.

Executes pipeline nodes as Dagster ops within a job, supporting both
in-process execution (local/testing) and remote Dagster instance
submission (production).
"""

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from agentic_assistants.pipelines.runners.base import (
    AbstractRunner,
    NodeRunResult,
    PipelineRunResult,
    RunnerError,
)
from agentic_assistants.pipelines.pipeline import Pipeline
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

try:
    import dagster as dg
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False
    dg = None  # type: ignore


class DagsterRunner(AbstractRunner):
    """
    Execute pipeline nodes as Dagster ops within a job.

    This runner converts a Pipeline into a Dagster job and executes it,
    supporting both in-process execution for testing and remote
    DagsterInstance submission for production deployments.

    Example:
        >>> runner = DagsterRunner()
        >>> result = runner.run(pipeline, catalog)

        >>> # For remote execution
        >>> runner = DagsterRunner(dagster_host="http://dagster:3000")
        >>> result = runner.run(pipeline, catalog)
    """

    def __init__(
        self,
        dagster_host: Optional[str] = None,
        is_async: bool = False,
        run_config: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the Dagster runner.

        Args:
            dagster_host: URL of the Dagster webserver for remote execution.
                          If None, executes in-process.
            is_async: Whether to run asynchronously
            run_config: Default run configuration for Dagster jobs
            tags: Default tags for Dagster runs
        """
        super().__init__(is_async=is_async)

        if not DAGSTER_AVAILABLE:
            raise RunnerError(
                "Dagster is not installed. Install with: pip install dagster"
            )

        self._dagster_host = dagster_host
        self._default_run_config = run_config or {}
        self._default_tags = tags or {}

    def run(
        self,
        pipeline: Pipeline,
        catalog: Any,
        run_id: Optional[str] = None,
        hook_manager: Optional[Any] = None,
    ) -> PipelineRunResult:
        """
        Run a pipeline by converting it to a Dagster job and executing it.

        Args:
            pipeline: Pipeline to execute
            catalog: Data catalog for loading/saving datasets
            run_id: Optional unique run identifier
            hook_manager: Optional hook manager for callbacks

        Returns:
            PipelineRunResult with execution details
        """
        if hook_manager:
            self.set_hook_manager(hook_manager)

        actual_run_id = run_id or str(uuid.uuid4())
        start_time = datetime.utcnow()
        node_results: List[NodeRunResult] = []
        all_outputs: Dict[str, Any] = {}
        errors: List[str] = []

        sorted_nodes = pipeline.topological_sort()
        execution_order = [n.name for n in sorted_nodes]

        logger.info(
            f"DagsterRunner: executing pipeline {pipeline!r} "
            f"(run_id={actual_run_id})"
        )

        try:
            logger.info(
                f"Execution order: {execution_order} "
                f"({len(execution_order)} nodes)"
            )

            # Build Dagster ops from pipeline nodes
            ops_map = {}
            for node in sorted_nodes:
                node_name = node.name
                safe_name = node_name.replace(".", "_").replace("-", "_")

                @dg.op(name=safe_name)
                def make_op(context, _node=node, _catalog=catalog, _store=all_outputs):
                    """Execute a pipeline node as a Dagster op."""
                    inputs = {}
                    for input_name in _node.input_names:
                        if input_name in _store:
                            inputs[input_name] = _store[input_name]
                        elif input_name.startswith("params:"):
                            param_name = input_name[7:]
                            try:
                                params = _catalog.load("parameters")
                                value = params
                                for key in param_name.split("."):
                                    value = value[key]
                                inputs[input_name] = value
                            except Exception:
                                pass
                        else:
                            try:
                                inputs[input_name] = _catalog.load(input_name)
                            except Exception:
                                pass

                    outputs = _node.run(inputs)
                    for out_name, out_val in outputs.items():
                        _store[out_name] = out_val
                    return outputs

                ops_map[node_name] = make_op

            # Build and execute the job
            job_name = f"pipeline_{actual_run_id}".replace(".", "_").replace("-", "_")

            @dg.job(name=job_name, tags=self._default_tags)
            def dynamic_job():
                for node_name in execution_order:
                    ops_map[node_name]()

            # Execute in-process or submit to remote instance
            if self._dagster_host:
                result = self._execute_remote(dynamic_job, actual_run_id)
            else:
                result = dynamic_job.execute_in_process(
                    run_config=self._default_run_config,
                )

            # Convert Dagster result to pipeline node results
            for node_name in execution_order:
                node_start = datetime.utcnow()
                safe_name = node_name.replace(".", "_").replace("-", "_")

                # Check step success from Dagster result
                step_success = True
                step_error = None
                try:
                    step_events = result.events_for_node(safe_name)
                    for event in step_events:
                        if hasattr(event, "is_failure") and event.is_failure:
                            step_success = False
                            step_error = str(event)
                except Exception:
                    pass

                node_obj = pipeline.get_node(node_name)
                per_node_outputs: Dict[str, Any] = {}
                if node_obj is not None:
                    per_node_outputs = {
                        k: all_outputs[k]
                        for k in node_obj.output_names
                        if k in all_outputs
                    }
                node_results.append(
                    NodeRunResult(
                        node_name=node_name,
                        outputs=per_node_outputs,
                        start_time=node_start,
                        end_time=datetime.utcnow(),
                        success=step_success,
                        error=step_error,
                    )
                )

                if step_error:
                    errors.append(f"Node '{node_name}': {step_error}")

            overall_success = result.success if hasattr(result, "success") else len(errors) == 0

            # Save outputs to catalog
            self._save_outputs(catalog, all_outputs, pipeline.outputs)

        except Exception as e:
            logger.error(f"Pipeline {pipeline!r} failed: {e}")
            errors.append(str(e))
            overall_success = False

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        run_result = PipelineRunResult(
            pipeline=pipeline,
            node_results=node_results,
            outputs=all_outputs,
            start_time=start_time,
            end_time=end_time,
            success=overall_success,
            errors=errors,
        )

        logger.info(
            f"Pipeline {pipeline!r} {'succeeded' if overall_success else 'failed'} "
            f"in {duration:.2f}s ({len(node_results)} nodes)"
        )
        return run_result

    def _execute_remote(self, job: Any, run_id: str) -> Any:
        """
        Submit a job to a remote Dagster instance via the GraphQL API.

        Args:
            job: Dagster job to submit
            run_id: Run identifier

        Returns:
            Run result (polling for completion)
        """
        import httpx

        graphql_url = f"{self._dagster_host}/graphql"

        # Launch run via GraphQL
        mutation = """
        mutation LaunchRun($executionParams: ExecutionParams!) {
            launchRun(executionParams: $executionParams) {
                ... on LaunchRunSuccess {
                    run {
                        runId
                        status
                    }
                }
                ... on PythonError {
                    message
                    stack
                }
            }
        }
        """

        variables = {
            "executionParams": {
                "selector": {"repositoryLocationName": "default", "jobName": job.name},
                "runConfigData": self._default_run_config,
                "mode": "default",
            }
        }

        response = httpx.post(
            graphql_url,
            json={"query": mutation, "variables": variables},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        launch_result = data.get("data", {}).get("launchRun", {})
        if "run" in launch_result:
            remote_run_id = launch_result["run"]["runId"]
            logger.info(f"Launched remote Dagster run: {remote_run_id}")
            return self._poll_run_status(graphql_url, remote_run_id)
        else:
            error_msg = launch_result.get("message", "Unknown error")
            raise RunnerError(f"Failed to launch Dagster run: {error_msg}")

    def _poll_run_status(
        self,
        graphql_url: str,
        run_id: str,
        poll_interval: float = 2.0,
        max_wait: float = 3600.0,
    ) -> Any:
        """
        Poll a remote Dagster run until completion.

        Args:
            graphql_url: GraphQL endpoint URL
            run_id: Run to poll
            poll_interval: Seconds between polls
            max_wait: Maximum seconds to wait

        Returns:
            SimpleNamespace with success attribute
        """
        import httpx
        from types import SimpleNamespace

        query = """
        query RunStatus($runId: ID!) {
            runOrError(runId: $runId) {
                ... on Run {
                    runId
                    status
                }
            }
        }
        """

        terminal_statuses = {"SUCCESS", "FAILURE", "CANCELED"}
        elapsed = 0.0

        while elapsed < max_wait:
            response = httpx.post(
                graphql_url,
                json={"query": query, "variables": {"runId": run_id}},
                timeout=10,
            )
            data = response.json()
            status = (
                data.get("data", {}).get("runOrError", {}).get("status", "UNKNOWN")
            )

            if status in terminal_statuses:
                logger.info(f"Dagster run {run_id} finished with status: {status}")
                return SimpleNamespace(success=(status == "SUCCESS"))

            time.sleep(poll_interval)
            elapsed += poll_interval

        raise RunnerError(
            f"Dagster run {run_id} did not complete within {max_wait}s"
        )
