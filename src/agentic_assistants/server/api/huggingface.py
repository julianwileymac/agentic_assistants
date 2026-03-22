"""
HuggingFace Hub API routes.

This module provides REST API endpoints for interacting with HuggingFace Hub:
- Model search, info, pull, and push
- Dataset search, info, and pull
- Paper search
- LoRA adapter weight push/pull
- Connection and authentication status
"""

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.integrations.huggingface import (
    HuggingFaceHubIntegration,
    ModelCard,
    DatasetCard,
)
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/huggingface", tags=["huggingface"])

_hf: Optional[HuggingFaceHubIntegration] = None


def _get_hf() -> HuggingFaceHubIntegration:
    global _hf
    if _hf is None:
        from agentic_assistants.config import AgenticConfig
        cfg = AgenticConfig()
        _hf = HuggingFaceHubIntegration(
            token=cfg.huggingface.token,
            local_cache_dir=str(cfg.huggingface.cache_dir),
        )
    return _hf


# ============================================================================
# Request / Response Models
# ============================================================================

class PullModelRequest(BaseModel):
    repo_id: str = Field(..., description="HuggingFace model repo ID")
    revision: Optional[str] = Field(None, description="Revision/branch")
    local_dir: Optional[str] = Field(None, description="Local directory to save to")


class PushModelRequest(BaseModel):
    model_path: str = Field(..., description="Local path to model")
    repo_id: str = Field(..., description="HuggingFace repo ID")
    private: bool = Field(default=False)
    commit_message: str = Field(default="Upload model")
    model_card: Optional[Dict[str, Any]] = Field(None, description="Model card data")


class PullDatasetRequest(BaseModel):
    repo_id: str = Field(..., description="HuggingFace dataset repo ID")
    local_dir: Optional[str] = Field(None, description="Local directory to save to")


class PushWeightsRequest(BaseModel):
    weights_path: str = Field(..., description="Local path to adapter weights")
    repo_id: str = Field(..., description="HuggingFace repo ID")
    adapter_name: str = Field(default="default")
    private: bool = Field(default=False)
    commit_message: str = Field(default="Upload adapter weights")


class PullWeightsRequest(BaseModel):
    repo_id: str = Field(..., description="HuggingFace repo ID")
    adapter_name: str = Field(default="default")
    revision: Optional[str] = Field(None)
    local_dir: Optional[str] = Field(None)


# ============================================================================
# Status
# ============================================================================

