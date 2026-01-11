"""
Kubernetes API router for the Agentic Control Panel.

Provides REST endpoints for Kubernetes cluster management,
deployments, and model serving.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.kubernetes import (
    KubernetesClient,
    DeploymentManager,
    MinIOStorage,
    ModelServingManager,
    ClusterInfo,
    NodeInfo,
    DeploymentInfo,
    DeploymentConfig,
    DeploymentStatus,
    ModelDeploymentConfig,
    ModelServingType,
    AgentDeploymentConfig,
    FlowDeploymentConfig,
    ResourceRequirements,
    ClusterConnectionConfig,
)

router = APIRouter(prefix="/api/v1/kubernetes", tags=["kubernetes"])

# Singleton instances
_config: Optional[AgenticConfig] = None
_client: Optional[KubernetesClient] = None
_deployer: Optional[DeploymentManager] = None
_storage: Optional[MinIOStorage] = None
_model_serving: Optional[ModelServingManager] = None


def get_config() -> AgenticConfig:
    """Get or create configuration instance."""
    global _config
    if _config is None:
        _config = AgenticConfig()
    return _config


def get_client() -> KubernetesClient:
    """Get or create Kubernetes client instance."""
    global _client
    if _client is None:
        _client = KubernetesClient(config=get_config())
    return _client


def get_deployer() -> DeploymentManager:
    """Get or create deployment manager instance."""
    global _deployer
    if _deployer is None:
        _deployer = DeploymentManager(client=get_client(), config=get_config())
    return _deployer


def get_storage() -> MinIOStorage:
    """Get or create MinIO storage instance."""
    global _storage
    if _storage is None:
        _storage = MinIOStorage(config=get_config())
    return _storage


def get_model_serving() -> ModelServingManager:
    """Get or create model serving manager instance."""
    global _model_serving
    if _model_serving is None:
        _model_serving = ModelServingManager(client=get_client(), config=get_config())
    return _model_serving


# ============================================================================
# Request/Response Models
# ============================================================================

class ConnectionTestRequest(BaseModel):
    """Request to test cluster connection."""
    kubeconfig_path: Optional[str] = None
    context: Optional[str] = None
    cluster_endpoint: Optional[str] = None
    token: Optional[str] = None
    verify_ssl: bool = True


class ConnectionTestResponse(BaseModel):
    """Response from connection test."""
    connected: bool
    version: Optional[str] = None
    platform: Optional[str] = None
    error: Optional[str] = None


class ScaleRequest(BaseModel):
    """Request to scale a deployment."""
    replicas: int = Field(ge=0, le=100)


class CreateDeploymentRequest(BaseModel):
    """Request to create a deployment."""
    name: str
    namespace: str = "agentic-workloads"
    image: str
    replicas: int = 1
    port: Optional[int] = None
    env: dict[str, str] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)
    cpu_request: str = "100m"
    cpu_limit: str = "1000m"
    memory_request: str = "256Mi"
    memory_limit: str = "1Gi"
    create_service: bool = True
    service_type: str = "ClusterIP"
    deployment_type: str = "custom"
    source_id: Optional[str] = None


class DeployAgentRequest(BaseModel):
    """Request to deploy an agent."""
    agent_id: str
    name: str
    namespace: str = "agentic-workloads"
    replicas: int = 1
    framework: str = "crewai"
    model_endpoint: Optional[str] = None
    tools: list[str] = Field(default_factory=list)
    env_vars: dict[str, str] = Field(default_factory=dict)
    cpu_request: str = "100m"
    cpu_limit: str = "1000m"
    memory_request: str = "256Mi"
    memory_limit: str = "1Gi"


class DeployFlowRequest(BaseModel):
    """Request to deploy a flow."""
    flow_id: str
    name: str
    namespace: str = "agentic-workloads"
    replicas: int = 1
    framework: str = "langgraph"
    model_endpoint: Optional[str] = None
    state_backend: str = "minio"
    env_vars: dict[str, str] = Field(default_factory=dict)
    cpu_request: str = "100m"
    cpu_limit: str = "1000m"
    memory_request: str = "256Mi"
    memory_limit: str = "1Gi"


class DeployModelRequest(BaseModel):
    """Request to deploy an LLM model."""
    name: str
    model_name: str
    serving_type: str = "ollama"
    namespace: str = "model-serving"
    replicas: int = 1
    model_path: Optional[str] = None
    quantization: Optional[str] = None
    context_length: int = 4096
    gpu_layers: Optional[int] = None
    cpu_request: str = "500m"
    cpu_limit: str = "4000m"
    memory_request: str = "2Gi"
    memory_limit: str = "8Gi"
    create_ingress: bool = False
    ingress_host: Optional[str] = None


class StorageTestResponse(BaseModel):
    """Response from storage connection test."""
    connected: bool
    endpoint: Optional[str] = None
    buckets: list[str] = Field(default_factory=list)
    error: Optional[str] = None


class BucketListResponse(BaseModel):
    """Response with list of buckets."""
    buckets: list[str]


class ObjectListResponse(BaseModel):
    """Response with list of objects."""
    objects: list[dict]
    bucket: str
    prefix: Optional[str] = None


# ============================================================================
# Cluster Endpoints
# ============================================================================

@router.get("/cluster", response_model=ClusterInfo)
async def get_cluster_info():
    """Get cluster information and health status."""
    client = get_client()
    return await client.get_cluster_info()


@router.get("/cluster/status")
async def get_cluster_status():
    """Get quick cluster connection status."""
    client = get_client()
    result = await client.test_connection()
    return result


@router.post("/cluster/test", response_model=ConnectionTestResponse)
async def test_cluster_connection(request: ConnectionTestRequest):
    """Test connection to a Kubernetes cluster with custom configuration."""
    conn_config = ClusterConnectionConfig(
        kubeconfig_path=request.kubeconfig_path,
        context=request.context,
        cluster_endpoint=request.cluster_endpoint,
        token=request.token,
        verify_ssl=request.verify_ssl,
    )
    
    test_client = KubernetesClient(
        config=get_config(),
        connection_config=conn_config,
    )
    
    result = await test_client.test_connection()
    return ConnectionTestResponse(**result)


# ============================================================================
# Node Endpoints
# ============================================================================

@router.get("/nodes", response_model=list[NodeInfo])
async def list_nodes():
    """List all cluster nodes."""
    client = get_client()
    return await client.list_nodes()


@router.get("/nodes/{name}", response_model=NodeInfo)
async def get_node(name: str):
    """Get a specific node by name."""
    client = get_client()
    node = await client.get_node(name)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {name} not found")
    return node


# ============================================================================
# Namespace Endpoints
# ============================================================================

@router.get("/namespaces")
async def list_namespaces():
    """List all namespaces."""
    client = get_client()
    namespaces = await client.get_namespaces()
    return {"namespaces": namespaces}


@router.post("/namespaces/{name}")
async def create_namespace(name: str):
    """Create a namespace."""
    client = get_client()
    success = await client.create_namespace(name)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to create namespace {name}")
    return {"status": "created", "namespace": name}


# ============================================================================
# Deployment Endpoints
# ============================================================================

@router.get("/deployments", response_model=list[DeploymentInfo])
async def list_deployments(
    namespace: Optional[str] = Query(None, description="Filter by namespace"),
    deployment_type: Optional[str] = Query(None, description="Filter by type (agent, flow, model)"),
):
    """List all managed deployments."""
    deployer = get_deployer()
    return await deployer.list_deployments(
        namespace=namespace,
        deployment_type=deployment_type,
    )


@router.get("/deployments/{namespace}/{name}", response_model=DeploymentInfo)
async def get_deployment(namespace: str, name: str):
    """Get a specific deployment."""
    deployer = get_deployer()
    deployment = await deployer.get_deployment(name, namespace)
    if not deployment:
        raise HTTPException(status_code=404, detail=f"Deployment {name} not found")
    return deployment


@router.post("/deployments", response_model=DeploymentInfo)
async def create_deployment(request: CreateDeploymentRequest):
    """Create a new deployment."""
    deployer = get_deployer()
    
    resources = ResourceRequirements(
        cpu_request=request.cpu_request,
        cpu_limit=request.cpu_limit,
        memory_request=request.memory_request,
        memory_limit=request.memory_limit,
    )
    
    config = DeploymentConfig(
        name=request.name,
        namespace=request.namespace,
        image=request.image,
        replicas=request.replicas,
        port=request.port,
        env=request.env,
        labels=request.labels,
        resources=resources,
        create_service=request.create_service,
        service_type=request.service_type,
        deployment_type=request.deployment_type,
        source_id=request.source_id,
    )
    
    deployment = await deployer.create_deployment(config)
    if not deployment:
        raise HTTPException(status_code=500, detail="Failed to create deployment")
    return deployment


@router.delete("/deployments/{namespace}/{name}")
async def delete_deployment(
    namespace: str,
    name: str,
    delete_service: bool = Query(True, description="Also delete associated service"),
):
    """Delete a deployment."""
    deployer = get_deployer()
    success = await deployer.delete_deployment(name, namespace, delete_service)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete deployment")
    return {"status": "deleted", "name": name, "namespace": namespace}


@router.post("/deployments/{namespace}/{name}/scale")
async def scale_deployment(namespace: str, name: str, request: ScaleRequest):
    """Scale a deployment."""
    deployer = get_deployer()
    deployment = await deployer.scale_deployment(name, namespace, request.replicas)
    if not deployment:
        raise HTTPException(status_code=500, detail="Failed to scale deployment")
    return deployment


@router.post("/deployments/{namespace}/{name}/restart")
async def restart_deployment(namespace: str, name: str):
    """Restart a deployment."""
    deployer = get_deployer()
    deployment = await deployer.restart_deployment(name, namespace)
    if not deployment:
        raise HTTPException(status_code=500, detail="Failed to restart deployment")
    return deployment


@router.get("/deployments/{namespace}/{name}/status")
async def get_deployment_status(namespace: str, name: str):
    """Get detailed deployment status including pod info."""
    deployer = get_deployer()
    return await deployer.get_deployment_status(name, namespace)


@router.get("/deployments/{namespace}/{name}/logs")
async def get_deployment_logs(
    namespace: str,
    name: str,
    tail_lines: int = Query(100, ge=1, le=10000),
):
    """Get logs from a deployment's pods."""
    deployer = get_deployer()
    logs = await deployer.get_deployment_logs(name, namespace, tail_lines)
    return {"logs": logs}


