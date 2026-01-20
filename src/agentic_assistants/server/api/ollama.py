"""
Ollama Model Management API endpoints.

This module provides REST API endpoints for managing Ollama models,
including listing, pulling, importing for fine-tuning, and exporting.
"""

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.ollama import OllamaManager
from agentic_assistants.training import OllamaModelImporter, OllamaModelExporter
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ollama", tags=["ollama"])


def get_config() -> AgenticConfig:
    """Get the global configuration."""
    return AgenticConfig()


def get_ollama_manager() -> OllamaManager:
    """Get the Ollama manager."""
    return OllamaManager(get_config())


# Request/Response Models

class OllamaModelResponse(BaseModel):
    """Response for a single Ollama model."""
    name: str
    tag: str
    size: int
    digest: str
    modifiedAt: str
    quantization: Optional[str] = None
    family: Optional[str] = None
    parameterSize: Optional[str] = None


class ModelsListResponse(BaseModel):
    """Response for listing models."""
    models: List[OllamaModelResponse]


class PullModelRequest(BaseModel):
    """Request to pull a model."""
    name: str = Field(..., description="Model name to pull (e.g., llama3.2)")


class PullModelResponse(BaseModel):
    """Response from pull model."""
    status: str
    message: str


class DeleteModelRequest(BaseModel):
    """Request to delete a model."""
    name: str = Field(..., description="Model name to delete")


class ImportModelResponse(BaseModel):
    """Response from import model."""
    status: str
    name: str
    outputPath: str
    format: str


class CreateModelRequest(BaseModel):
    """Request to create a custom model."""
    name: str = Field(..., description="Name for the new model")
    baseModel: str = Field(..., description="Base model to use")
    systemPrompt: Optional[str] = Field(default=None, description="System prompt")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Model parameters")


class CreateModelResponse(BaseModel):
    """Response from create model."""
    status: str
    name: str


class ExportModelRequest(BaseModel):
    """Request to export a model to Ollama."""
    modelPath: str = Field(..., description="Path to the model to export")
    name: str = Field(..., description="Name for the Ollama model")
    systemPrompt: Optional[str] = Field(default=None, description="System prompt")
    quantization: str = Field(default="q4_k_m", description="Quantization method")


class ExportModelResponse(BaseModel):
    """Response from export model."""
    status: str
    ollamaName: str


class ImportedModelResponse(BaseModel):
    """Response for an imported model."""
    name: str
    sourceModel: str
    outputPath: str
    format: str
    sizeBytes: int
    importedAt: str


class ExportedModelResponse(BaseModel):
    """Response for an exported model."""
    name: str
    sourcePath: str
    ollamaName: str
    createdAt: str


# Endpoints

@router.get("/models", response_model=ModelsListResponse)
async def list_models():
    """
    List all available Ollama models.
    """
    try:
        manager = get_ollama_manager()
        models_data = await manager.list_models()
        
        models = []
        for m in models_data:
            name_parts = m.get("name", "").split(":")
            models.append(OllamaModelResponse(
                name=name_parts[0],
                tag=name_parts[1] if len(name_parts) > 1 else "latest",
                size=m.get("size", 0),
                digest=m.get("digest", ""),
                modifiedAt=m.get("modified_at", ""),
                quantization=m.get("details", {}).get("quantization_level"),
                family=m.get("details", {}).get("family"),
                parameterSize=m.get("details", {}).get("parameter_size"),
            ))
        
        return ModelsListResponse(models=models)
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """
    Get detailed information about a specific model.
    """
    try:
        manager = get_ollama_manager()
        info = await manager.get_model_info(model_name)
        
        if not info:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/pull", response_model=PullModelResponse)
async def pull_model(request: PullModelRequest, background_tasks: BackgroundTasks):
    """
    Pull a model from the Ollama registry.
    
    This operation runs in the background.
    """
    try:
        manager = get_ollama_manager()
        
        # Start pull in background
        async def do_pull():
            try:
                await manager.pull_model(request.name)
                logger.info(f"Successfully pulled model: {request.name}")
            except Exception as e:
                logger.error(f"Failed to pull model: {e}")
        
        background_tasks.add_task(asyncio.create_task, do_pull())
        
        return PullModelResponse(
            status="pulling",
            message=f"Started pulling {request.name}",
        )
    except Exception as e:
        logger.error(f"Failed to initiate pull: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/models")
