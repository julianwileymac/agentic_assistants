"""
Training API routes.

This module provides REST API endpoints for managing LLM training jobs,
including job creation, status monitoring, and logs.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from agentic_assistants.training import (
    TrainingConfig,
    TrainingJob,
    TrainingJobManager,
    TrainingJobStatus,
    TrainingMethod,
    LoRAConfig,
    QLoRAConfig,
)
from agentic_assistants.training.frameworks import LlamaFactoryAdapter
from agentic_assistants.training.datasets import TrainingDatasetManager, DatasetFormat
from agentic_assistants.training.export import ModelExporter, ExportConfig, ExportFormat
from agentic_assistants.training.quantization import ModelQuantizer, QuantizationConfig
from agentic_assistants.training.distillation import KnowledgeDistiller, DistillationConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/training", tags=["training"])

# Global instances (initialized lazily)
_job_manager: Optional[TrainingJobManager] = None
_dataset_manager: Optional[TrainingDatasetManager] = None
_model_exporter: Optional[ModelExporter] = None


def get_job_manager() -> TrainingJobManager:
    """Get or create the training job manager."""
    global _job_manager
    if _job_manager is None:
        _job_manager = TrainingJobManager()
        # Register frameworks
        _job_manager.register_framework("llama_factory", LlamaFactoryAdapter())
    return _job_manager


def get_dataset_manager() -> TrainingDatasetManager:
    """Get or create the dataset manager."""
    global _dataset_manager
    if _dataset_manager is None:
        _dataset_manager = TrainingDatasetManager()
    return _dataset_manager


def get_model_exporter() -> ModelExporter:
    """Get or create the model exporter."""
    global _model_exporter
    if _model_exporter is None:
        _model_exporter = ModelExporter()
    return _model_exporter


# ============================================================================
# Request/Response Models
# ============================================================================

class LoRAConfigRequest(BaseModel):
    """LoRA configuration for API requests."""
    r: int = Field(default=8, description="LoRA rank")
    lora_alpha: int = Field(default=16, description="LoRA alpha")
    lora_dropout: float = Field(default=0.05, description="LoRA dropout")
    target_modules: List[str] = Field(
        default_factory=lambda: ["q_proj", "v_proj"],
        description="Target modules"
    )


class CreateTrainingJobRequest(BaseModel):
    """Request to create a new training job."""
    
    # Model settings
    base_model: str = Field(..., description="Base model (HuggingFace ID or path)")
    output_name: str = Field(..., description="Name for the trained model")
    
    # Training method
    method: str = Field(default="lora", description="Training method: full, lora, qlora")
    lora_config: Optional[LoRAConfigRequest] = None
    
    # Dataset
    dataset_id: str = Field(..., description="Training dataset ID")
    dataset_format: str = Field(default="alpaca", description="Dataset format")
    max_seq_length: int = Field(default=2048, description="Max sequence length")
    
    # Hyperparameters
    num_epochs: int = Field(default=3, description="Number of epochs")
    batch_size: int = Field(default=4, description="Batch size")
    learning_rate: float = Field(default=2e-4, description="Learning rate")
    gradient_accumulation_steps: int = Field(default=4, description="Gradient accumulation")
    
    # Optimization
    bf16: bool = Field(default=True, description="Use BF16")
    gradient_checkpointing: bool = Field(default=True, description="Gradient checkpointing")
    
    # Framework
    framework: str = Field(default="llama_factory", description="Training framework")
    
    # Metadata
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # MLFlow
    mlflow_experiment_name: Optional[str] = None


class TrainingJobResponse(BaseModel):
    """Training job response."""
    
    id: str
    status: str
    progress: float
    
    config: Dict[str, Any]
    
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    metrics: Dict[str, Any] = {}
    error_message: Optional[str] = None
    output_model_path: Optional[str] = None
    mlflow_run_id: Optional[str] = None


class TrainingJobListResponse(BaseModel):
    """List of training jobs."""
    jobs: List[TrainingJobResponse]
    total: int


class TrainingDatasetRequest(BaseModel):
    """Request to register a training dataset."""
    
    name: str = Field(..., description="Dataset name")
    filepath: Optional[str] = Field(None, description="Local file path")
    hf_dataset_id: Optional[str] = Field(None, description="HuggingFace dataset ID")
    format: str = Field(default="alpaca", description="Dataset format")
    description: str = Field(default="", description="Dataset description")
    tags: List[str] = Field(default_factory=list)


class TrainingDatasetResponse(BaseModel):
    """Training dataset response."""
    
    id: str
    name: str
    description: str
    format: str
    filepath: Optional[str]
    hf_dataset_id: Optional[str]
    num_samples: int
    size_bytes: int
    created_at: str
    tags: List[str]


class ExportModelRequest(BaseModel):
    """Request to export a model."""
    
    model_path: str = Field(..., description="Path to source model")
    output_dir: str = Field(..., description="Output directory")
    format: str = Field(default="huggingface", description="Export format")
    
    # GGUF options
    gguf_quantization: Optional[str] = Field(None, description="GGUF quantization type")
    
    # Options
    merge_lora: bool = Field(default=True, description="Merge LoRA weights")
    include_tokenizer: bool = Field(default=True, description="Include tokenizer")


class ExportModelResponse(BaseModel):
    """Model export response."""
    
    success: bool
    output_path: str
    format: str
    size_bytes: int = 0
    error: Optional[str] = None


class DistillationRequest(BaseModel):
    """Request for knowledge distillation."""
    
    teacher_model: str = Field(..., description="Teacher model path or ID")
    student_model: str = Field(..., description="Student model path or ID")
    output_name: str = Field(..., description="Output model name")
    dataset_id: str = Field(..., description="Training dataset ID")
    
    temperature: float = Field(default=2.0, description="Distillation temperature")
    alpha: float = Field(default=0.5, description="Loss weight")
    
    num_epochs: int = Field(default=3)
    batch_size: int = Field(default=4)
    learning_rate: float = Field(default=2e-5)
    
    use_lora_student: bool = Field(default=True)


# ============================================================================
# Training Job Endpoints
# ============================================================================

@router.post("/jobs", response_model=TrainingJobResponse)
async def create_training_job(
    request: CreateTrainingJobRequest,
    background_tasks: BackgroundTasks,
    job_manager: TrainingJobManager = Depends(get_job_manager),
) -> TrainingJobResponse:
    """
    Create a new training job.
    
    The job will be queued and started automatically when resources are available.
    """
    try:
        # Build training config
        method = TrainingMethod(request.method)
        
        lora_config = None
        qlora_config = None
        
        if method == TrainingMethod.LORA and request.lora_config:
            lora_config = LoRAConfig(**request.lora_config.model_dump())
        elif method == TrainingMethod.QLORA and request.lora_config:
            qlora_config = QLoRAConfig(**request.lora_config.model_dump())
        
        config = TrainingConfig(
            base_model=request.base_model,
            output_name=request.output_name,
            method=method,
            lora_config=lora_config,
            qlora_config=qlora_config,
            dataset_id=request.dataset_id,
            dataset_format=request.dataset_format,
            max_seq_length=request.max_seq_length,
            num_epochs=request.num_epochs,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate,
            gradient_accumulation_steps=request.gradient_accumulation_steps,
            bf16=request.bf16,
            gradient_checkpointing=request.gradient_checkpointing,
            framework=request.framework,
            description=request.description,
            tags=request.tags,
            mlflow_experiment_name=request.mlflow_experiment_name,
        )
        
        # Create job
        job = job_manager.create_job(config, framework=request.framework)
        
        # Start job in background
        background_tasks.add_task(job_manager.start_job, job.id)
        
        return _job_to_response(job)
        
    except Exception as e:
        logger.exception(f"Failed to create training job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=TrainingJobListResponse)
async def list_training_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Maximum jobs to return"),
    job_manager: TrainingJobManager = Depends(get_job_manager),
) -> TrainingJobListResponse:
    """List training jobs with optional filtering."""
    try:
        status_filter = TrainingJobStatus(status) if status else None
        jobs = job_manager.list_jobs(status=status_filter, limit=limit)
        
        return TrainingJobListResponse(
            jobs=[_job_to_response(job) for job in jobs],
            total=len(jobs),
        )
    except Exception as e:
        logger.exception(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=TrainingJobResponse)
async def get_training_job(
    job_id: str,
    job_manager: TrainingJobManager = Depends(get_job_manager),
) -> TrainingJobResponse:
    """Get a specific training job by ID."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return _job_to_response(job)