# ============================================================================
# Agent Deployment Endpoints
# ============================================================================

@router.post("/agents/deploy", response_model=DeploymentInfo)
async def deploy_agent(request: DeployAgentRequest):
    """Deploy an agent to the cluster."""
    deployer = get_deployer()
    
    resources = ResourceRequirements(
        cpu_request=request.cpu_request,
        cpu_limit=request.cpu_limit,
        memory_request=request.memory_request,
        memory_limit=request.memory_limit,
    )
    
    config = AgentDeploymentConfig(
        agent_id=request.agent_id,
        name=request.name,
        namespace=request.namespace,
        replicas=request.replicas,
        framework=request.framework,
        model_endpoint=request.model_endpoint,
        tools=request.tools,
        env_vars=request.env_vars,
        resources=resources,
    )
    
    deployment = await deployer.deploy_agent(config)
    if not deployment:
        raise HTTPException(status_code=500, detail="Failed to deploy agent")
    return deployment


# ============================================================================
# Flow Deployment Endpoints
# ============================================================================

@router.post("/flows/deploy", response_model=DeploymentInfo)
async def deploy_flow(request: DeployFlowRequest):
    """Deploy a flow to the cluster."""
    deployer = get_deployer()
    
    resources = ResourceRequirements(
        cpu_request=request.cpu_request,
        cpu_limit=request.cpu_limit,
        memory_request=request.memory_request,
        memory_limit=request.memory_limit,
    )
    
    config = FlowDeploymentConfig(
        flow_id=request.flow_id,
        name=request.name,
        namespace=request.namespace,
        replicas=request.replicas,
        framework=request.framework,
        model_endpoint=request.model_endpoint,
        state_backend=request.state_backend,
        env_vars=request.env_vars,
        resources=resources,
    )
    
    deployment = await deployer.deploy_flow(config)
    if not deployment:
        raise HTTPException(status_code=500, detail="Failed to deploy flow")
    return deployment


