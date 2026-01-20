"""
ML Deployments API Router.

This module provides REST endpoints for ML model deployment tracking:
- CRUD operations for deployments
- Deployment status management
- Health monitoring
- Traffic management for canary/blue-green deployments
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.core.mlflow_tracker import MLFlowManager, DeploymentTarget, ModelStage
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ml-deployments", tags=["ml-deployments"])


# === Request/Response Models ===

class DeploymentCreate(BaseModel):
    """Request to create a new ML deployment."""
    name: str = Field(..., description="Deployment name")
    model_name: str = Field(..., description="Registered model name")
    model_version: str = Field(..., description="Model version")
    target_type: str = Field(..., description="Deployment target (local, docker, kubernetes, sagemaker)")
    target_endpoint: str = Field(default="", description="Target endpoint URL")
    target_config: dict = Field(default_factory=dict, description="Target-specific configuration")
    project_id: Optional[str] = Field(default=None, description="Associated project ID")
    mlflow_run_id: Optional[str] = Field(default=None, description="MLFlow run ID")
    cpu_limit: Optional[str] = Field(default=None, description="CPU limit")
    memory_limit: Optional[str] = Field(default=None, description="Memory limit")
    gpu_enabled: bool = Field(default=False, description="Enable GPU")
    replicas: int = Field(default=1, ge=1, description="Number of replicas")
    tags: List[str] = Field(default_factory=list, description="Tags")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class DeploymentUpdate(BaseModel):
    """Request to update a deployment."""
    name: Optional[str] = None
    target_endpoint: Optional[str] = None
    target_config: Optional[dict] = None
    status: Optional[str] = None
    cpu_limit: Optional[str] = None
    memory_limit: Optional[str] = None
    gpu_enabled: Optional[bool] = None
    replicas: Optional[int] = None
    traffic_percentage: Optional[int] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class DeploymentResponse(BaseModel):
    """Deployment response model."""
    id: str
    name: str
    model_name: str
    model_version: str
    model_uri: Optional[str]
    model_framework: Optional[str]
    target_type: str
    target_endpoint: str
    target_config: dict
    status: str
    health_status: str
    last_health_check: Optional[str]
    cpu_limit: Optional[str]
    memory_limit: Optional[str]
    gpu_enabled: bool
    replicas: int
    traffic_percentage: int
    parent_deployment_id: Optional[str]
    request_count: int
    avg_latency_ms: Optional[float]
    error_rate: Optional[float]
    project_id: Optional[str]
    mlflow_run_id: Optional[str]
    deployed_at: Optional[str]
    stopped_at: Optional[str]
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: dict


class DeploymentsListResponse(BaseModel):
    """Response containing list of deployments."""
    items: List[DeploymentResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class DeploymentHealthResponse(BaseModel):
    """Deployment health check response."""
    deployment_id: str
    status: str
    health_status: str
    last_check: str
    latency_ms: Optional[float]
    details: dict


class DeploymentMetricsResponse(BaseModel):
    """Deployment metrics response."""
    deployment_id: str
    request_count: int
    avg_latency_ms: Optional[float]
    error_rate: Optional[float]
    cpu_usage: Optional[float]
    memory_usage: Optional[float]
    time_range: str


# === Helper Functions ===

def _get_store() -> ControlPanelStore:
    """Get the control panel store instance."""
    return ControlPanelStore.get_instance()


VALID_TARGET_TYPES = {"local", "docker", "kubernetes", "sagemaker", "azure_ml"}
VALID_STATUSES = {"pending", "deploying", "active", "failed", "stopped", "scaling"}


# === Endpoints ===

@router.get("", response_model=DeploymentsListResponse)
async def list_deployments(
    project_id: Optional[str] = Query(None, description="Filter by project"),
    status: Optional[str] = Query(None, description="Filter by status"),
    model_name: Optional[str] = Query(None, description="Filter by model name"),
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> DeploymentsListResponse:
    """List all ML deployments with optional filtering."""
    store = _get_store()
    
    # Build filter criteria
    filters = {}
    if project_id:
        filters["project_id"] = project_id
    if status:
        filters["status"] = status
    if model_name:
        filters["model_name"] = model_name
    if target_type:
        filters["target_type"] = target_type
    
    try:
        deployments, total = store.list_ml_deployments(
            filters=filters, page=page, limit=limit
        )
        
        return DeploymentsListResponse(
            items=[DeploymentResponse(**d.to_dict()) for d in deployments],
            total=total,
            page=page,
            page_size=limit,
            has_more=(page * limit) < total,
        )
    except AttributeError:
        # Store doesn't have this method yet, return empty
        return DeploymentsListResponse(
            items=[],
            total=0,
            page=page,
            page_size=limit,
            has_more=False,
        )


@router.post("", response_model=DeploymentResponse)
async def create_deployment(request: DeploymentCreate) -> DeploymentResponse:
    """Create a new ML deployment."""
    store = _get_store()
    
    if request.target_type not in VALID_TARGET_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target type. Must be one of: {', '.join(VALID_TARGET_TYPES)}"
        )
    
    try:
        deployment = store.create_ml_deployment(
            name=request.name,
            model_name=request.model_name,
            model_version=request.model_version,
            target_type=request.target_type,
            target_endpoint=request.target_endpoint,
            target_config=request.target_config,
            project_id=request.project_id,
            mlflow_run_id=request.mlflow_run_id,
            cpu_limit=request.cpu_limit,
            memory_limit=request.memory_limit,
            gpu_enabled=request.gpu_enabled,
            replicas=request.replicas,
            tags=request.tags,
            metadata=request.metadata,
        )
        return DeploymentResponse(**deployment.to_dict())
    except AttributeError:
        raise HTTPException(
            status_code=501,
            detail="ML deployment storage not implemented"
        )
    except Exception as e:
        logger.error(f"Failed to create deployment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(deployment_id: str) -> DeploymentResponse:
    """Get a deployment by ID."""
    store = _get_store()
    
    try:
        deployment = store.get_ml_deployment(deployment_id)
        if deployment is None:
            raise HTTPException(status_code=404, detail="Deployment not found")
        return DeploymentResponse(**deployment.to_dict())
    except AttributeError:
        raise HTTPException(status_code=404, detail="Deployment not found")


@router.put("/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(deployment_id: str, request: DeploymentUpdate) -> DeploymentResponse:
    """Update a deployment."""
    store = _get_store()
    
    if request.status and request.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
        )
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    
    try:
        deployment = store.update_ml_deployment(deployment_id, **update_data)
        if deployment is None:
            raise HTTPException(status_code=404, detail="Deployment not found")
        return DeploymentResponse(**deployment.to_dict())
    except AttributeError:
        raise HTTPException(status_code=404, detail="Deployment not found")


@router.delete("/{deployment_id}")
async def delete_deployment(deployment_id: str) -> dict:
    """Delete a deployment."""
    store = _get_store()
    
    try:
        if not store.delete_ml_deployment(deployment_id):
            raise HTTPException(status_code=404, detail="Deployment not found")
        return {"status": "deleted", "id": deployment_id}
    except AttributeError:
        raise HTTPException(status_code=404, detail="Deployment not found")


# === Deployment Lifecycle ===

@router.post("/{deployment_id}/deploy")
async def trigger_deploy(deployment_id: str) -> dict:
    """Trigger deployment to target environment."""
    store = _get_store()
    
    try:
        deployment = store.get_ml_deployment(deployment_id)
        if deployment is None:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        # Update status to deploying
        store.update_ml_deployment(deployment_id, status="deploying")
        
        # Use MLFlow manager for actual deployment
        manager = MLFlowManager()
        target = DeploymentTarget(deployment.target_type)
        
        deploy_info = manager.deploy_model(
            model_name=deployment.model_name,
            target=target,
            version=deployment.model_version,
            config=deployment.target_config,
        )
        
        # Update deployment with result
        new_status = "active" if deploy_info.status == "ready" else deploy_info.status
        store.update_ml_deployment(
            deployment_id,
            status=new_status,
            target_endpoint=deploy_info.endpoint or deployment.target_endpoint,
            target_config={**deployment.target_config, **deploy_info.config},
            deployed_at=datetime.utcnow().isoformat(),
        )
        
        return {
            "status": "deployment_triggered",
            "deployment_id": deployment_id,
            "deploy_status": deploy_info.status,
            "endpoint": deploy_info.endpoint,
        }
        
    except AttributeError:
        raise HTTPException(status_code=501, detail="Deployment not implemented")
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        store.update_ml_deployment(deployment_id, status="failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{deployment_id}/stop")
async def stop_deployment(deployment_id: str) -> dict:
    """Stop a running deployment."""
    store = _get_store()
    
    try:
        deployment = store.get_ml_deployment(deployment_id)
        if deployment is None:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        # Update status
        store.update_ml_deployment(
            deployment_id,
            status="stopped",
            stopped_at=datetime.utcnow().isoformat(),
        )
        
        return {
            "status": "stopped",
            "deployment_id": deployment_id,
        }
        
    except AttributeError:
        raise HTTPException(status_code=404, detail="Deployment not found")


@router.post("/{deployment_id}/scale")
async def scale_deployment(
    deployment_id: str,
    replicas: int = Query(..., ge=0, description="Number of replicas"),
) -> dict:
    """Scale a deployment."""
    store = _get_store()
    
    try:
        deployment = store.get_ml_deployment(deployment_id)
        if deployment is None:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        # Update replicas
        store.update_ml_deployment(deployment_id, replicas=replicas)
        
        return {
            "status": "scaling",
            "deployment_id": deployment_id,
            "replicas": replicas,
        }
        
    except AttributeError:
        raise HTTPException(status_code=404, detail="Deployment not found")


# === Health & Monitoring ===

@router.get("/{deployment_id}/health", response_model=DeploymentHealthResponse)
async def check_deployment_health(deployment_id: str) -> DeploymentHealthResponse:
    """Check deployment health status."""
    store = _get_store()
    
    try:
        deployment = store.get_ml_deployment(deployment_id)
        if deployment is None:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        # Perform health check
        health_status = "unknown"
        latency_ms = None
        details = {}
        
        if deployment.target_endpoint:
            import httpx
            import time
            
            try:
                start = time.time()
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(f"{deployment.target_endpoint}/health")
                    latency_ms = (time.time() - start) * 1000
                    
                    if response.status_code == 200:
                        health_status = "healthy"
                    else:
                        health_status = "unhealthy"
                    
                    details = {
                        "status_code": response.status_code,
                        "endpoint": deployment.target_endpoint,
                    }
            except Exception as e:
                health_status = "unhealthy"
                details = {"error": str(e)}
        
        # Update deployment health status
        store.update_ml_deployment(
            deployment_id,
            health_status=health_status,
            last_health_check=datetime.utcnow().isoformat(),
        )
        
        return DeploymentHealthResponse(
            deployment_id=deployment_id,
            status=deployment.status,
            health_status=health_status,
            last_check=datetime.utcnow().isoformat(),
            latency_ms=latency_ms,
            details=details,
        )
        
    except AttributeError:
        raise HTTPException(status_code=404, detail="Deployment not found")


@router.get("/{deployment_id}/metrics", response_model=DeploymentMetricsResponse)
async def get_deployment_metrics(
    deployment_id: str,
    time_range: str = Query("1h", description="Time range (1h, 24h, 7d, 30d)"),
) -> DeploymentMetricsResponse:
    """Get deployment metrics."""
    store = _get_store()
    
    try:
        deployment = store.get_ml_deployment(deployment_id)
        if deployment is None:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        return DeploymentMetricsResponse(
            deployment_id=deployment_id,
            request_count=deployment.request_count,
            avg_latency_ms=deployment.avg_latency_ms,
            error_rate=deployment.error_rate,
            cpu_usage=None,  # Would come from monitoring system
            memory_usage=None,
            time_range=time_range,
        )
        
    except AttributeError:
        raise HTTPException(status_code=404, detail="Deployment not found")


# === Traffic Management ===

@router.post("/{deployment_id}/traffic")
async def update_traffic(
    deployment_id: str,
    percentage: int = Query(..., ge=0, le=100, description="Traffic percentage"),
) -> dict:
    """Update traffic percentage for canary/blue-green deployments."""
    store = _get_store()
    
    try:
        deployment = store.get_ml_deployment(deployment_id)
        if deployment is None:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        # Update traffic percentage
        store.update_ml_deployment(deployment_id, traffic_percentage=percentage)
        
        return {
            "status": "traffic_updated",
            "deployment_id": deployment_id,
            "traffic_percentage": percentage,
        }
        
    except AttributeError:
        raise HTTPException(status_code=404, detail="Deployment not found")


# === MLFlow Integration ===

@router.post("/from-mlflow")
async def create_from_mlflow(
    model_name: str = Query(..., description="MLFlow model name"),
    version: Optional[str] = Query(None, description="Model version"),
    stage: Optional[str] = Query(None, description="Model stage (Production, Staging)"),
    target_type: str = Query("local", description="Deployment target"),
    project_id: Optional[str] = Query(None, description="Project ID"),
) -> dict:
    """Create a deployment from an MLFlow registered model."""
    store = _get_store()
    manager = MLFlowManager()
    
    # Get model info from MLFlow
    if stage:
        model_stage = ModelStage(stage)
        versions = manager.get_model_versions(model_name, stages=[model_stage])
        if not versions:
            raise HTTPException(
                status_code=404,
                detail=f"No model found for {model_name} at stage {stage}"
            )
        model_version = versions[0]
    elif version:
        versions = manager.get_model_versions(model_name)
        model_version = next((v for v in versions if v.version == version), None)
        if not model_version:
            raise HTTPException(
                status_code=404,
                detail=f"Model version {version} not found"
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="Must specify either 'version' or 'stage'"
        )
    
    # Create deployment
    try:
        deployment = store.create_ml_deployment(
            name=f"{model_name}-{model_version.version}",
            model_name=model_name,
            model_version=model_version.version,
            target_type=target_type,
            mlflow_run_id=model_version.run_id,
            project_id=project_id,
            metadata={
                "source": model_version.source,
                "stage": model_version.stage.value,
            },
        )
        
        return {
            "status": "created",
            "deployment_id": deployment.id,
            "model_name": model_name,
            "model_version": model_version.version,
        }
        
    except AttributeError:
        raise HTTPException(status_code=501, detail="Deployment storage not implemented")


@router.get("/models/registered")
async def list_registered_models() -> dict:
    """List all registered models available for deployment."""
    manager = MLFlowManager()
    models = manager.list_registered_models()
    
    return {
        "models": models,
        "total": len(models),
    }