@router.get("/jobs/{job_id}/status")
async def get_training_job_status(
    job_id: str,
    job_manager: TrainingJobManager = Depends(get_job_manager),
) -> Dict[str, Any]:
    """Get training job status and metrics."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return {
        "id": job.id,
        "status": job.status.value,
        "progress": job.progress,
        "metrics": job.metrics.to_dict(),
        "error_message": job.error_message,
    }


@router.get("/jobs/{job_id}/logs")
async def get_training_job_logs(
    job_id: str,
    tail: int = Query(100, description="Number of log lines to return"),
    job_manager: TrainingJobManager = Depends(get_job_manager),
) -> Dict[str, Any]:
    """Get training job logs."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    logs = job_manager.get_job_logs(job_id, tail=tail)
    return {
        "job_id": job_id,
        "logs": logs,
        "total_lines": len(job.logs),
    }


@router.post("/jobs/{job_id}/stop")
async def stop_training_job(
    job_id: str,
    job_manager: TrainingJobManager = Depends(get_job_manager),
) -> Dict[str, Any]:
    """Stop a running training job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    success = await job_manager.stop_job(job_id)
    return {
        "success": success,
        "job_id": job_id,
        "message": "Job stopped" if success else "Failed to stop job",
    }


@router.delete("/jobs/{job_id}")
async def delete_training_job(
    job_id: str,
    job_manager: TrainingJobManager = Depends(get_job_manager),
) -> Dict[str, Any]:
    """Delete a training job."""
    success = job_manager.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found or cannot be deleted")
    
    return {"success": True, "message": f"Job {job_id} deleted"}


# ============================================================================
# Dataset Endpoints
# ============================================================================

@router.post("/datasets", response_model=TrainingDatasetResponse)
async def register_training_dataset(
    request: TrainingDatasetRequest,
    dataset_manager: TrainingDatasetManager = Depends(get_dataset_manager),
) -> TrainingDatasetResponse:
    """Register a new training dataset."""
    try:
        dataset = dataset_manager.register(
            name=request.name,
            filepath=request.filepath,
            hf_dataset_id=request.hf_dataset_id,
            format=DatasetFormat(request.format),
            description=request.description,
            tags=request.tags,
        )
        
        return TrainingDatasetResponse(
            id=dataset.id,
            name=dataset.name,
            description=dataset.description,
            format=dataset.format.value,
            filepath=dataset.filepath,
            hf_dataset_id=dataset.hf_dataset_id,
            num_samples=dataset.num_samples,
            size_bytes=dataset.size_bytes,
            created_at=dataset.created_at,
            tags=dataset.tags,
        )
    except Exception as e:
        logger.exception(f"Failed to register dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets")
async def list_training_datasets(
    format: Optional[str] = Query(None, description="Filter by format"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    dataset_manager: TrainingDatasetManager = Depends(get_dataset_manager),
) -> Dict[str, Any]:
    """List training datasets."""
    try:
        format_filter = DatasetFormat(format) if format else None
        tags_filter = tags.split(",") if tags else None
        
        datasets = dataset_manager.list(format=format_filter, tags=tags_filter)
        
        return {
            "datasets": [
                {
                    "id": ds.id,
                    "name": ds.name,
                    "format": ds.format.value,
                    "num_samples": ds.num_samples,
                    "tags": ds.tags,
                }
                for ds in datasets
            ],
            "total": len(datasets),
        }
    except Exception as e:
        logger.exception(f"Failed to list datasets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_id}")
async def get_training_dataset(
    dataset_id: str,
    dataset_manager: TrainingDatasetManager = Depends(get_dataset_manager),
) -> TrainingDatasetResponse:
    """Get a training dataset by ID."""
    dataset = dataset_manager.get(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    
    return TrainingDatasetResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        format=dataset.format.value,
        filepath=dataset.filepath,
        hf_dataset_id=dataset.hf_dataset_id,
        num_samples=dataset.num_samples,
        size_bytes=dataset.size_bytes,
        created_at=dataset.created_at,
        tags=dataset.tags,
    )


@router.get("/datasets/{dataset_id}/samples")
async def get_dataset_samples(
    dataset_id: str,
    limit: int = Query(10, description="Number of samples to return"),
    dataset_manager: TrainingDatasetManager = Depends(get_dataset_manager),
) -> Dict[str, Any]:
    """Get sample data from a dataset."""
    dataset = dataset_manager.get(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    
    samples = dataset.load_samples(limit=limit)
    return {
        "dataset_id": dataset_id,
        "samples": samples,
        "total_samples": dataset.num_samples,
    }


# ============================================================================
# Export Endpoints
# ============================================================================

@router.post("/export", response_model=ExportModelResponse)
async def export_model(
    request: ExportModelRequest,
    exporter: ModelExporter = Depends(get_model_exporter),
) -> ExportModelResponse:
    """Export a trained model to a different format."""
    try:
        config = ExportConfig(
            format=ExportFormat(request.format),
            output_dir=request.output_dir,
            gguf_quantization=request.gguf_quantization,
            merge_lora=request.merge_lora,
            include_tokenizer=request.include_tokenizer,
        )
        
        result = exporter.export(request.model_path, config)
        
        return ExportModelResponse(
            success=result.success,
            output_path=result.output_path,
            format=result.format.value,
            size_bytes=result.size_bytes,
            error=result.error,
        )
    except Exception as e:
        logger.exception(f"Failed to export model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/formats")
async def get_export_formats(
    exporter: ModelExporter = Depends(get_model_exporter),
) -> Dict[str, Any]:
    """Get supported export formats."""
    formats = exporter.get_supported_formats()
    quantizations = exporter.get_gguf_quantizations()
    
    return {
        "formats": [f.value for f in formats],
        "gguf_quantizations": quantizations,
    }


# ============================================================================
# Distillation Endpoints
# ============================================================================

@router.post("/distillation")
async def start_distillation(
    request: DistillationRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """Start a knowledge distillation job."""
    try:
        config = DistillationConfig(
            teacher_model=request.teacher_model,
            student_model=request.student_model,
            output_dir=f"./data/training/outputs/distill-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            output_name=request.output_name,
            dataset_id=request.dataset_id,
            temperature=request.temperature,
            alpha=request.alpha,
            num_epochs=request.num_epochs,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate,
            use_lora_student=request.use_lora_student,
        )
        
        distiller = KnowledgeDistiller()
        
        # Start distillation in background
        async def run_distillation():
            result = await distiller.distill(config)
            logger.info(f"Distillation completed: {result.success}")
        
        background_tasks.add_task(run_distillation)
        
        return {
            "status": "started",
            "config": config.to_dict(),
            "message": "Distillation job started in background",
        }
    except Exception as e:
        logger.exception(f"Failed to start distillation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Framework Info Endpoints
# ============================================================================

@router.get("/frameworks")
async def get_training_frameworks(
    job_manager: TrainingJobManager = Depends(get_job_manager),
) -> Dict[str, Any]:
    """Get information about available training frameworks."""
    frameworks = {}
    
    # Check Llama Factory
    llama_factory = LlamaFactoryAdapter()
    frameworks["llama_factory"] = {
        "name": "Llama Factory",
        "available": llama_factory.is_available(),
        "version": llama_factory.version,
        "capabilities": llama_factory.get_capabilities(),
    }
    
    return {"frameworks": frameworks}


@router.get("/capabilities")
async def get_training_capabilities() -> Dict[str, Any]:
    """Get overall training capabilities."""
    llama_factory = LlamaFactoryAdapter()
    exporter = get_model_exporter()
    
    return {
        "training_methods": ["full", "lora", "qlora"],
        "frameworks": ["llama_factory"],
        "export_formats": [f.value for f in exporter.get_supported_formats()],
        "gguf_quantizations": exporter.get_gguf_quantizations(),
        "supports_distributed": True,
        "supports_rlhf": True,
        "supports_dpo": True,
        "supports_distillation": True,
    }


# ============================================================================
# Helper Functions
# ============================================================================

def _job_to_response(job: TrainingJob) -> TrainingJobResponse:
    """Convert TrainingJob to TrainingJobResponse."""
    return TrainingJobResponse(
        id=job.id,
        status=job.status.value,
        progress=job.progress,
        config=job.config.model_dump() if hasattr(job.config, 'model_dump') else {},
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        metrics=job.metrics.to_dict(),
        error_message=job.error_message,
        output_model_path=job.output_model_path,
        mlflow_run_id=job.mlflow_run_id,
    )