# ============================================================================
# Storage Endpoints
# ============================================================================

@router.get("/storage/status", response_model=StorageTestResponse)
async def get_storage_status():
    """Get MinIO storage connection status."""
    storage = get_storage()
    result = await storage.test_connection()
    return StorageTestResponse(**result)


@router.get("/storage/buckets", response_model=BucketListResponse)
async def list_buckets():
    """List all storage buckets."""
    storage = get_storage()
    buckets = await storage.list_buckets()
    return BucketListResponse(buckets=buckets)


@router.post("/storage/buckets/{name}")
async def create_bucket(name: str):
    """Create a storage bucket."""
    storage = get_storage()
    success = await storage.ensure_bucket(name)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to create bucket {name}")
    return {"status": "created", "bucket": name}


@router.get("/storage/buckets/{bucket}/objects", response_model=ObjectListResponse)
async def list_objects(
    bucket: str,
    prefix: Optional[str] = Query(None, description="Filter by prefix"),
    recursive: bool = Query(False, description="Include subdirectories"),
):
    """List objects in a bucket."""
    storage = get_storage()
    objects = await storage.list_objects(bucket, prefix=prefix, recursive=recursive)
    return ObjectListResponse(objects=objects, bucket=bucket, prefix=prefix)


@router.delete("/storage/buckets/{bucket}/objects/{object_path:path}")
async def delete_object(bucket: str, object_path: str):
    """Delete an object from storage."""
    storage = get_storage()
    success = await storage.delete_object(bucket, object_path)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete object")
    return {"status": "deleted", "bucket": bucket, "object": object_path}


