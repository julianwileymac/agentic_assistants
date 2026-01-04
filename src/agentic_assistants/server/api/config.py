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
    
    host: str = Field(..., description="Server host")
    port: int = Field(..., description="Server port")
    enable_mcp: bool = Field(..., description="MCP enabled")
    enable_rest: bool = Field(..., description="REST API enabled")


class UserConfigResponse(BaseModel):
    """User configuration."""
    
    user_id: str = Field(..., description="User ID")
    home_dir: str = Field(..., description="User home directory")
    preferences: dict[str, Any] = Field(default_factory=dict, description="User preferences")


class UserConfigUpdate(BaseModel):
    """Request to update user configuration."""
    
    preferences: Optional[dict[str, Any]] = Field(None, description="User preferences")


class SessionConfigResponse(BaseModel):
    """Session configuration."""
    
    session_id: Optional[str] = Field(None, description="Current session ID")
    memory_limit_mb: int = Field(..., description="Memory limit in MB")
    persist_interactions: bool = Field(..., description="Persist interactions")
    shared_artifact_dir: str = Field(..., description="Shared artifact directory")


class SessionConfigUpdate(BaseModel):
    """Request to update session configuration."""
    
    memory_limit_mb: Optional[int] = Field(None, description="Memory limit in MB")
    persist_interactions: Optional[bool] = Field(None, description="Persist interactions")


class FullConfigResponse(BaseModel):
    """Complete configuration export."""
    
    global_config: GlobalConfigResponse
    ollama: OllamaConfigResponse
    mlflow: MLFlowConfigResponse
    vectordb: VectorDBConfigResponse
    server: ServerConfigResponse
    user: UserConfigResponse
    session: SessionConfigResponse


# === Configuration Manager ===


