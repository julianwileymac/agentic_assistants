# Chunk: 8b62fd6ac4cd_0

- source: `src/agentic_assistants/server/api/config.py`
- lines: 1-87
- chunk: 1/7

```
"""
Configuration API Router.

This module provides REST endpoints for runtime configuration management:
- Get/set global, user, and session configuration
- Configuration validation
- Configuration export/import
"""

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/config", tags=["config"])


# === Request/Response Models ===


class GlobalConfigResponse(BaseModel):
    """Global configuration settings."""
    
    mlflow_enabled: bool = Field(..., description="MLFlow tracking enabled")
    telemetry_enabled: bool = Field(..., description="OpenTelemetry enabled")
    log_level: str = Field(..., description="Logging level")
    data_dir: str = Field(..., description="Data directory path")


class GlobalConfigUpdate(BaseModel):
    """Request to update global configuration."""
    
    mlflow_enabled: Optional[bool] = Field(None, description="MLFlow tracking enabled")
    telemetry_enabled: Optional[bool] = Field(None, description="OpenTelemetry enabled")
    log_level: Optional[str] = Field(None, description="Logging level")


class OllamaConfigResponse(BaseModel):
    """Ollama configuration."""
    
    host: str = Field(..., description="Ollama server URL")
    default_model: str = Field(..., description="Default model")
    timeout: int = Field(..., description="Request timeout")


class OllamaConfigUpdate(BaseModel):
    """Request to update Ollama configuration."""
    
    host: Optional[str] = Field(None, description="Ollama server URL")
    default_model: Optional[str] = Field(None, description="Default model")
    timeout: Optional[int] = Field(None, description="Request timeout")


class MLFlowConfigResponse(BaseModel):
    """MLFlow configuration."""
    
    tracking_uri: str = Field(..., description="Tracking server URI")
    experiment_name: str = Field(..., description="Default experiment name")
    artifact_location: Optional[str] = Field(None, description="Artifact storage location")


class MLFlowConfigUpdate(BaseModel):
    """Request to update MLFlow configuration."""
    
    tracking_uri: Optional[str] = Field(None, description="Tracking server URI")
    experiment_name: Optional[str] = Field(None, description="Default experiment name")


class VectorDBConfigResponse(BaseModel):
    """Vector database configuration."""
    
    backend: str = Field(..., description="Backend type (lancedb, chroma)")
    path: str = Field(..., description="Storage path")
    embedding_model: str = Field(..., description="Embedding model")
    embedding_dimension: int = Field(..., description="Embedding dimension")


class ServerConfigResponse(BaseModel):
    """Server configuration."""
    
```