@router.get("/storage/buckets/{bucket}/objects/{object_path:path}/info")
async def get_object_info(bucket: str, object_path: str):
    """Get metadata for an object."""
    storage = get_storage()
    info = await storage.get_object_info(bucket, object_path)
    if not info:
        raise HTTPException(status_code=404, detail="Object not found")
    return info


@router.get("/storage/buckets/{bucket}/objects/{object_path:path}/url")
async def get_presigned_url(
    bucket: str,
    object_path: str,
    expires_hours: int = Query(1, ge=1, le=168),
):
    """Generate a presigned URL for an object."""
    storage = get_storage()
    url = await storage.get_presigned_url(bucket, object_path, expires_hours)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate URL")
    return {"url": url, "expires_hours": expires_hours}


# ============================================================================
# Model Serving Endpoints
# ============================================================================

@router.get("/models", response_model=list[DeploymentInfo])
async def list_model_deployments(
    namespace: Optional[str] = Query(None, description="Filter by namespace"),
):
    """List all model deployments."""
    manager = get_model_serving()
    return await manager.list_model_deployments(namespace=namespace)


@router.get("/models/{name}", response_model=DeploymentInfo)
async def get_model_deployment(
    name: str,
    namespace: Optional[str] = Query(None, description="Namespace"),
):
    """Get a specific model deployment."""
    manager = get_model_serving()
    deployment = await manager.get_model_deployment(name, namespace)
    if not deployment:
        raise HTTPException(status_code=404, detail=f"Model deployment {name} not found")
    return deployment