class ConfigManager:
    """Manages runtime configuration with persistence."""
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        self.config = config or AgenticConfig()
        self._runtime_overrides: dict[str, Any] = {}
    
    def get_global(self) -> GlobalConfigResponse:
        """Get global configuration."""
        return GlobalConfigResponse(
            mlflow_enabled=self._get_override("mlflow_enabled", self.config.mlflow_enabled),
            telemetry_enabled=self._get_override("telemetry_enabled", self.config.telemetry_enabled),
            log_level=self._get_override("log_level", self.config.log_level),
            data_dir=str(self.config.data_dir),
        )
    
    def update_global(self, updates: GlobalConfigUpdate) -> GlobalConfigResponse:
        """Update global configuration."""
        if updates.mlflow_enabled is not None:
            self._runtime_overrides["mlflow_enabled"] = updates.mlflow_enabled
        if updates.telemetry_enabled is not None:
            self._runtime_overrides["telemetry_enabled"] = updates.telemetry_enabled
        if updates.log_level is not None:
            self._validate_log_level(updates.log_level)
            self._runtime_overrides["log_level"] = updates.log_level
            self._update_log_level(updates.log_level)
        
        return self.get_global()
    
    def get_ollama(self) -> OllamaConfigResponse:
        """Get Ollama configuration."""
        return OllamaConfigResponse(
            host=self._get_override("ollama_host", self.config.ollama.host),
            default_model=self._get_override("ollama_model", self.config.ollama.default_model),
            timeout=self._get_override("ollama_timeout", self.config.ollama.timeout),
        )
    
    def update_ollama(self, updates: OllamaConfigUpdate) -> OllamaConfigResponse:
        """Update Ollama configuration."""
        if updates.host is not None:
            self._runtime_overrides["ollama_host"] = updates.host
        if updates.default_model is not None:
            self._runtime_overrides["ollama_model"] = updates.default_model
        if updates.timeout is not None:
            self._runtime_overrides["ollama_timeout"] = updates.timeout
        
        return self.get_ollama()
    
    def get_mlflow(self) -> MLFlowConfigResponse:
        """Get MLFlow configuration."""
        return MLFlowConfigResponse(
            tracking_uri=self._get_override("mlflow_uri", self.config.mlflow.tracking_uri),
            experiment_name=self._get_override("mlflow_experiment", self.config.mlflow.experiment_name),
            artifact_location=self.config.mlflow.artifact_location,
        )
    
    def update_mlflow(self, updates: MLFlowConfigUpdate) -> MLFlowConfigResponse:
        """Update MLFlow configuration."""
        if updates.tracking_uri is not None:
            self._runtime_overrides["mlflow_uri"] = updates.tracking_uri
        if updates.experiment_name is not None:
            self._runtime_overrides["mlflow_experiment"] = updates.experiment_name
        
        return self.get_mlflow()
    
    def get_vectordb(self) -> VectorDBConfigResponse:
        """Get vector database configuration."""
        return VectorDBConfigResponse(
            backend=self.config.vectordb.backend,
            path=str(self.config.vectordb.path),
            embedding_model=self.config.vectordb.embedding_model,
            embedding_dimension=self.config.vectordb.embedding_dimension,
        )
    
    def get_server(self) -> ServerConfigResponse:
        """Get server configuration."""
        return ServerConfigResponse(
            host=self.config.server.host,
            port=self.config.server.port,
            enable_mcp=self.config.server.enable_mcp,
            enable_rest=self.config.server.enable_rest,
        )
    
    def get_user(self) -> UserConfigResponse:
        """Get user configuration."""
        return UserConfigResponse(
            user_id=self.config.user.user_id,
            home_dir=str(self.config.user.home_dir),
            preferences=self._get_override("user_preferences", self.config.user.preferences),
        )
    
    def update_user(self, updates: UserConfigUpdate) -> UserConfigResponse:
        """Update user configuration."""
        if updates.preferences is not None:
            current = self._get_override("user_preferences", self.config.user.preferences)
            current.update(updates.preferences)
            self._runtime_overrides["user_preferences"] = current
        
        return self.get_user()
    
    def get_session(self) -> SessionConfigResponse:
        """Get session configuration."""
        return SessionConfigResponse(
            session_id=self.config.session_config.session_id,
            memory_limit_mb=self._get_override("session_memory", self.config.session_config.memory_limit_mb),
            persist_interactions=self._get_override("session_persist", self.config.session_config.persist_interactions),
            shared_artifact_dir=str(self.config.session_config.shared_artifact_dir),
        )
    
    def update_session(self, updates: SessionConfigUpdate) -> SessionConfigResponse:
        """Update session configuration."""
        if updates.memory_limit_mb is not None:
            self._runtime_overrides["session_memory"] = updates.memory_limit_mb
        if updates.persist_interactions is not None:
            self._runtime_overrides["session_persist"] = updates.persist_interactions
        
        return self.get_session()
    
    def get_full(self) -> FullConfigResponse:
        """Get complete configuration."""
        return FullConfigResponse(
            global_config=self.get_global(),
            ollama=self.get_ollama(),
            mlflow=self.get_mlflow(),
            vectordb=self.get_vectordb(),
            server=self.get_server(),
            user=self.get_user(),
            session=self.get_session(),
        )
    
    def export_config(self) -> dict[str, Any]:
        """Export configuration as dictionary."""
        return self.config.to_dict()
    
    def reset_overrides(self) -> None:
        """Reset all runtime overrides."""
        self._runtime_overrides.clear()
    
    def _get_override(self, key: str, default: Any) -> Any:
        """Get value with runtime override."""
        return self._runtime_overrides.get(key, default)
    
    def _validate_log_level(self, level: str) -> None:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {level}")
    
    def _update_log_level(self, level: str) -> None:
        """Update logging level at runtime."""
        import logging
        logging.getLogger().setLevel(getattr(logging, level.upper()))


# Global config manager
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


# === Endpoints ===


@router.get("", response_model=FullConfigResponse)
async def get_full_config() -> FullConfigResponse:
    """Get complete configuration."""
    logger.debug("Getting full configuration")
    
    manager = get_config_manager()
    return manager.get_full()


@router.get("/export")
async def export_config() -> dict[str, Any]:
    """Export configuration as dictionary."""
    logger.debug("Exporting configuration")
    
    manager = get_config_manager()
    return manager.export_config()


@router.post("/reset")
async def reset_overrides() -> dict[str, str]:
    """Reset all runtime configuration overrides."""
    logger.info("Resetting configuration overrides")
    
    manager = get_config_manager()
    manager.reset_overrides()
    
    return {"status": "reset"}