@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get HuggingFace Hub connection and auth status."""
    hf = _get_hf()
    user_info = hf.whoami()
    return {
        "hub_available": hf._hub_available,
        "token_set": hf.token is not None,
        "authenticated": user_info is not None,
        "user": user_info,
        "storage_backend": hf.get_storage_backend(),
    }


# ============================================================================
# Models
# ============================================================================

@router.get("/models")
async def search_models(
    query: Optional[str] = Query(None, description="Search query"),
    author: Optional[str] = Query(None, description="Filter by author"),
    task: Optional[str] = Query(None, description="Filter by task"),
    library: Optional[str] = Query(None, description="Filter by library"),
    language: Optional[str] = Query(None, description="Filter by language"),
    sort: str = Query("downloads", description="Sort field"),
    limit: int = Query(50, description="Max results"),
) -> Dict[str, Any]:
    """Search and list models on HuggingFace Hub."""
    hf = _get_hf()
    models = hf.search_models(
        query=query,
        author=author,
        task=task,
        library=library,
        language=language,
        sort=sort,
        limit=limit,
    )
    return {"models": models, "total": len(models)}


@router.get("/models/{repo_id:path}/info")
async def get_model_info(repo_id: str) -> Dict[str, Any]:
    """Get information about a specific model."""
    hf = _get_hf()
    info = hf.get_model_info(repo_id)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Model {repo_id} not found")
    return info


@router.post("/models/pull")
async def pull_model(
    request: PullModelRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """Pull a model from HuggingFace Hub."""
    hf = _get_hf()
    local_path = hf.pull_model(
        repo_id=request.repo_id,
        revision=request.revision,
        local_dir=request.local_dir,
    )
    if local_path is None:
        raise HTTPException(status_code=500, detail="Failed to pull model")
    return {"success": True, "local_path": local_path, "repo_id": request.repo_id}


@router.post("/models/push")
async def push_model(request: PushModelRequest) -> Dict[str, Any]:
    """Push a model to HuggingFace Hub."""
    hf = _get_hf()

    card = None
    if request.model_card:
        card = ModelCard(
            model_name=request.model_card.get("model_name", request.repo_id),
            base_model=request.model_card.get("base_model", ""),
            description=request.model_card.get("description", ""),
            training_method=request.model_card.get("training_method", ""),
            tags=request.model_card.get("tags", []),
        )

    result = hf.push_model(
        model_path=request.model_path,
        repo_id=request.repo_id,
        model_card=card,
        private=request.private,
        commit_message=request.commit_message,
    )
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Push failed"))
    return result


# ============================================================================
# Datasets
# ============================================================================

@router.get("/datasets")
async def search_datasets(
    query: Optional[str] = Query(None, description="Search query"),
    author: Optional[str] = Query(None, description="Filter by author"),
    limit: int = Query(50, description="Max results"),
) -> Dict[str, Any]:
    """Search and list datasets on HuggingFace Hub."""
    hf = _get_hf()
    datasets = hf.list_datasets(author=author, search=query, limit=limit)
    return {"datasets": datasets, "total": len(datasets)}


@router.get("/datasets/{repo_id:path}/info")
async def get_dataset_info(repo_id: str) -> Dict[str, Any]:
    """Get information about a specific dataset."""
    hf = _get_hf()
    info = hf.get_dataset_info(repo_id)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Dataset {repo_id} not found")
    return info


@router.post("/datasets/pull")
async def pull_dataset(request: PullDatasetRequest) -> Dict[str, Any]:
    """Pull a dataset from HuggingFace Hub."""
    hf = _get_hf()
    local_path = hf.pull_dataset(
        repo_id=request.repo_id,
        local_dir=request.local_dir,
    )
    if local_path is None:
        raise HTTPException(status_code=500, detail="Failed to pull dataset")
    return {"success": True, "local_path": local_path, "repo_id": request.repo_id}


# ============================================================================
# Papers
# ============================================================================

@router.get("/papers")
async def search_papers(
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Max results"),
) -> Dict[str, Any]:
    """Search papers on HuggingFace."""
    hf = _get_hf()
    papers = hf.search_papers(query=query, limit=limit)
    return {"papers": papers, "total": len(papers)}


@router.get("/papers/{paper_id}")
async def get_paper(paper_id: str) -> Dict[str, Any]:
    """Get a specific paper by ID."""
    hf = _get_hf()
    paper = hf.get_paper(paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")
    return paper


# ============================================================================
# Weights (LoRA adapters)
# ============================================================================

@router.post("/weights/push")
async def push_weights(request: PushWeightsRequest) -> Dict[str, Any]:
    """Push LoRA adapter weights to HuggingFace Hub."""
    hf = _get_hf()
    result = hf.push_weights(
        weights_path=request.weights_path,
        repo_id=request.repo_id,
        adapter_name=request.adapter_name,
        private=request.private,
        commit_message=request.commit_message,
    )
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Push failed"))
    return result


@router.post("/weights/pull")
async def pull_weights(request: PullWeightsRequest) -> Dict[str, Any]:
    """Pull LoRA adapter weights from HuggingFace Hub."""
    hf = _get_hf()
    local_path = hf.pull_weights(
        repo_id=request.repo_id,
        adapter_name=request.adapter_name,
        revision=request.revision,
        local_dir=request.local_dir,
    )
    if local_path is None:
        raise HTTPException(status_code=500, detail="Failed to pull weights")
    return {"success": True, "local_path": local_path, "repo_id": request.repo_id}


# ============================================================================
# Spaces
# ============================================================================

@router.get("/spaces")
async def list_spaces(
    query: Optional[str] = Query(None, description="Search query"),
    author: Optional[str] = Query(None, description="Filter by author"),
    limit: int = Query(50, description="Max results"),
) -> Dict[str, Any]:
    """List HuggingFace Spaces."""
    hf = _get_hf()
    spaces = hf.list_spaces(author=author, search=query, limit=limit)
    return {"spaces": spaces, "total": len(spaces)}


# ============================================================================
# Credentials
# ============================================================================

class SetCredentialsRequest(BaseModel):
    token: str = Field(..., description="HuggingFace API token")


@router.post("/credentials")
async def set_credentials(request: SetCredentialsRequest) -> Dict[str, Any]:
    """Set or update the HuggingFace API token.

    Validates the token by calling ``whoami`` and, if valid, applies it
    to the running integration singleton.
    """
    hf = _get_hf()
    hf.set_token(request.token)
    user_info = hf.whoami()
    if user_info is None:
        hf.set_token(None)
        raise HTTPException(status_code=401, detail="Invalid token -- whoami failed")
    return {
        "status": "ok",
        "authenticated": True,
        "user": user_info,
    }


@router.delete("/credentials")
async def clear_credentials() -> Dict[str, Any]:
    """Clear the HuggingFace API token from the running singleton."""
    hf = _get_hf()
    hf.set_token(None)
    return {"status": "ok", "authenticated": False}
