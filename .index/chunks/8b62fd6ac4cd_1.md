# Chunk: 8b62fd6ac4cd_1

- source: `src/agentic_assistants/server/api/config.py`
- lines: 78-157
- chunk: 2/7

```
, chroma)")
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
```