@router.get("/global", response_model=GlobalConfigResponse)
async def get_global_config() -> GlobalConfigResponse:
    """Get global configuration."""
    logger.debug("Getting global configuration")
    
    manager = get_config_manager()
    return manager.get_global()


@router.patch("/global", response_model=GlobalConfigResponse)
async def update_global_config(updates: GlobalConfigUpdate) -> GlobalConfigResponse:
    """Update global configuration."""
    logger.info("Updating global configuration")
    
    manager = get_config_manager()
    
    try:
        return manager.update_global(updates)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ollama", response_model=OllamaConfigResponse)
async def get_ollama_config() -> OllamaConfigResponse:
    """Get Ollama configuration."""
    logger.debug("Getting Ollama configuration")
    
    manager = get_config_manager()
    return manager.get_ollama()


@router.patch("/ollama", response_model=OllamaConfigResponse)
async def update_ollama_config(updates: OllamaConfigUpdate) -> OllamaConfigResponse:
    """Update Ollama configuration."""
    logger.info("Updating Ollama configuration")
    
    manager = get_config_manager()
    return manager.update_ollama(updates)


@router.get("/mlflow", response_model=MLFlowConfigResponse)
async def get_mlflow_config() -> MLFlowConfigResponse:
    """Get MLFlow configuration."""
    logger.debug("Getting MLFlow configuration")
    
    manager = get_config_manager()
    return manager.get_mlflow()


@router.patch("/mlflow", response_model=MLFlowConfigResponse)
async def update_mlflow_config(updates: MLFlowConfigUpdate) -> MLFlowConfigResponse:
    """Update MLFlow configuration."""
    logger.info("Updating MLFlow configuration")
    
    manager = get_config_manager()
    return manager.update_mlflow(updates)


@router.get("/vectordb", response_model=VectorDBConfigResponse)
async def get_vectordb_config() -> VectorDBConfigResponse:
    """Get vector database configuration."""
    logger.debug("Getting vector database configuration")
    
    manager = get_config_manager()
    return manager.get_vectordb()


@router.get("/server", response_model=ServerConfigResponse)
async def get_server_config() -> ServerConfigResponse:
    """Get server configuration."""
    logger.debug("Getting server configuration")
    
    manager = get_config_manager()
    return manager.get_server()


@router.get("/user", response_model=UserConfigResponse)
async def get_user_config() -> UserConfigResponse:
    """Get user configuration."""
    logger.debug("Getting user configuration")
    
    manager = get_config_manager()
    return manager.get_user()


@router.patch("/user", response_model=UserConfigResponse)
async def update_user_config(updates: UserConfigUpdate) -> UserConfigResponse:
    """Update user configuration."""
    logger.info("Updating user configuration")
    
    manager = get_config_manager()
    return manager.update_user(updates)


@router.get("/session", response_model=SessionConfigResponse)
async def get_session_config() -> SessionConfigResponse:
    """Get session configuration."""
    logger.debug("Getting session configuration")
    
    manager = get_config_manager()
    return manager.get_session()


@router.patch("/session", response_model=SessionConfigResponse)
async def update_session_config(updates: SessionConfigUpdate) -> SessionConfigResponse:
    """Update session configuration."""
    logger.info("Updating session configuration")
    
    manager = get_config_manager()
    return manager.update_session(updates)


@router.get("/validate")
async def validate_config() -> dict[str, Any]:
    """Validate current configuration."""
    logger.debug("Validating configuration")
    
    manager = get_config_manager()
    errors = []
    warnings = []
    
    # Validate data directory
    config = manager.config
    if not Path(config.data_dir).exists():
        warnings.append(f"Data directory does not exist: {config.data_dir}")
    
    # Validate Ollama host
    try:
        import httpx
        response = httpx.get(f"{config.ollama.host}/api/tags", timeout=2)
        if response.status_code != 200:
            warnings.append("Ollama server is not responding")
    except Exception:
        warnings.append("Cannot connect to Ollama server")
    
    # Validate MLFlow if enabled
    if config.mlflow_enabled:
        try:
            import httpx
            response = httpx.get(f"{config.mlflow.tracking_uri}/health", timeout=2)
            if response.status_code != 200:
                warnings.append("MLFlow server is not responding")
        except Exception:
            warnings.append("Cannot connect to MLFlow server")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }

