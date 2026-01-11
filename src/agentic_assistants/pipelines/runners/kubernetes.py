"""
Kubernetes Pipeline Runner.

Executes pipeline nodes as Kubernetes Jobs for distributed processing.
Supports integration with Dask and Ray for parallel execution.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

from agentic_assistants.config import AgenticConfig
from agentic_assistants.kubernetes.client import KubernetesClient
from agentic_assistants.kubernetes.storage import MinIOStorage
from agentic_assistants.pipelines.base import Pipeline, Node
from agentic_assistants.pipelines.runners.base import PipelineRunner, RunResult

logger = logging.getLogger(__name__)


class KubernetesRunner(PipelineRunner):
    """
    Execute pipeline nodes as Kubernetes Jobs.
    
    This runner creates Kubernetes Jobs for each pipeline node,
    enabling distributed execution across the cluster. It supports:
    - Parallel node execution based on DAG dependencies
    - Resource requests and limits per node
    - Artifact storage via MinIO
    - Integration with Dask/Ray for data-parallel operations
    
    Example:
        >>> runner = KubernetesRunner()
        >>> result = await runner.run(pipeline, inputs={"data": df})
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
        super().__init__(config)
        self.namespace = namespace or self.config.kubernetes.default_deploy_namespace
        self.image = image
        self.default_cpu = default_cpu
        self.default_memory = default_memory
        self.use_dask = use_dask
        self.use_ray = use_ray
        
        self._client: Optional[KubernetesClient] = None
        self._storage: Optional[MinIOStorage] = None
        self._k8s_available = False
        
        # Check if kubernetes library is available
        try:
            from kubernetes import client
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

    async def run(
        self,
        pipeline: Pipeline,
        inputs: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
    ) -> RunResult:
        """
        Execute the pipeline on Kubernetes.
        
        Args:
            pipeline: Pipeline to execute
            inputs: Initial input data
            run_id: Optional run identifier
            
        Returns:
            RunResult with execution details
        """
        if not self._k8s_available:
            return RunResult(
                run_id=run_id or f"k8s-{int(time.time())}",
                pipeline_name=pipeline.name,
                status="failed",
                error="kubernetes library not installed",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                outputs={},
                node_results={},
            )
        
        run_id = run_id or f"k8s-{pipeline.name}-{int(time.time())}"
        start_time = datetime.utcnow()
        
        logger.info(f"Starting Kubernetes pipeline run: {run_id}")
        
        # Ensure namespace exists
        await self.client.create_namespace(self.namespace)
        
        # Store inputs in MinIO
        if inputs:
            await self._store_inputs(run_id, inputs)
        
        # Build execution plan
        execution_order = self._topological_sort(pipeline)
        
        # Track results
        node_results: Dict[str, Dict[str, Any]] = {}
        outputs: Dict[str, Any] = {}
        error: Optional[str] = None
        
        try:
            # Execute nodes in dependency order
            for node_batch in execution_order:
                # Execute batch in parallel
                batch_tasks = [
                    self._execute_node(run_id, node, pipeline, inputs or {})
                    for node in node_batch
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Process results
                for node, result in zip(node_batch, batch_results):
                    if isinstance(result, Exception):
                        node_results[node.name] = {
                            "status": "failed",
                            "error": str(result),
                        }
                        raise result
                    else:
                        node_results[node.name] = result
                        # Update inputs with outputs for downstream nodes
                        if result.get("outputs"):
                            inputs = inputs or {}
                            inputs.update(result["outputs"])
            
            # Retrieve final outputs
            outputs = await self._retrieve_outputs(run_id, pipeline)
            status = "completed"
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            error = str(e)
            status = "failed"
        
        end_time = datetime.utcnow()
        
        # Cleanup jobs
        await self._cleanup_jobs(run_id)
        
        return RunResult(
            run_id=run_id,
            pipeline_name=pipeline.name,
            status=status,
            error=error,
            start_time=start_time,
            end_time=end_time,
            outputs=outputs,
            node_results=node_results,
        )

    def _topological_sort(self, pipeline: Pipeline) -> List[List[Node]]:
        """
        Sort nodes into execution batches based on dependencies.
        
        Returns a list of batches, where nodes in each batch can
        be executed in parallel.
        """
        # Build dependency graph
        in_degree: Dict[str, int] = {node.name: 0 for node in pipeline.nodes}
        dependents: Dict[str, List[str]] = {node.name: [] for node in pipeline.nodes}
        
        for node in pipeline.nodes:
            for dep in node.inputs:
                # Find which node produces this input
                for other in pipeline.nodes:
                    if dep in other.outputs:
                        in_degree[node.name] += 1
                        dependents[other.name].append(node.name)
        
        # Build batches
        batches: List[List[Node]] = []
        remaining = set(node.name for node in pipeline.nodes)
        node_map = {node.name: node for node in pipeline.nodes}
        
        while remaining:
            # Find nodes with no dependencies
            ready = [name for name in remaining if in_degree[name] == 0]
            if not ready:
                raise ValueError("Circular dependency detected in pipeline")
            
            batches.append([node_map[name] for name in ready])
            
            # Update dependencies
            for name in ready:
                remaining.remove(name)
                for dep in dependents[name]:
                    in_degree[dep] -= 1
        
        return batches

    async def _execute_node(
        self,
        run_id: str,
        node: Node,
        pipeline: Pipeline,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a single node as a Kubernetes Job."""
        job_name = f"{run_id}-{node.name}".lower().replace("_", "-")[:63]
        
        logger.info(f"Creating job for node: {node.name}")
        
        try:
            from kubernetes import client
            
            # Build job spec
            job = self._build_job_spec(
                job_name=job_name,
                node=node,
                run_id=run_id,
                inputs=inputs,
            )
            
            # Create job
            batch_api = client.BatchV1Api()
            batch_api.create_namespaced_job(
                namespace=self.namespace,
                body=job,
            )
            
            # Wait for completion
            result = await self._wait_for_job(job_name)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute node {node.name}: {e}")
            raise

    def _build_job_spec(
        self,
        job_name: str,
        node: Node,
        run_id: str,
        inputs: Dict[str, Any],
    ):
        """Build Kubernetes Job specification."""
        from kubernetes import client
        
        # Get resource requirements from node metadata
        cpu_request = node.metadata.get("cpu", self.default_cpu)
        memory_request = node.metadata.get("memory", self.default_memory)
        
        # Build environment variables
        env = [
            client.V1EnvVar(name="RUN_ID", value=run_id),
            client.V1EnvVar(name="NODE_NAME", value=node.name),
            client.V1EnvVar(name="MINIO_ENDPOINT", value=self.config.minio.endpoint),
            client.V1EnvVar(name="MINIO_BUCKET", value=self.config.minio.default_bucket),
        ]
        
        if self.config.minio.access_key:
            env.append(client.V1EnvVar(name="MINIO_ACCESS_KEY", value=self.config.minio.access_key))
        if self.config.minio.secret_key:
            env.append(client.V1EnvVar(name="MINIO_SECRET_KEY", value=self.config.minio.secret_key))
        
        # Build container spec
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
                "--run-id", run_id,
                "--node-name", node.name,
            ],
        )
        
        # Build pod spec
        pod_spec = client.V1PodSpec(
            containers=[container],
            restart_policy="Never",
        )
        
        # Build job spec
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
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            job = batch_api.read_namespaced_job(
                name=job_name,
                namespace=self.namespace,
            )
            
            if job.status.succeeded:
                logger.info(f"Job {job_name} completed successfully")
                return {
                    "status": "completed",
                    "outputs": await self._retrieve_node_outputs(job_name),
                }
            
            if job.status.failed:
                logger.error(f"Job {job_name} failed")
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
        outputs = {}
        
        # Get outputs from terminal nodes
        for node in pipeline.nodes:
            # Check if this is a terminal node (no other nodes depend on its outputs)
            is_terminal = True
            for other in pipeline.nodes:
                if node.name != other.name:
                    for inp in other.inputs:
                        if inp in node.outputs:
                            is_terminal = False
                            break
            
            if is_terminal:
                node_outputs = await self.storage.download_json(
                    self.config.minio.default_bucket,
                    f"runs/{run_id}/nodes/{node.name}/outputs.json",
                )
                if node_outputs:
                    outputs.update(node_outputs)
        
        return outputs

    async def _retrieve_node_outputs(self, job_name: str) -> Dict[str, Any]:
        """Retrieve outputs for a specific node."""
        # Parse run_id and node_name from job_name
        parts = job_name.rsplit("-", 1)
        if len(parts) >= 2:
            # Job name format: {run_id}-{node_name}
            # This is simplified - in production, use labels
            pass
        
        # For now, return empty dict - actual implementation would
        # read from MinIO based on job labels
        return {}

    async def _cleanup_jobs(self, run_id: str) -> None:
        """Clean up completed jobs for a run."""
        if not self._k8s_available:
            return
        
        try:
            from kubernetes import client
            
            batch_api = client.BatchV1Api()
            
            # Delete jobs with matching run-id label
            batch_api.delete_collection_namespaced_job(
                namespace=self.namespace,
                label_selector=f"agentic.io/run-id={run_id}",
                propagation_policy="Background",
            )
            
            logger.info(f"Cleaned up jobs for run: {run_id}")
            
        except Exception as e:
            logger.warning(f"Failed to cleanup jobs: {e}")

    async def run_with_dask(
        self,
        pipeline: Pipeline,
        inputs: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
        scheduler_address: Optional[str] = None,
    ) -> RunResult:
        """
        Execute pipeline using Dask for distributed data processing.
        
        This method connects to a Dask scheduler running in the cluster
        and uses Dask's distributed computing capabilities.
        
        Args:
            pipeline: Pipeline to execute
            inputs: Initial input data
            run_id: Optional run identifier
            scheduler_address: Dask scheduler address
        """
        try:
            from dask.distributed import Client
        except ImportError:
            return RunResult(
                run_id=run_id or f"dask-{int(time.time())}",
                pipeline_name=pipeline.name,
                status="failed",
                error="dask library not installed",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                outputs={},
                node_results={},
            )
        
        run_id = run_id or f"dask-{pipeline.name}-{int(time.time())}"
        start_time = datetime.utcnow()
        
        # Default scheduler address
        scheduler = scheduler_address or "tcp://dask-scheduler.data-services.svc.cluster.local:8786"
        
        try:
            # Connect to Dask cluster
            client = Client(scheduler)
            logger.info(f"Connected to Dask scheduler: {scheduler}")
            
            # Execute pipeline nodes
            outputs = {}
            node_results = {}
            
            for node in pipeline.nodes:
                # Submit node execution to Dask
                future = client.submit(
                    node.func,
                    *[inputs.get(inp) for inp in node.inputs] if inputs else [],
                )
                result = future.result()
                
                node_results[node.name] = {"status": "completed"}
                
                # Update outputs
                if node.outputs:
                    for i, output_name in enumerate(node.outputs):
                        if isinstance(result, tuple):
                            outputs[output_name] = result[i]
                        else:
                            outputs[output_name] = result
                
                # Update inputs for downstream nodes
                if inputs is None:
                    inputs = {}
                inputs.update(outputs)
            
            client.close()
            
            return RunResult(
                run_id=run_id,
                pipeline_name=pipeline.name,
                status="completed",
                start_time=start_time,
                end_time=datetime.utcnow(),
                outputs=outputs,
                node_results=node_results,
            )
            
        except Exception as e:
            logger.error(f"Dask execution failed: {e}")
            return RunResult(
                run_id=run_id,
                pipeline_name=pipeline.name,
                status="failed",
                error=str(e),
                start_time=start_time,
                end_time=datetime.utcnow(),
                outputs={},
                node_results={},
            )

    async def run_with_ray(
        self,
        pipeline: Pipeline,
        inputs: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
        ray_address: Optional[str] = None,
    ) -> RunResult:
        """
        Execute pipeline using Ray for distributed execution.
        
        Args:
            pipeline: Pipeline to execute
            inputs: Initial input data
            run_id: Optional run identifier
            ray_address: Ray cluster address
        """
        try:
            import ray
        except ImportError:
            return RunResult(
                run_id=run_id or f"ray-{int(time.time())}",
                pipeline_name=pipeline.name,
                status="failed",
                error="ray library not installed",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                outputs={},
                node_results={},
            )
        
        run_id = run_id or f"ray-{pipeline.name}-{int(time.time())}"
        start_time = datetime.utcnow()
        
        # Default Ray address
        address = ray_address or "ray://ray-head.data-services.svc.cluster.local:10001"
        
        try:
            # Connect to Ray cluster
            ray.init(address=address, ignore_reinit_error=True)
            logger.info(f"Connected to Ray cluster: {address}")
            
            # Execute pipeline nodes
            outputs = {}
            node_results = {}
            
            for node in pipeline.nodes:
                # Create remote function
                @ray.remote
                def execute_node(func, *args):
                    return func(*args)
                
                # Submit node execution to Ray
                future = execute_node.remote(
                    node.func,
                    *[inputs.get(inp) for inp in node.inputs] if inputs else [],
                )
                result = ray.get(future)
                
                node_results[node.name] = {"status": "completed"}
                
                # Update outputs
                if node.outputs:
                    for i, output_name in enumerate(node.outputs):
                        if isinstance(result, tuple):
                            outputs[output_name] = result[i]
                        else:
                            outputs[output_name] = result
                
                # Update inputs for downstream nodes
                if inputs is None:
                    inputs = {}
                inputs.update(outputs)
            
            return RunResult(
                run_id=run_id,
                pipeline_name=pipeline.name,
                status="completed",
                start_time=start_time,
                end_time=datetime.utcnow(),
                outputs=outputs,
                node_results=node_results,
            )
            
        except Exception as e:
            logger.error(f"Ray execution failed: {e}")
            return RunResult(
                run_id=run_id,
                pipeline_name=pipeline.name,
                status="failed",
                error=str(e),
                start_time=start_time,
                end_time=datetime.utcnow(),
                outputs={},
                node_results={},
            )
