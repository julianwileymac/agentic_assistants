"""
Nemotron model management API endpoints.

Provides REST endpoints for model fetching, serving, training,
evaluation, and dataset management for the nemotron model family.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/nemotron", tags=["nemotron"])


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class FetchModelRequest(BaseModel):
    model_id: str = "nvidia/Llama-3.1-Nemotron-Nano-8B-v1"
    revision: str = "main"
    cache_dir: Optional[str] = None


class ServeModelRequest(BaseModel):
    model_path: Optional[str] = None
    model_name: str = "nemotron-nano-coding"
    backend: str = "ollama"


class ExportModelRequest(BaseModel):
    model_path: str
    format: str = "gguf"
    quantization: str = "q4_k_m"


class TrainingRequest(BaseModel):
    method: str = "qlora"
    dataset_id: Optional[str] = None
    base_model: str = "nvidia/Llama-3.1-Nemotron-Nano-8B-v1"
    learning_rate: Optional[float] = None
    num_epochs: Optional[int] = None
    batch_size: Optional[int] = None


class EvaluateRequest(BaseModel):
    model_path: str
    benchmarks: List[str] = Field(default_factory=lambda: ["humaneval", "mbpp"])


class RegisterDatasetRequest(BaseModel):
    name: str
    source_type: str = "local"
    source_path: str = ""
    format: str = "jsonl"
    tags: List[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str
    system_prompt: str = ""
    model: str = "nemotron-nano-coding"
    temperature: float = 0.2
    max_tokens: int = 4096


# ---------------------------------------------------------------------------
# Model management endpoints
# ---------------------------------------------------------------------------

@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """List available nemotron models and their status."""
    from agentic_assistants.integrations.nemotron import NemotronModelManager
    mgr = NemotronModelManager()
    return {"models": mgr.list_available_models()}


@router.post("/models/fetch")
async def fetch_model(request: FetchModelRequest) -> Dict[str, Any]:
    """Download model weights from HuggingFace."""
    from agentic_assistants.integrations.nemotron import NemotronModelManager
    mgr = NemotronModelManager(cache_dir=request.cache_dir)
    result = mgr.fetch_weights(model_id=request.model_id, revision=request.revision)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Fetch failed"))
    return result


@router.get("/models/{model_id}/status")
async def model_status(model_id: str) -> Dict[str, Any]:
    """Get the status of a specific model."""
    from agentic_assistants.integrations.nemotron import NemotronModelManager
    mgr = NemotronModelManager()
    return mgr.get_model_info(model_id)


@router.post("/models/{model_id}/serve")
async def serve_model(model_id: str, request: ServeModelRequest) -> Dict[str, Any]:
    """Deploy a model for inference."""
    from agentic_assistants.integrations.nemotron import NemotronModelManager
    mgr = NemotronModelManager()
    result = mgr.deploy(
        model_path=request.model_path or model_id,
        backend=request.backend,
        model_name=request.model_name,
    )
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Deploy failed"))
    return result


@router.delete("/models/{model_id}/serve")
async def undeploy_model(model_id: str) -> Dict[str, Any]:
    """Undeploy a model."""
    try:
        from agentic_assistants.serving.manager import ServingManager
        mgr = ServingManager()
        mgr.undeploy(model_id)
        return {"status": "undeployed", "model_id": model_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/export")
async def export_model(model_id: str, request: ExportModelRequest) -> Dict[str, Any]:
    """Export a model to GGUF, Ollama, or other format."""
    from agentic_assistants.integrations.nemotron import NemotronModelManager
    mgr = NemotronModelManager()
    result = mgr.export(
        model_path=request.model_path,
        format=request.format,
        quantization=request.quantization,
    )
    return result


# ---------------------------------------------------------------------------
# Training endpoints
# ---------------------------------------------------------------------------

@router.post("/training/start")
async def start_training(request: TrainingRequest) -> Dict[str, Any]:
    """Start a nemotron training job."""
    try:
        from agentic_assistants.training.jobs import TrainingJobManager
        from agentic_assistants.training.config import TrainingConfig, TrainingMethod

        method_map = {
            "sft": TrainingMethod.FULL,
            "lora": TrainingMethod.LORA,
            "qlora": TrainingMethod.QLORA,
            "full": TrainingMethod.FULL,
        }

        config = TrainingConfig(
            base_model=request.base_model,
            method=method_map.get(request.method, TrainingMethod.QLORA),
        )
        if request.learning_rate:
            config.learning_rate = request.learning_rate
        if request.num_epochs:
            config.num_epochs = request.num_epochs
        if request.batch_size:
            config.per_device_train_batch_size = request.batch_size

        mgr = TrainingJobManager()
        job = mgr.create_job(config)
        return {"job_id": job.job_id, "status": job.status.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training/jobs")
async def list_training_jobs() -> Dict[str, Any]:
    """List all training jobs."""
    try:
        from agentic_assistants.training.jobs import TrainingJobManager
        mgr = TrainingJobManager()
        jobs = mgr.list_jobs()
        return {
            "jobs": [
                {
                    "job_id": j.job_id,
                    "status": j.status.value,
                    "created_at": j.created_at,
                }
                for j in jobs
            ]
        }
    except Exception as e:
        return {"jobs": [], "error": str(e)}


# ---------------------------------------------------------------------------
# Evaluation endpoints
# ---------------------------------------------------------------------------

@router.post("/evaluate")
async def evaluate_model(request: EvaluateRequest) -> Dict[str, Any]:
    """Run evaluation benchmarks on a model."""
    from agentic_assistants.integrations.nemotron import NemotronModelManager
    mgr = NemotronModelManager()
    info = mgr.get_model_info(request.model_path)
    return {
        "model_path": request.model_path,
        "benchmarks": request.benchmarks,
        "status": "evaluation_queued",
        "model_info": info,
    }


# ---------------------------------------------------------------------------
# Dataset endpoints
# ---------------------------------------------------------------------------

@router.get("/datasets")
async def list_datasets(
    project_id: Optional[str] = None,
    source_type: Optional[str] = None,
) -> Dict[str, Any]:
    """List datasets from the catalog."""
    try:
        from agentic_assistants.datasources.dataset_catalog import DatasetCatalog
        catalog = DatasetCatalog(project_id=project_id)
        entries = catalog.list(project_id=project_id, source_type=source_type)
        return {
            "datasets": [e.model_dump() for e in entries],
            "total": len(entries),
        }
    except Exception as e:
        return {"datasets": [], "error": str(e)}


@router.post("/datasets")
async def register_dataset(request: RegisterDatasetRequest) -> Dict[str, Any]:
    """Register a new dataset in the catalog."""
    try:
        from agentic_assistants.datasources.dataset_catalog import DatasetCatalog
        catalog = DatasetCatalog()
        entry = catalog.register(
            name=request.name,
            source_type=request.source_type,
            source_path=request.source_path,
            format=request.format,
            tags=request.tags,
        )
        return {"dataset": entry.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_id}/stats")
async def dataset_stats(dataset_id: str) -> Dict[str, Any]:
    """Get statistics for a dataset."""
    try:
        from agentic_assistants.datasources.dataset_catalog import DatasetCatalog
        catalog = DatasetCatalog()
        return catalog.get_stats(dataset_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_id}/preview")
async def dataset_preview(dataset_id: str, n: int = 5) -> Dict[str, Any]:
    """Preview first N samples of a dataset."""
    try:
        from agentic_assistants.datasources.dataset_catalog import DatasetCatalog
        catalog = DatasetCatalog()
        samples = catalog.preview(dataset_id, n=n)
        return {"samples": samples, "count": len(samples)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------

@router.post("/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """Chat with the nemotron model."""
    from agentic_assistants.integrations.nemotron import NemotronModelManager
    mgr = NemotronModelManager()
    response = mgr.chat(
        prompt=request.message,
        system_prompt=request.system_prompt,
        model=request.model,
        temperature=request.temperature,
    )
    return {"response": response, "model": request.model}
