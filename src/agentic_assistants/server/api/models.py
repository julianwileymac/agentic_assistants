"""
Custom Models API routes.

This module provides REST API endpoints for managing custom trained models,
including registration, deployment, and metadata management.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.training.config import CustomModelInfo, TrainingMethod
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/models/custom", tags=["models"])

# Global registry storage
_models_registry_path = Path("./data/models/registry.json")
_models: Dict[str, CustomModelInfo] = {}


def _load_models():
    """Load models from registry file."""
    global _models
    if _models_registry_path.exists():
        try:
            with open(_models_registry_path, "r") as f:
                data = json.load(f)
            for model_data in data.get("models", []):
                model = CustomModelInfo(
                    id=model_data["id"],
                    name=model_data["name"],
                    base_model=model_data["base_model"],
                    training_method=TrainingMethod(model_data.get("training_method", "lora")),
                    training_job_id=model_data.get("training_job_id", ""),
                    local_path=model_data.get("local_path", ""),
                    hf_repo_id=model_data.get("hf_repo_id"),
                    status=model_data.get("status", "created"),
                    metrics=model_data.get("metrics", {}),
                    training_config=model_data.get("training_config"),
                    created_at=model_data.get("created_at"),
                    updated_at=model_data.get("updated_at"),
                    tags=model_data.get("tags", []),
                    description=model_data.get("description"),
                    mlflow_run_id=model_data.get("mlflow_run_id"),
                    mlflow_model_uri=model_data.get("mlflow_model_uri"),
                )
                _models[model.id] = model
        except Exception as e:
            logger.warning(f"Failed to load models registry: {e}")


def _save_models():
    """Save models to registry file."""
    _models_registry_path.parent.mkdir(parents=True, exist_ok=True)
    data = {"models": [m.to_dict() for m in _models.values()]}
    with open(_models_registry_path, "w") as f:
        json.dump(data, f, indent=2)


# Initialize on module load
_load_models()


# ============================================================================
# Request/Response Models
# ============================================================================

class RegisterModelRequest(BaseModel):
    """Request to register a custom model."""
    
    name: str = Field(..., description="Model name")
    base_model: str = Field(..., description="Base model used for training")
    training_method: str = Field(default="lora", description="Training method used")
    training_job_id: Optional[str] = Field(None, description="Associated training job ID")
    local_path: str = Field(..., description="Path to model files")
    hf_repo_id: Optional[str] = Field(None, description="HuggingFace repository ID")
    description: Optional[str] = Field(None, description="Model description")
    tags: List[str] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)
    mlflow_run_id: Optional[str] = Field(None, description="MLFlow run ID")


class CustomModelResponse(BaseModel):
    """Custom model response."""
    
    id: str
    name: str
    base_model: str
    training_method: str
    training_job_id: Optional[str]
    local_path: str
    hf_repo_id: Optional[str]
    status: str
    metrics: Dict[str, float]
    created_at: Optional[str]
    updated_at: Optional[str]
    tags: List[str]
    description: Optional[str]
    mlflow_run_id: Optional[str]
    mlflow_model_uri: Optional[str]


class UpdateModelRequest(BaseModel):
    """Request to update a model."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    hf_repo_id: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None


class DeployModelRequest(BaseModel):
    """Request to deploy a model."""
    
    target: str = Field(default="ollama", description="Deployment target: ollama, vllm, tgi")
    model_name: Optional[str] = Field(None, description="Name for deployed model")
    
    # Ollama-specific options
    quantization: Optional[str] = Field(None, description="Quantization for GGUF conversion")
    
    # vLLM/TGI options
    gpu_memory_utilization: float = Field(default=0.9, description="GPU memory utilization")
    max_model_len: Optional[int] = Field(None, description="Maximum model length")


class ModelDeploymentResponse(BaseModel):
    """Model deployment response."""
    
    success: bool
    model_id: str
    deployment_target: str
    endpoint: Optional[str] = None
    message: str
    details: Dict[str, Any] = {}


# ============================================================================
# Endpoints
# ============================================================================

