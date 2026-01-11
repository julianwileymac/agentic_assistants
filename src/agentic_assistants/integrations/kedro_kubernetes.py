"""
Kedro Kubernetes Integration.

Provides runners and utilities for executing Kedro pipelines on Kubernetes,
with support for Argo Workflows and distributed data processing.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.kubernetes.client import KubernetesClient
from agentic_assistants.kubernetes.storage import MinIOStorage

logger = logging.getLogger(__name__)


class KedroKubernetesRunner:
    """
    Run Kedro pipelines on Kubernetes.
    
    This runner executes Kedro pipeline nodes as Kubernetes Jobs,
    enabling distributed execution across the cluster.
    
    Features:
    - Execute pipeline nodes as K8s Jobs
    - S3/MinIO data catalog integration
    - Argo Workflows support for complex DAGs
    - Resource management per node
    
    Example:
        >>> runner = KedroKubernetesRunner()
        >>> result = await runner.run(
        ...     pipeline_name="data_processing",
        ...     catalog=catalog,
        ...     namespace="kedro-pipelines"
        ... )
    """

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        namespace: Optional[str] = None,
        image: str = "agentic/kedro-runner:latest",
        use_argo: bool = False,
    ):
        """
        Initialize the Kedro Kubernetes runner.
        
        Args:
            config: Agentic configuration
            namespace: Kubernetes namespace for jobs
            image: Container image for job execution
            use_argo: Use Argo Workflows for orchestration
        """
        self.config = config or AgenticConfig()
        self.namespace = namespace or self.config.kubernetes.default_deploy_namespace
        self.image = image
        self.use_argo = use_argo
        
        self._client: Optional[KubernetesClient] = None
        self._storage: Optional[MinIOStorage] = None

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
        pipeline_name: str,
        catalog: Dict[str, Any],
        run_id: Optional[str] = None,
        node_names: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        env: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run a Kedro pipeline on Kubernetes.
        
        Args:
            pipeline_name: Name of the pipeline to run
            catalog: Data catalog configuration
            run_id: Optional run identifier
            node_names: Specific nodes to run (runs all if None)
            tags: Filter nodes by tags
            env: Kedro environment
        
        Returns:
            Run result with status and outputs
        """
        run_id = run_id or f"kedro-{pipeline_name}-{int(datetime.utcnow().timestamp())}"
        
        logger.info(f"Starting Kedro pipeline run: {run_id}")
        
        # Ensure namespace exists
        await self.client.create_namespace(self.namespace)
        
        if self.use_argo:
            return await self._run_with_argo(
                pipeline_name, catalog, run_id, node_names, tags, env
            )
        else:
            return await self._run_with_jobs(
                pipeline_name, catalog, run_id, node_names, tags, env
            )

    async def _run_with_jobs(
        self,
        pipeline_name: str,
        catalog: Dict[str, Any],
        run_id: str,
        node_names: Optional[List[str]],
        tags: Optional[List[str]],
        env: Optional[str],
    ) -> Dict[str, Any]:
        """Execute pipeline using Kubernetes Jobs."""
        try:
            from kubernetes import client
            
            # Store catalog configuration in MinIO
            await self._store_catalog(run_id, catalog)
            
            # Build job specification
            job = self._build_kedro_job(
                run_id=run_id,
                pipeline_name=pipeline_name,
                node_names=node_names,
                tags=tags,
                env=env,
            )
            
            # Create job
            batch_api = client.BatchV1Api()
            batch_api.create_namespaced_job(
                namespace=self.namespace,
                body=job,
            )
            
            logger.info(f"Created Kedro job: {run_id}")
            
            # Wait for completion
            result = await self._wait_for_job(run_id)
            
            return {
                "run_id": run_id,
                "pipeline_name": pipeline_name,
                "status": result.get("status", "unknown"),
                "outputs": result.get("outputs", {}),
            }
            
        except ImportError:
            logger.error("kubernetes library not installed")
            return {
                "run_id": run_id,
                "pipeline_name": pipeline_name,
                "status": "failed",
                "error": "kubernetes library not installed",
            }
        except Exception as e:
            logger.error(f"Failed to run Kedro pipeline: {e}")
            return {
                "run_id": run_id,
                "pipeline_name": pipeline_name,
                "status": "failed",
                "error": str(e),
            }

    async def _run_with_argo(
        self,
        pipeline_name: str,
        catalog: Dict[str, Any],
        run_id: str,
        node_names: Optional[List[str]],
        tags: Optional[List[str]],
        env: Optional[str],
    ) -> Dict[str, Any]:
        """Execute pipeline using Argo Workflows."""
        try:
            # Store catalog configuration
            await self._store_catalog(run_id, catalog)
            
            # Build Argo Workflow
            workflow = self._build_argo_workflow(
                run_id=run_id,
                pipeline_name=pipeline_name,
                node_names=node_names,
                tags=tags,
                env=env,
            )
            
            # Submit workflow using custom objects API
            custom_api = self.client._custom_api
            if custom_api is None:
                raise RuntimeError("Kubernetes client not initialized")
            
            custom_api.create_namespaced_custom_object(
                group="argoproj.io",
                version="v1alpha1",
                namespace=self.namespace,
                plural="workflows",
                body=workflow,
            )
            
            logger.info(f"Created Argo workflow: {run_id}")
            
            return {
                "run_id": run_id,
                "pipeline_name": pipeline_name,
                "status": "submitted",
                "workflow_type": "argo",
            }
            
        except Exception as e:
            logger.error(f"Failed to submit Argo workflow: {e}")
            return {
                "run_id": run_id,
                "pipeline_name": pipeline_name,
                "status": "failed",
                "error": str(e),
            }

    def _build_kedro_job(
        self,
        run_id: str,
        pipeline_name: str,
        node_names: Optional[List[str]],
        tags: Optional[List[str]],
        env: Optional[str],
    ):
        """Build Kubernetes Job specification for Kedro."""
        from kubernetes import client
        
        # Build command arguments
        args = ["kedro", "run", "--pipeline", pipeline_name]
        
        if node_names:
            args.extend(["--nodes", ",".join(node_names)])
        if tags:
            args.extend(["--tags", ",".join(tags)])
        if env:
            args.extend(["--env", env])
        
        # Build environment variables
        env_vars = [
            client.V1EnvVar(name="KEDRO_RUN_ID", value=run_id),
            client.V1EnvVar(name="MINIO_ENDPOINT", value=self.config.minio.endpoint),
            client.V1EnvVar(name="MINIO_BUCKET", value=self.config.minio.default_bucket),
        ]
        
        if self.config.minio.access_key:
            env_vars.append(client.V1EnvVar(name="MINIO_ACCESS_KEY", value=self.config.minio.access_key))
        if self.config.minio.secret_key:
            env_vars.append(client.V1EnvVar(name="MINIO_SECRET_KEY", value=self.config.minio.secret_key))
        
        # Build container
        container = client.V1Container(
            name="kedro-runner",
            image=self.image,
            args=args,
            env=env_vars,
            resources=client.V1ResourceRequirements(
                requests={
                    "cpu": self.config.kubernetes.default_cpu_request,
                    "memory": self.config.kubernetes.default_memory_request,
                },
                limits={
                    "cpu": self.config.kubernetes.default_cpu_limit,
                    "memory": self.config.kubernetes.default_memory_limit,
                },
            ),
        )
        
        # Build job
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(
                name=run_id,
                namespace=self.namespace,
                labels={
                    "agentic.io/type": "kedro-pipeline",
                    "agentic.io/pipeline": pipeline_name,
                    "agentic.io/run-id": run_id,
                },
            ),
            spec=client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    spec=client.V1PodSpec(
                        containers=[container],
                        restart_policy="Never",
                    ),
                ),
                backoff_limit=0,
                ttl_seconds_after_finished=3600,
            ),
        )
        
        return job

    def _build_argo_workflow(
        self,
        run_id: str,
        pipeline_name: str,
        node_names: Optional[List[str]],
        tags: Optional[List[str]],
        env: Optional[str],
    ) -> Dict[str, Any]:
        """Build Argo Workflow specification for Kedro."""
        # Build command arguments
        args = ["kedro", "run", "--pipeline", pipeline_name]
        
        if node_names:
            args.extend(["--nodes", ",".join(node_names)])
        if tags:
            args.extend(["--tags", ",".join(tags)])
        if env:
            args.extend(["--env", env])
        
        workflow = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": {
                "name": run_id,
                "namespace": self.namespace,
                "labels": {
                    "agentic.io/type": "kedro-pipeline",
                    "agentic.io/pipeline": pipeline_name,
                },
            },
            "spec": {
                "entrypoint": "kedro-run",
                "templates": [
                    {
                        "name": "kedro-run",
                        "container": {
                            "image": self.image,
                            "args": args,
                            "env": [
                                {"name": "KEDRO_RUN_ID", "value": run_id},
                                {"name": "MINIO_ENDPOINT", "value": self.config.minio.endpoint},
                                {"name": "MINIO_BUCKET", "value": self.config.minio.default_bucket},
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": self.config.kubernetes.default_cpu_request,
                                    "memory": self.config.kubernetes.default_memory_request,
                                },
                                "limits": {
                                    "cpu": self.config.kubernetes.default_cpu_limit,
                                    "memory": self.config.kubernetes.default_memory_limit,
                                },
                            },
                        },
                    },
                ],
            },
        }
        
        return workflow

    async def _store_catalog(self, run_id: str, catalog: Dict[str, Any]) -> None:
        """Store catalog configuration in MinIO."""
        await self.storage.upload_json(
            self.config.minio.default_bucket,
            f"kedro-runs/{run_id}/catalog.json",
            catalog,
        )

    async def _wait_for_job(
        self,
        job_name: str,
        timeout: int = 3600,
        poll_interval: int = 10,
    ) -> Dict[str, Any]:
        """Wait for a job to complete."""
        import asyncio
        import time
        
        try:
            from kubernetes import client
            
            batch_api = client.BatchV1Api()
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                job = batch_api.read_namespaced_job(
                    name=job_name,
                    namespace=self.namespace,
                )
                
                if job.status.succeeded:
                    return {"status": "completed", "outputs": {}}
                
                if job.status.failed:
                    return {"status": "failed", "error": "Job execution failed"}
                
                await asyncio.sleep(poll_interval)
            
            return {"status": "timeout", "error": f"Job timed out after {timeout}s"}
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def list_runs(
        self,
        pipeline_name: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List Kedro pipeline runs."""
        label_selector = "agentic.io/type=kedro-pipeline"
        if pipeline_name:
            label_selector += f",agentic.io/pipeline={pipeline_name}"
        
        try:
            from kubernetes import client
            
            batch_api = client.BatchV1Api()
            jobs = batch_api.list_namespaced_job(
                namespace=self.namespace,
                label_selector=label_selector,
                limit=limit,
            )
            
            runs = []
            for job in jobs.items:
                status = "running"
                if job.status.succeeded:
                    status = "completed"
                elif job.status.failed:
                    status = "failed"
                
                runs.append({
                    "run_id": job.metadata.name,
                    "pipeline_name": job.metadata.labels.get("agentic.io/pipeline"),
                    "status": status,
                    "created_at": job.metadata.creation_timestamp.isoformat(),
                })
            
            return runs
            
        except Exception as e:
            logger.error(f"Failed to list runs: {e}")
            return []

    async def get_run_logs(
        self,
        run_id: str,
        tail_lines: int = 100,
    ) -> str:
        """Get logs for a Kedro run."""
        try:
            # Get pods for the job
            pods = await self.client.list_pods(
                namespace=self.namespace,
                label_selector=f"job-name={run_id}",
            )
            
            if not pods:
                return "No pods found for run"
            
            # Get logs from first pod
            return await self.client.get_pod_logs(
                name=pods[0].name,
                namespace=self.namespace,
                tail_lines=tail_lines,
            )
            
        except Exception as e:
            return f"Error fetching logs: {e}"


class S3DataCatalog:
    """
    S3/MinIO-compatible data catalog for Kedro.
    
    Provides dataset configurations that work with MinIO storage
    for distributed pipeline execution.
    """

    def __init__(self, config: Optional[AgenticConfig] = None):
        self.config = config or AgenticConfig()

    def get_s3_credentials(self) -> Dict[str, Any]:
        """Get S3 credentials for catalog configuration."""
        return {
            "client_kwargs": {
                "endpoint_url": f"http://{self.config.minio.endpoint}",
                "aws_access_key_id": self.config.minio.access_key,
                "aws_secret_access_key": self.config.minio.secret_key,
            },
        }

    def create_parquet_dataset(
        self,
        name: str,
        path: str,
        bucket: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Parquet dataset configuration."""
        bucket = bucket or self.config.minio.default_bucket
        
        return {
            name: {
                "type": "pandas.ParquetDataset",
                "filepath": f"s3://{bucket}/{path}",
                "credentials": "minio",
            }
        }

    def create_csv_dataset(
        self,
        name: str,
        path: str,
        bucket: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a CSV dataset configuration."""
        bucket = bucket or self.config.minio.default_bucket
        
        return {
            name: {
                "type": "pandas.CSVDataset",
                "filepath": f"s3://{bucket}/{path}",
                "credentials": "minio",
            }
        }

    def create_json_dataset(
        self,
        name: str,
        path: str,
        bucket: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a JSON dataset configuration."""
        bucket = bucket or self.config.minio.default_bucket
        
        return {
            name: {
                "type": "json.JSONDataset",
                "filepath": f"s3://{bucket}/{path}",
                "credentials": "minio",
            }
        }

    def create_pickle_dataset(
        self,
        name: str,
        path: str,
        bucket: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Pickle dataset configuration."""
        bucket = bucket or self.config.minio.default_bucket
        
        return {
            name: {
                "type": "pickle.PickleDataset",
                "filepath": f"s3://{bucket}/{path}",
                "credentials": "minio",
            }
        }

    def generate_catalog(
        self,
        datasets: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate a complete catalog configuration.
        
        Args:
            datasets: List of dataset configurations
        
        Returns:
            Complete catalog dict with credentials
        """
        catalog = {}
        
        # Add credentials
        catalog["_credentials"] = {
            "minio": self.get_s3_credentials(),
        }
        
        # Add datasets
        for dataset in datasets:
            catalog.update(dataset)
        
        return catalog