@router.post("/models/deploy", response_model=DeploymentInfo)
async def deploy_model(request: DeployModelRequest):
    """Deploy an LLM model to the cluster."""
    manager = get_model_serving()
    
    # Map string to enum
    serving_type_map = {
        "ollama": ModelServingType.OLLAMA,
        "vllm": ModelServingType.VLLM,
        "tgi": ModelServingType.TGI,
    }
    serving_type = serving_type_map.get(request.serving_type.lower(), ModelServingType.OLLAMA)
    
    resources = ResourceRequirements(
        cpu_request=request.cpu_request,
        cpu_limit=request.cpu_limit,
        memory_request=request.memory_request,
        memory_limit=request.memory_limit,
    )
    
    config = ModelDeploymentConfig(
        name=request.name,
        model_name=request.model_name,
        serving_type=serving_type,
        namespace=request.namespace,
        replicas=request.replicas,
        model_path=request.model_path,
        quantization=request.quantization,
        context_length=request.context_length,
        gpu_layers=request.gpu_layers,
        resources=resources,
        create_ingress=request.create_ingress,
        ingress_host=request.ingress_host,
    )
    
    deployment = await manager.deploy_model(config)
    if not deployment:
        raise HTTPException(status_code=500, detail="Failed to deploy model")
    
    # Create ingress if requested
    if request.create_ingress and request.ingress_host:
        await manager.create_ingress(request.name, request.ingress_host, request.namespace)
    
    return deployment


@router.delete("/models/{name}")
async def delete_model_deployment(
    name: str,
    namespace: Optional[str] = Query(None, description="Namespace"),
):
    """Delete a model deployment."""
    manager = get_model_serving()
    success = await manager.delete_model_deployment(name, namespace)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete model deployment")
    return {"status": "deleted", "name": name}


@router.post("/models/{name}/scale")
async def scale_model_deployment(
    name: str,
    request: ScaleRequest,
    namespace: Optional[str] = Query(None, description="Namespace"),
):
    """Scale a model deployment."""
    manager = get_model_serving()
    deployment = await manager.scale_model_deployment(name, request.replicas, namespace)
    if not deployment:
        raise HTTPException(status_code=500, detail="Failed to scale model deployment")
    return deployment


@router.get("/models/{name}/endpoint")
async def get_model_endpoint(
    name: str,
    namespace: Optional[str] = Query(None, description="Namespace"),
):
    """Get the endpoint URL for a model deployment."""
    manager = get_model_serving()
    endpoint = await manager.get_model_endpoint(name, namespace)
    external = await manager.get_model_external_endpoint(name, namespace)
    
    if not endpoint:
        raise HTTPException(status_code=404, detail=f"Model deployment {name} not found")
    
    return {
        "internal_endpoint": endpoint,
        "external_endpoint": external,
    }


@router.post("/models/{name}/use")
async def set_model_as_code_assistant(
    name: str,
    namespace: Optional[str] = Query(None, description="Namespace"),
):
    """Configure a model deployment to be used as the code assistant."""
    manager = get_model_serving()
    result = await manager.set_as_code_assistant(name, namespace)
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return result


@router.post("/models/{name}/pull")
async def pull_ollama_model(
    name: str,
    model_name: str = Query(..., description="Model to pull"),
    namespace: Optional[str] = Query(None, description="Namespace"),
):
    """Pull a model in an Ollama deployment."""
    manager = get_model_serving()
    success = await manager.pull_ollama_model(name, model_name, namespace)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to initiate model pull")
    
    return {
        "status": "initiated",
        "deployment": name,
        "model": model_name,
        "message": "Model pull initiated. Check deployment logs for progress.",
    }