async def delete_model(request: DeleteModelRequest):
    """
    Delete a model from Ollama.
    """
    try:
        manager = get_ollama_manager()
        success = await manager.delete_model(request.name)
        
        if success:
            return {"status": "ok", "message": f"Deleted {request.name}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete model")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_name}/import", response_model=ImportModelResponse)
async def import_model_for_training(model_name: str):
    """
    Import a model from Ollama for fine-tuning.
    
    This exports the model weights and prepares them for training.
    """
    try:
        config = get_config()
        async with OllamaModelImporter(config) as importer:
            imported = await importer.import_model(model_name)
            
            if imported:
                return ImportModelResponse(
                    status="imported",
                    name=imported.name,
                    outputPath=str(imported.output_path),
                    format=imported.format,
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to import model")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to import model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/export", response_model=ExportModelResponse)
async def export_model_to_ollama(request: ExportModelRequest):
    """
    Export a fine-tuned model to Ollama.
    """
    try:
        config = get_config()
        async with OllamaModelExporter(config) as exporter:
            from pathlib import Path
            
            exported = await exporter.export_model(
                model_path=Path(request.modelPath),
                name=request.name,
                system_prompt=request.systemPrompt,
                quantization=request.quantization,
            )
            
            if exported:
                return ExportModelResponse(
                    status="exported",
                    ollamaName=exported.ollama_name,
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to export model")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/create", response_model=CreateModelResponse)
async def create_custom_model(request: CreateModelRequest):
    """
    Create a custom model based on an existing model.
    
    This creates a new Modelfile with custom system prompt and parameters.
    """
    try:
        config = get_config()
        async with OllamaModelExporter(config) as exporter:
            ollama_name = await exporter.create_from_base(
                name=request.name,
                base_model=request.baseModel,
                system_prompt=request.systemPrompt,
                parameters=request.parameters,
            )
            
            if ollama_name:
                return CreateModelResponse(
                    status="created",
                    name=ollama_name,
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to create model")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/imports")
async def list_imported_models():
    """
    List all models that have been imported for training.
    """
    try:
        config = get_config()
        importer = OllamaModelImporter(config)
        
        # List import metadata files
        imports_dir = importer.models_dir
        imported = []
        
        if imports_dir.exists():
            for metadata_file in imports_dir.glob("*/import_metadata.json"):
                try:
                    import json
                    with open(metadata_file, "r") as f:
                        data = json.load(f)
                    imported.append(ImportedModelResponse(
                        name=data.get("source_model", "").replace(":", "_"),
                        sourceModel=data.get("source_model", ""),
                        outputPath=str(metadata_file.parent),
                        format=data.get("format", "gguf"),
                        sizeBytes=0,
                        importedAt=data.get("imported_at", ""),
                    ))
                except Exception:
                    pass
        
        return {"models": imported}
    except Exception as e:
        logger.error(f"Failed to list imported models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exports")
async def list_exported_models():
    """
    List all models that have been exported to Ollama.
    """
    try:
        config = get_config()
        async with OllamaModelExporter(config) as exporter:
            exports = await exporter.list_exported_models()
            
            exported = [
                ExportedModelResponse(
                    name=e.get("name", ""),
                    sourcePath=e.get("source_path", ""),
                    ollamaName=e.get("ollama_name", ""),
                    createdAt=e.get("created_at", ""),
                )
                for e in exports
            ]
            
            return {"models": exported}
    except Exception as e:
        logger.error(f"Failed to list exported models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_ollama_status():
    """
    Check the status of the Ollama server.
    """
    try:
        manager = get_ollama_manager()
        is_running = await manager.is_running()
        
        if is_running:
            models = await manager.list_models()
            return {
                "status": "running",
                "host": manager.host,
                "modelCount": len(models),
            }
        else:
            return {
                "status": "not_running",
                "host": manager.host,
            }
    except Exception as e:
        logger.error(f"Failed to get Ollama status: {e}")
        return {
            "status": "error",
            "error": str(e),
        }
