"""
Kubernetes Pipeline Runner.

Executes pipeline nodes as Kubernetes Jobs for distributed processing.
Supports integration with Dask and Ray for parallel execution.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.kubernetes.client import KubernetesClient
from agentic_assistants.kubernetes.storage import MinIOStorage
from agentic_assistants.pipelines.node import Node
from agentic_assistants.pipelines.pipeline import Pipeline
from agentic_assistants.pipelines.runners.base import (
    AbstractRunner,
    NodeRunResult,
    PipelineRunResult,
    RunnerError,
)

logger = logging.getLogger(__name__)


def _node_run_remote(node: Node, inp: Dict[str, Any]) -> Dict[str, Any]:
    """Module-level helper so Dask/Ray can serialize distributed tasks."""
    return node.run(inp)


class KubernetesRunner(AbstractRunner):
    """
    Execute pipeline nodes as Kubernetes Jobs.

    This runner creates Kubernetes Jobs for each pipeline node,
    enabling distributed execution across the cluster. It supports:
    - Sequential node execution in topological order
    - Resource requests and limits per node
    - Artifact storage via MinIO
    - Integration with Dask/Ray for data-parallel operations

    Example:
        >>> runner = KubernetesRunner()
        >>> result = runner.run(pipeline, catalog)
    """

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        namespace: Optional[str] = None,
        image: str = "agentic/pipeline-runner:latest",
        default_cpu: str = "500m",
        default_memory: str = "1Gi",
        use_dask: bool = False,
        use_ray: bool = False,
    ):
        """
        Initialize the Kubernetes runner.

        Args:
            config: Agentic configuration
            namespace: Kubernetes namespace for jobs
            image: Container image for job execution
            default_cpu: Default CPU request per job
            default_memory: Default memory request per job
            use_dask: Use Dask for distributed data processing
            use_ray: Use Ray for distributed execution
        """
        super().__init__(is_async=True)
        self.config = config or AgenticConfig()
        self.namespace = namespace or self.config.kubernetes.default_deploy_namespace
        self.image = image
        self.default_cpu = default_cpu
        self.default_memory = default_memory
        self.use_dask = use_dask
        self.use_ray = use_ray

        self._client: Optional[KubernetesClient] = None
        self._storage: Optional[MinIOStorage] = None
        self._k8s_available = False

        try:
            from kubernetes import client  # noqa: F401

            self._k8s_available = True
        except ImportError:
            logger.warning("kubernetes library not installed. K8s runner disabled.")

    @property
    def client(self) -> KubernetesClient:
        """Get or create Kubernetes client."""
        if self._client is None:
            self._client = KubernetesClient(config=self.config)
        return self._client

    @property
    def storage(self) -> MinIOStorage:
        """Get or create MinIO storage client."""
        if self._storage is None:
            self._storage = MinIOStorage(config=self.config)
        return self._storage

    def run(
        self,
        pipeline: Pipeline,
        catalog: Any,
        run_id: Optional[str] = None,
        hook_manager: Optional[Any] = None,
    ) -> PipelineRunResult:
        """Execute the pipeline on Kubernetes (blocking)."""
        if hook_manager:
            self.set_hook_manager(hook_manager)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self._run_async(pipeline, catalog, run_id))
        raise RunnerError(
            "KubernetesRunner.run() cannot be used from a running event loop; "
            "call asyncio.run(runner._run_async(...)) instead."
        )

    async def _run_async(
        self,
        pipeline: Pipeline,
        catalog: Any,
        run_id: Optional[str] = None,
    ) -> PipelineRunResult:
        start_time = datetime.utcnow()
        node_results: List[NodeRunResult] = []
        errors: List[str] = []

        if not self._k8s_available:
            end_time = datetime.utcnow()
            return PipelineRunResult(
                pipeline=pipeline,
                node_results=[],
                outputs={},
                start_time=start_time,
                end_time=end_time,
                success=False,
                errors=["kubernetes library not installed"],
            )

        run_id = run_id or f"k8s-{int(time.time())}"
        logger.info("Starting Kubernetes pipeline run: %s", run_id)

        await self.client.create_namespace(self.namespace)

        data_store: Dict[str, Any] = {}
        for name in pipeline.inputs:
            try:
                data_store[name] = catalog.load(name)
            except Exception as exc:
                logger.warning("Could not load pipeline input %s: %s", name, exc)

        if data_store:
            await self._store_inputs(run_id, data_store)

        error: Optional[str] = None
        success = True

        try:
            for node in pipeline.topological_sort():
                n_start = datetime.utcnow()
                try:
                    raw = await self._execute_node(run_id, node, pipeline, data_store)
                    n_end = datetime.utcnow()
                    if isinstance(raw, dict) and raw.get("status") == "completed":
                        outs = raw.get("outputs") or {}
                        data_store.update(outs)
                        node_results.append(
                            NodeRunResult(
                                node_name=node.name,
                                outputs=outs,
                                start_time=n_start,
                                end_time=n_end,
                                success=True,
                            )
                        )
                    else:
                        err = (
                            (raw or {}).get("error", "Job execution failed")
                            if isinstance(raw, dict)
                            else "Job execution failed"
                        )
                        node_results.append(
                            NodeRunResult(
                                node_name=node.name,
                                outputs={},
                                start_time=n_start,
                                end_time=n_end,
                                success=False,
                                error=str(err),
                            )
                        )
                        errors.append(f"Node '{node.name}': {err}")
                        success = False
                        break
                except Exception as exc:
                    n_end = datetime.utcnow()
                    node_results.append(
                        NodeRunResult(
                            node_name=node.name,
                            outputs={},
                            start_time=n_start,
                            end_time=n_end,
                            success=False,
                            error=str(exc),
                        )
                    )
                    errors.append(f"Node '{node.name}': {exc}")
                    success = False
                    error = str(exc)
                    break

            retrieved = await self._retrieve_outputs(run_id, pipeline)
            final_outputs = {
                name: data_store[name]
                for name in pipeline.outputs
                if name in data_store
            }
            final_outputs.update(retrieved)

        except Exception as exc:
            logger.error("Pipeline execution failed: %s", exc)
            error = str(exc)
            success = False
            errors.append(str(exc))
            final_outputs = {}

        end_time = datetime.utcnow()

        await self._cleanup_jobs(run_id)

        return PipelineRunResult(
            pipeline=pipeline,
            node_results=node_results,
            outputs=final_outputs if success else {},
            start_time=start_time,
            end_time=end_time,
            success=success and error is None,
            errors=errors,
        )

    async def _execute_node(
        self,
        run_id: str,
        node: Node,
        pipeline: Pipeline,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a single node as a Kubernetes Job."""
        job_name = f"{run_id}-{node.name}".lower().replace("_", "-")[:63]

        logger.info("Creating job for node: %s", node.name)

        try:
            from kubernetes import client

            job = self._build_job_spec(job_name, node, run_id, inputs)

            batch_api = client.BatchV1Api()
            batch_api.create_namespaced_job(
                namespace=self.namespace,
                body=job,
            )

            return await self._wait_for_job(job_name)

        except Exception as exc:
            logger.error("Failed to execute node %s: %s", node.name, exc)
            raise

    def _build_job_spec(
        self,
        job_name: str,
        node: Node,
        run_id: str,
        _inputs: Dict[str, Any],
    ):
        """Build Kubernetes Job specification."""
        from kubernetes import client

        cpu_request = self.default_cpu
        memory_request = self.default_memory

        env = [
            client.V1EnvVar(name="RUN_ID", value=run_id),
            client.V1EnvVar(name="NODE_NAME", value=node.name),
            client.V1EnvVar(name="MINIO_ENDPOINT", value=self.config.minio.endpoint),
            client.V1EnvVar(name="MINIO_BUCKET", value=self.config.minio.default_bucket),
        ]

        if self.config.minio.access_key:
            env.append(
                client.V1EnvVar(
                    name="MINIO_ACCESS_KEY", value=self.config.minio.access_key
                )
            )
        if self.config.minio.secret_key:
            env.append(
                client.V1EnvVar(
                    name="MINIO_SECRET_KEY", value=self.config.minio.secret_key
                )
            )

        container = client.V1Container(
            name="node-runner",
            image=self.image,
            env=env,
            resources=client.V1ResourceRequirements(
                requests={"cpu": cpu_request, "memory": memory_request},
                limits={"cpu": cpu_request, "memory": memory_request},
            ),
            command=["python", "-m", "agentic_assistants.pipelines.node_executor"],
            args=[
                "--run-id",
                run_id,
                "--node-name",
                node.name,
            ],
        )

        pod_spec = client.V1PodSpec(
            containers=[container],
            restart_policy="Never",
        )

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(
                name=job_name,
                namespace=self.namespace,
                labels={
                    "agentic.io/run-id": run_id,
                    "agentic.io/node": node.name,
                    "agentic.io/managed": "true",
                },
            ),
            spec=client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    spec=pod_spec,
                ),
                backoff_limit=0,
                ttl_seconds_after_finished=3600,
            ),
        )

        return job

    async def _wait_for_job(
        self,
        job_name: str,
        timeout: int = 3600,
        poll_interval: int = 5,
    ) -> Dict[str, Any]:
        """Wait for a job to complete and return its result."""
        from kubernetes import client

        batch_api = client.BatchV1Api()
        start = time.time()

        while time.time() - start < timeout:
            job = batch_api.read_namespaced_job(
                name=job_name,
                namespace=self.namespace,
            )

            if job.status.succeeded:
                logger.info("Job %s completed successfully", job_name)
                return {
                    "status": "completed",
                    "outputs": await self._retrieve_node_outputs(job_name),
                }

            if job.status.failed:
                logger.error("Job %s failed", job_name)
                return {
                    "status": "failed",
                    "error": "Job execution failed",
                }

            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Job {job_name} timed out after {timeout}s")

    async def _store_inputs(self, run_id: str, inputs: Dict[str, Any]) -> None:
        """Store pipeline inputs in MinIO."""
        await self.storage.upload_json(
            self.config.minio.default_bucket,
            f"runs/{run_id}/inputs.json",
            inputs,
        )

    async def _retrieve_outputs(
        self,
        run_id: str,
        pipeline: Pipeline,
    ) -> Dict[str, Any]:
        """Retrieve final pipeline outputs from MinIO."""
        outputs: Dict[str, Any] = {}

        for node in pipeline.nodes:
            is_terminal = True
            for other in pipeline.nodes:
                if other.name == node.name:
                    continue
                if other.all_inputs & node.all_outputs:
                    is_terminal = False
                    break

            if is_terminal:
                try:
                    node_outputs = await self.storage.download_json(
                        self.config.minio.default_bucket,
                        f"runs/{run_id}/nodes/{node.name}/outputs.json",
                    )
                    if node_outputs:
                        outputs.update(node_outputs)
                except Exception:
                    pass

        return outputs

    async def _retrieve_node_outputs(self, job_name: str) -> Dict[str, Any]:
        """Retrieve outputs for a specific node."""
        _ = job_name
        return {}

    async def _cleanup_jobs(self, run_id: str) -> None:
        """Clean up completed jobs for a run."""
        if not self._k8s_available:
            return

        try:
            from kubernetes import client

            batch_api = client.BatchV1Api()

            batch_api.delete_collection_namespaced_job(
                namespace=self.namespace,
                label_selector=f"agentic.io/run-id={run_id}",
                propagation_policy="Background",
            )

            logger.info("Cleaned up jobs for run: %s", run_id)

        except Exception as exc:
            logger.warning("Failed to cleanup jobs: %s", exc)

    async def run_with_dask(
        self,
        pipeline: Pipeline,
        inputs: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
        scheduler_address: Optional[str] = None,
    ) -> PipelineRunResult:
        """
        Execute pipeline using Dask for distributed data processing.
        """
        start_time = datetime.utcnow()
        try:
            from dask.distributed import Client
        except ImportError:
            end_time = datetime.utcnow()
            return PipelineRunResult(
                pipeline=pipeline,
                node_results=[],
                outputs={},
                start_time=start_time,
                end_time=end_time,
                success=False,
                errors=["dask library not installed"],
            )

        run_id = run_id or f"dask-{int(time.time())}"
        scheduler = (
            scheduler_address
            or "tcp://dask-scheduler.data-services.svc.cluster.local:8786"
        )

        data_store: Dict[str, Any] = dict(inputs or {})
        node_results: List[NodeRunResult] = []
        errors: List[str] = []

        try:
            dask_client = Client(scheduler)
            logger.info("Connected to Dask scheduler: %s", scheduler)

            for node in pipeline.topological_sort():
                n_start = datetime.utcnow()
                try:
                    inp = {k: data_store[k] for k in node.input_names}
                    future = dask_client.submit(_node_run_remote, node, inp)
                    out = future.result()
                    data_store.update(out)
                    n_end = datetime.utcnow()
                    node_results.append(
                        NodeRunResult(
                            node_name=node.name,
                            outputs=out,
                            start_time=n_start,
                            end_time=n_end,
                            success=True,
                        )
                    )
                except Exception as exc:
                    n_end = datetime.utcnow()
                    node_results.append(
                        NodeRunResult(
                            node_name=node.name,
                            outputs={},
                            start_time=n_start,
                            end_time=n_end,
                            success=False,
                            error=str(exc),
                        )
                    )
                    errors.append(f"Node '{node.name}': {exc}")
                    break

            dask_client.close()

            end_time = datetime.utcnow()
            success = len(errors) == 0
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
                errors=errors,
            )

        except Exception as exc:
            logger.error("Dask execution failed: %s", exc)
            end_time = datetime.utcnow()
            return PipelineRunResult(
                pipeline=pipeline,
                node_results=node_results,
                outputs={},
                start_time=start_time,
                end_time=end_time,
                success=False,
                errors=errors + [str(exc)],
            )

    async def run_with_ray(
        self,
        pipeline: Pipeline,
        inputs: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
        ray_address: Optional[str] = None,
    ) -> PipelineRunResult:
        """Execute pipeline using Ray for distributed execution."""
        start_time = datetime.utcnow()
        try:
            import ray
        except ImportError:
            end_time = datetime.utcnow()
            return PipelineRunResult(
                pipeline=pipeline,
                node_results=[],
                outputs={},
                start_time=start_time,
                end_time=end_time,
                success=False,
                errors=["ray library not installed"],
            )

        _ = run_id
        address = ray_address or "ray://ray-head.data-services.svc.cluster.local:10001"

        data_store: Dict[str, Any] = dict(inputs or {})
        node_results: List[NodeRunResult] = []
        errors: List[str] = []

        try:
            ray.init(address=address, ignore_reinit_error=True)
            logger.info("Connected to Ray cluster: %s", address)

            execute_node_run = ray.remote(_node_run_remote)

            for node in pipeline.topological_sort():
                n_start = datetime.utcnow()
                try:
                    inp = {k: data_store[k] for k in node.input_names}
                    future = execute_node_run.remote(node, inp)
                    out = ray.get(future)
                    data_store.update(out)
                    n_end = datetime.utcnow()
                    node_results.append(
                        NodeRunResult(
                            node_name=node.name,
                            outputs=out,
                            start_time=n_start,
                            end_time=n_end,
                            success=True,
                        )
                    )
                except Exception as exc:
                    n_end = datetime.utcnow()
                    node_results.append(
                        NodeRunResult(
                            node_name=node.name,
                            outputs={},
                            start_time=n_start,
                            end_time=n_end,
                            success=False,
                            error=str(exc),
                        )
                    )
                    errors.append(f"Node '{node.name}': {exc}")
                    break

            end_time = datetime.utcnow()
            success = len(errors) == 0
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
                errors=errors,
            )

        except Exception as exc:
            logger.error("Ray execution failed: %s", exc)
            end_time = datetime.utcnow()
            return PipelineRunResult(
                pipeline=pipeline,
                node_results=node_results,
                outputs={},
                start_time=start_time,
                end_time=end_time,
                success=False,
                errors=errors + [str(exc)],
            )