@router.post("", response_model=CustomModelResponse)
async def register_custom_model(request: RegisterModelRequest) -> CustomModelResponse:
    """
    Register a new custom model.
    
    This registers a model that has been trained externally or by the training system.
    """
    try:
        model_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        model = CustomModelInfo(
            id=model_id,
            name=request.name,
            base_model=request.base_model,
            training_method=TrainingMethod(request.training_method),
            training_job_id=request.training_job_id or "",
            local_path=request.local_path,
            hf_repo_id=request.hf_repo_id,
            status="created",
            metrics=request.metrics,
            created_at=now,
            updated_at=now,
            tags=request.tags,
            description=request.description,
            mlflow_run_id=request.mlflow_run_id,
        )
        
        _models[model_id] = model
        _save_models()
        
        logger.info(f"Registered custom model {request.name} with ID {model_id}")
        
        return _model_to_response(model)
        
    except Exception as e:
        logger.exception(f"Failed to register model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=Dict[str, Any])
async def list_custom_models(
    status: Optional[str] = Query(None, description="Filter by status"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    limit: int = Query(50, description="Maximum models to return"),
) -> Dict[str, Any]:
    """List all custom models."""
    models = list(_models.values())
    
    # Filter by status
    if status:
        models = [m for m in models if m.status == status]
    
    # Filter by tags
    if tags:
        tag_set = set(tags.split(","))
        models = [m for m in models if tag_set & set(m.tags)]
    
    # Sort by created_at (newest first)
    models.sort(key=lambda m: m.created_at or "", reverse=True)
    
    return {
        "models": [_model_to_response(m) for m in models[:limit]],
        "total": len(models),
    }


@router.get("/{model_id}", response_model=CustomModelResponse)
async def get_custom_model(model_id: str) -> CustomModelResponse:
    """Get a custom model by ID."""
    model = _models.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    return _model_to_response(model)


@router.patch("/{model_id}", response_model=CustomModelResponse)
async def update_custom_model(
    model_id: str,
    request: UpdateModelRequest,
) -> CustomModelResponse:
    """Update a custom model."""
    model = _models.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    # Update fields
    if request.name is not None:
        model.name = request.name
    if request.description is not None:
        model.description = request.description
    if request.tags is not None:
        model.tags = request.tags
    if request.status is not None:
        model.status = request.status
    if request.hf_repo_id is not None:
        model.hf_repo_id = request.hf_repo_id
    if request.metrics is not None:
        model.metrics.update(request.metrics)
    
    model.updated_at = datetime.utcnow().isoformat()
    
    _save_models()
    
    return _model_to_response(model)


@router.delete("/{model_id}")
async def delete_custom_model(model_id: str) -> Dict[str, Any]:
    """Delete a custom model from the registry."""
    if model_id not in _models:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    model = _models.pop(model_id)
    _save_models()
    
    return {
        "success": True,
        "message": f"Model {model.name} deleted",
        "model_id": model_id,
    }


@router.post("/{model_id}/deploy", response_model=ModelDeploymentResponse)
async def deploy_custom_model(
    model_id: str,
    request: DeployModelRequest,
) -> ModelDeploymentResponse:
    """
    Deploy a custom model to a serving backend.
    
    Supports deployment to:
    - Ollama (requires GGUF conversion)
    - vLLM
    - TGI (Text Generation Inference)
    """
    model = _models.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    try:
        if request.target == "ollama":
            return await _deploy_to_ollama(model, request)
        elif request.target == "vllm":
            return await _deploy_to_vllm(model, request)
        elif request.target == "tgi":
            return await _deploy_to_tgi(model, request)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown deployment target: {request.target}"
            )
    except Exception as e:
        logger.exception(f"Failed to deploy model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}/config")
async def get_model_config(model_id: str) -> Dict[str, Any]:
    """Get the training configuration used for a model."""
    model = _models.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    return {
        "model_id": model_id,
        "training_config": model.training_config,
        "base_model": model.base_model,
        "training_method": model.training_method.value,
    }


@router.get("/{model_id}/metrics")
async def get_model_metrics(model_id: str) -> Dict[str, Any]:
    """Get metrics for a custom model."""
    model = _models.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    return {
        "model_id": model_id,
        "metrics": model.metrics,
    }


@router.post("/{model_id}/tags")
async def update_model_tags(
    model_id: str,
    tags: List[str],
) -> Dict[str, Any]:
    """Update tags for a model."""
    model = _models.get(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    model.tags = tags
    model.updated_at = datetime.utcnow().isoformat()
    _save_models()
    
    return {
        "model_id": model_id,
        "tags": model.tags,
    }


# ============================================================================
# Helper Functions
# ============================================================================

def _model_to_response(model: CustomModelInfo) -> CustomModelResponse:
    """Convert CustomModelInfo to response."""
    return CustomModelResponse(
        id=model.id,
        name=model.name,
        base_model=model.base_model,
        training_method=model.training_method.value if isinstance(model.training_method, TrainingMethod) else model.training_method,
        training_job_id=model.training_job_id,
        local_path=model.local_path,
        hf_repo_id=model.hf_repo_id,
        status=model.status,
        metrics=model.metrics,
        created_at=model.created_at,
        updated_at=model.updated_at,
        tags=model.tags,
        description=model.description,
        mlflow_run_id=model.mlflow_run_id,
        mlflow_model_uri=model.mlflow_model_uri,
    )


async def _deploy_to_ollama(
    model: CustomModelInfo,
    request: DeployModelRequest,
) -> ModelDeploymentResponse:
    """Deploy model to Ollama."""
    from agentic_assistants.core.ollama import OllamaManager
    from agentic_assistants.training.export import ModelExporter, ExportConfig, ExportFormat
    
    model_name = request.model_name or model.name.lower().replace(" ", "-")
    
    # Check if model is already in GGUF format
    model_path = Path(model.local_path)
    gguf_files = list(model_path.glob("*.gguf"))
    
    if not gguf_files:
        # Need to convert to GGUF
        if request.quantization:
            exporter = ModelExporter()
            export_config = ExportConfig(
                format=ExportFormat.GGUF,
                output_dir=str(model_path / "gguf"),
                gguf_quantization=request.quantization,
            )
            result = exporter.export(str(model_path), export_config)
            
            if not result.success:
                return ModelDeploymentResponse(
                    success=False,
                    model_id=model.id,
                    deployment_target="ollama",
                    message=f"GGUF conversion failed: {result.error}",
                )
            
            gguf_path = result.output_path
        else:
            return ModelDeploymentResponse(
                success=False,
                model_id=model.id,
                deployment_target="ollama",
                message="Model needs GGUF conversion. Specify quantization parameter.",
                details={"available_quantizations": ["q4_k_m", "q5_k_m", "q8_0", "f16"]},
            )
    else:
        gguf_path = str(gguf_files[0])
    
    # Create Ollama model
    try:
        ollama = OllamaManager()
        
        # Create Modelfile
        modelfile_content = f"""FROM {gguf_path}

PARAMETER temperature 0.7
PARAMETER top_p 0.9

SYSTEM You are a helpful AI assistant.
"""
        
        # For now, return instructions for manual creation
        # Full automation requires Ollama API support for creating from file
        return ModelDeploymentResponse(
            success=True,
            model_id=model.id,
            deployment_target="ollama",
            endpoint=f"ollama run {model_name}",
            message="Model ready for Ollama import",
            details={
                "gguf_path": gguf_path,
                "model_name": model_name,
                "modelfile": modelfile_content,
                "instructions": [
                    f"1. Create a Modelfile with: FROM {gguf_path}",
                    f"2. Run: ollama create {model_name} -f Modelfile",
                    f"3. Test with: ollama run {model_name}",
                ],
            },
        )
        
    except Exception as e:
        return ModelDeploymentResponse(
            success=False,
            model_id=model.id,
            deployment_target="ollama",
            message=f"Ollama deployment failed: {str(e)}",
        )


async def _deploy_to_vllm(
    model: CustomModelInfo,
    request: DeployModelRequest,
) -> ModelDeploymentResponse:
    """Deploy model to vLLM."""
    model_name = request.model_name or model.name
    
    # vLLM can serve HuggingFace format models directly
    return ModelDeploymentResponse(
        success=True,
        model_id=model.id,
        deployment_target="vllm",
        message="Model ready for vLLM deployment",
        details={
            "model_path": model.local_path,
            "command": f"python -m vllm.entrypoints.openai.api_server --model {model.local_path} --port 8000",
            "api_endpoint": "http://localhost:8000/v1",
            "gpu_memory_utilization": request.gpu_memory_utilization,
        },
    )


async def _deploy_to_tgi(
    model: CustomModelInfo,
    request: DeployModelRequest,
) -> ModelDeploymentResponse:
    """Deploy model to Text Generation Inference."""
    return ModelDeploymentResponse(
        success=True,
        model_id=model.id,
        deployment_target="tgi",
        message="Model ready for TGI deployment",
        details={
            "model_path": model.local_path,
            "docker_command": f"docker run --gpus all -p 8080:80 -v {model.local_path}:/model ghcr.io/huggingface/text-generation-inference --model-id /model",
            "api_endpoint": "http://localhost:8080",
        },
    )
