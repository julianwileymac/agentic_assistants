"""
Configuration management for Agentic Assistants.

This module provides a centralized configuration system using Pydantic Settings,
supporting environment variables, .env files, and programmatic configuration.

The configuration hierarchy is:
    1. Global Config - Server-wide settings (persisted to config/global.yaml)
    2. User Config - User preferences (persisted to users/{user}/config.yaml)
    3. Session Config - Session-specific settings (persisted per session)

Configuration sources (in order of precedence):
    1. Programmatic values passed to __init__
    2. Environment variables
    3. .env file
    4. Persisted configuration files (YAML)
    5. Default values

Example:
    >>> config = AgenticConfig()
    >>> print(config.ollama_host)
    'http://localhost:11434'
    
    >>> # Override settings programmatically
    >>> config = AgenticConfig(mlflow_enabled=False)
    
    >>> # Load user-specific configuration
    >>> config = AgenticConfig.for_user("alice")
"""

import json
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaSettings(BaseSettings):
    """Configuration for Ollama LLM server."""

    model_config = SettingsConfigDict(
        env_prefix="OLLAMA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL",
    )
    default_model: str = Field(
        default="llama3.2",
        description="Default model to use for inference",
    )
    timeout: int = Field(
        default=120,
        description="Request timeout in seconds",
    )


class MLFlowSettings(BaseSettings):
    """Configuration for MLFlow experiment tracking."""

    model_config = SettingsConfigDict(
        env_prefix="MLFLOW_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    tracking_uri: str = Field(
        default="http://localhost:5000",
        description="MLFlow tracking server URI",
    )
    experiment_name: str = Field(
        default="agentic-experiments",
        description="Default experiment name",
    )
    artifact_location: Optional[str] = Field(
        default=None,
        description="Location for storing artifacts",
    )


class TelemetrySettings(BaseSettings):
    """Configuration for OpenTelemetry observability."""

    model_config = SettingsConfigDict(
        env_prefix="OTEL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    exporter_otlp_endpoint: str = Field(
        default="http://localhost:4317",
        description="OTLP exporter endpoint",
    )
    service_name: str = Field(
        default="agentic-assistants",
        description="Service name for tracing",
    )


class VectorDBSettings(BaseSettings):
    """Configuration for vector database storage."""

    model_config = SettingsConfigDict(
        env_prefix="VECTORDB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    backend: str = Field(
        default="lancedb",
        description="Vector database backend (lancedb, chroma)",
    )
    path: Path = Field(
        default=Path("./data/vectors"),
        description="Path for vector database storage",
    )
    embedding_model: str = Field(
        default="nomic-embed-text",
        description="Default embedding model for vector operations",
    )
    embedding_dimension: int = Field(
        default=768,
        description="Embedding vector dimension",
    )


class SessionSettings(BaseSettings):
    """Configuration for session management."""

    model_config = SettingsConfigDict(
        env_prefix="SESSION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_path: Path = Field(
        default=Path("./data/sessions.db"),
        description="Path to SQLite session database",
    )
    default_session_name: str = Field(
        default="default",
        description="Name of the default session",
    )
    auto_save: bool = Field(
        default=True,
        description="Automatically save session data on changes",
    )


class ServerSettings(BaseSettings):
    """Configuration for MCP and REST servers."""

    model_config = SettingsConfigDict(
        env_prefix="SERVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(
        default="127.0.0.1",
        description="Server host address",
    )
    port: int = Field(
        default=8080,
        description="Server port",
    )
    enable_mcp: bool = Field(
        default=True,
        description="Enable MCP (Model Context Protocol) server",
    )
    enable_rest: bool = Field(
        default=True,
        description="Enable REST API server",
    )
    
    # WebSocket configuration
    ws_ping_interval: int = Field(
        default=30,
        description="WebSocket ping interval in seconds",
    )
    ws_ping_timeout: int = Field(
        default=10,
        description="WebSocket ping timeout in seconds (time to wait for pong)",
    )
    ws_max_connections: int = Field(
        default=100,
        description="Maximum number of concurrent WebSocket connections",
    )
    ws_message_queue_size: int = Field(
        default=100,
        description="Maximum size of the WebSocket message queue per connection",
    )


class DataLayerSettings(BaseSettings):
    """Configuration for the data layer."""

    model_config = SettingsConfigDict(
        env_prefix="DATA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    cache_enabled: bool = Field(
        default=True,
        description="Enable caching for data reads",
    )
    cache_max_size: int = Field(
        default=100,
        description="Maximum number of items in LRU cache",
    )
    cache_ttl_seconds: int = Field(
        default=3600,
        description="Time-to-live for cached items in seconds",
    )
    prefer_parquet: bool = Field(
        default=True,
        description="Prefer Parquet format for tabular data",
    )


class UserConfig(BaseSettings):
    """
    User-specific configuration with persistence support.
    
    User configuration is persisted to users/{user_id}/config.yaml
    """
    
    model_config = SettingsConfigDict(
        env_prefix="AGENTIC_USER_",
        extra="ignore",
    )
    
    user_id: str = Field(default="default_user", description="Unique user identifier")
    home_dir: Path = Field(default=Path("./users/default_user"), description="User home directory")
    preferences: dict = Field(default_factory=dict, description="User preferences")
    theme: str = Field(default="dark", description="UI theme preference")
    default_experiment: Optional[str] = Field(default=None, description="Default experiment name")
    recent_sessions: list[str] = Field(default_factory=list, description="Recently accessed sessions")
    
    @classmethod
    def load_for_user(cls, user_id: str, base_dir: Path = Path("./users")) -> "UserConfig":
        """Load configuration for a specific user."""
        config_file = base_dir / user_id / "config.yaml"
        
        if config_file.exists():
            with open(config_file, "r") as f:
                data = yaml.safe_load(f) or {}
            return cls(
                user_id=user_id,
                home_dir=base_dir / user_id,
                **data
            )
        
        return cls(user_id=user_id, home_dir=base_dir / user_id)
    
    def save(self) -> None:
        """Persist user configuration to file."""
        config_file = self.home_dir / "config.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "preferences": self.preferences,
            "theme": self.theme,
            "default_experiment": self.default_experiment,
            "recent_sessions": self.recent_sessions,
        }
        
        with open(config_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def update_preferences(self, **kwargs) -> None:
        """Update user preferences and persist."""
        self.preferences.update(kwargs)
        self.save()
    
    def add_recent_session(self, session_id: str, max_recent: int = 10) -> None:
        """Add a session to recent sessions list."""
        if session_id in self.recent_sessions:
            self.recent_sessions.remove(session_id)
        self.recent_sessions.insert(0, session_id)
        self.recent_sessions = self.recent_sessions[:max_recent]
        self.save()


class SessionConfig(BaseSettings):
    """
    Session-specific configuration with persistence support.
    
    Session configuration is persisted to data/sessions/{session_id}/config.yaml
    """
    
    model_config = SettingsConfigDict(
        env_prefix="AGENTIC_SESSION_",
        extra="ignore",
    )
    
    session_id: Optional[str] = Field(default=None, description="Current session ID")
    memory_limit_mb: int = Field(default=1024, description="Memory limit for the session in MB")
    persist_interactions: bool = Field(default=True, description="Whether to persist interactions")
    shared_artifact_dir: Path = Field(default=Path("./data/shared"), description="Shared artifact directory")
    active_experiment_id: Optional[str] = Field(default=None, description="Currently active experiment")
    context_window_size: int = Field(default=4096, description="Context window size for LLM")
    max_artifacts: int = Field(default=1000, description="Maximum artifacts per session")
    auto_index: bool = Field(default=True, description="Automatically index session artifacts")
    
    @classmethod
    def load_for_session(cls, session_id: str, base_dir: Path = Path("./data/sessions")) -> "SessionConfig":
        """Load configuration for a specific session."""
        config_file = base_dir / session_id / "config.yaml"
        
        if config_file.exists():
            with open(config_file, "r") as f:
                data = yaml.safe_load(f) or {}
            return cls(session_id=session_id, **data)
        
        return cls(session_id=session_id)
    
    def save(self, base_dir: Path = Path("./data/sessions")) -> None:
        """Persist session configuration to file."""
        if not self.session_id:
            return
        
        config_file = base_dir / self.session_id / "config.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "memory_limit_mb": self.memory_limit_mb,
            "persist_interactions": self.persist_interactions,
            "shared_artifact_dir": str(self.shared_artifact_dir),
            "active_experiment_id": self.active_experiment_id,
            "context_window_size": self.context_window_size,
            "max_artifacts": self.max_artifacts,
            "auto_index": self.auto_index,
        }
        
        with open(config_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def update(self, **kwargs) -> None:
        """Update session configuration and persist."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()


class GlobalConfig(BaseSettings):
    """
    Global server-wide configuration with persistence support.
    
    Global configuration is persisted to config/global.yaml
    """
    
    model_config = SettingsConfigDict(
        env_prefix="AGENTIC_GLOBAL_",
        extra="ignore",
    )
    
    default_model: str = Field(default="llama3.2", description="Default LLM model")
    max_concurrent_sessions: int = Field(default=10, description="Maximum concurrent sessions")
    enable_anonymous_users: bool = Field(default=True, description="Allow anonymous users")
    artifact_retention_days: int = Field(default=30, description="Days to retain artifacts")
    log_retention_days: int = Field(default=7, description="Days to retain logs")
    enable_experiment_tracking: bool = Field(default=True, description="Enable MLFlow tracking")
    enable_telemetry: bool = Field(default=True, description="Enable OpenTelemetry")
    admin_users: list[str] = Field(default_factory=list, description="Admin user IDs")
    
    _config_file: Path = Path("./config/global.yaml")
    
    @classmethod
    def load(cls, config_dir: Path = Path("./config")) -> "GlobalConfig":
        """Load global configuration from file."""
        config_file = config_dir / "global.yaml"
        
        if config_file.exists():
            with open(config_file, "r") as f:
                data = yaml.safe_load(f) or {}
            instance = cls(**data)
            instance._config_file = config_file
            return instance
        
        instance = cls()
        instance._config_file = config_file
        return instance
    
    def save(self) -> None:
        """Persist global configuration to file."""
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "default_model": self.default_model,
            "max_concurrent_sessions": self.max_concurrent_sessions,
            "enable_anonymous_users": self.enable_anonymous_users,
            "artifact_retention_days": self.artifact_retention_days,
            "log_retention_days": self.log_retention_days,
            "enable_experiment_tracking": self.enable_experiment_tracking,
            "enable_telemetry": self.enable_telemetry,
            "admin_users": self.admin_users,
        }
        
        with open(self._config_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def update(self, **kwargs) -> None:
        """Update global configuration and persist."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()


class AgenticConfig(BaseSettings):
    """
    Main configuration class for Agentic Assistants.
    
    This class aggregates all sub-configurations and provides
    top-level settings for the framework.
    
    Configuration hierarchy:
        1. Global Config - Server-wide settings
        2. User Config - Per-user preferences
        3. Session Config - Per-session settings
    
    Configuration sources (in order of precedence):
        1. Programmatic values passed to __init__
        2. Environment variables
        3. .env file
        4. Persisted YAML files
        5. Default values
    
    Example:
        >>> config = AgenticConfig()
        >>> config.ollama.host
        'http://localhost:11434'
        
        >>> config = AgenticConfig(mlflow_enabled=False)
        >>> config.mlflow_enabled
        False
        
        >>> # Load for specific user
        >>> config = AgenticConfig.for_user("alice")
        
        >>> # Load for specific session
        >>> config = AgenticConfig.for_session("session123")
    """

    model_config = SettingsConfigDict(
        env_prefix="AGENTIC_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Feature toggles
    mlflow_enabled: bool = Field(
        default=True,
        description="Enable MLFlow experiment tracking",
    )
    telemetry_enabled: bool = Field(
        default=True,
        description="Enable OpenTelemetry tracing and metrics",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Data storage
    data_dir: Path = Field(
        default=Path("./data"),
        description="Directory for local data storage",
    )
    
    config_dir: Path = Field(
        default=Path("./config"),
        description="Directory for configuration files",
    )
    
    users_dir: Path = Field(
        default=Path("./users"),
        description="Directory for user data",
    )

    # Sub-configurations (populated lazily)
    _ollama: Optional[OllamaSettings] = None
    _mlflow: Optional[MLFlowSettings] = None
    _telemetry: Optional[TelemetrySettings] = None
    _vectordb: Optional[VectorDBSettings] = None
    _session: Optional[SessionSettings] = None
    _server: Optional[ServerSettings] = None
    _data_layer: Optional[DataLayerSettings] = None
    _user: Optional[UserConfig] = None
    _session_config: Optional[SessionConfig] = None
    _global: Optional[GlobalConfig] = None

    @property
    def ollama(self) -> OllamaSettings:
        """Get Ollama configuration."""
        if self._ollama is None:
            self._ollama = OllamaSettings()
        return self._ollama

    @property
    def mlflow(self) -> MLFlowSettings:
        """Get MLFlow configuration."""
        if self._mlflow is None:
            self._mlflow = MLFlowSettings()
        return self._mlflow

    @property
    def telemetry(self) -> TelemetrySettings:
        """Get telemetry configuration."""
        if self._telemetry is None:
            self._telemetry = TelemetrySettings()
        return self._telemetry

    @property
    def vectordb(self) -> VectorDBSettings:
        """Get vector database configuration."""
        if self._vectordb is None:
            self._vectordb = VectorDBSettings()
        return self._vectordb

    @property
    def session(self) -> SessionSettings:
        """Get session configuration."""
        if self._session is None:
            self._session = SessionSettings()
        return self._session

    @property
    def server(self) -> ServerSettings:
        """Get server configuration."""
        if self._server is None:
            self._server = ServerSettings()
        return self._server

    @property
    def data_layer(self) -> DataLayerSettings:
        """Get data layer configuration."""
        if self._data_layer is None:
            self._data_layer = DataLayerSettings()
        return self._data_layer

    @property
    def user(self) -> UserConfig:
        """Get user configuration."""
        if self._user is None:
            self._user = UserConfig()
        return self._user

    @property
    def session_config(self) -> SessionConfig:
        """Get session-level configuration."""
        if self._session_config is None:
            self._session_config = SessionConfig()
        return self._session_config

    @property
    def global_config(self) -> GlobalConfig:
        """Get global configuration."""
        if self._global is None:
            self._global = GlobalConfig.load(self.config_dir)
        return self._global
    
    @classmethod
    def for_user(cls, user_id: str, **kwargs) -> "AgenticConfig":
        """
        Create a configuration instance for a specific user.
        
        Args:
            user_id: The user identifier
            **kwargs: Additional configuration overrides
        
        Returns:
            AgenticConfig instance with user-specific settings
        """
        config = cls(**kwargs)
        config._user = UserConfig.load_for_user(user_id, config.users_dir)
        return config
    
    @classmethod
    def for_session(cls, session_id: str, user_id: Optional[str] = None, **kwargs) -> "AgenticConfig":
        """
        Create a configuration instance for a specific session.
        
        Args:
            session_id: The session identifier
            user_id: Optional user identifier
            **kwargs: Additional configuration overrides
        
        Returns:
            AgenticConfig instance with session-specific settings
        """
        config = cls(**kwargs)
        config._session_config = SessionConfig.load_for_session(session_id, config.data_dir / "sessions")
        
        if user_id:
            config._user = UserConfig.load_for_user(user_id, config.users_dir)
        
        return config
    
    def switch_user(self, user_id: str) -> None:
        """Switch to a different user's configuration."""
        self._user = UserConfig.load_for_user(user_id, self.users_dir)
    
    def switch_session(self, session_id: str) -> None:
        """Switch to a different session's configuration."""
        self._session_config = SessionConfig.load_for_session(session_id, self.data_dir / "sessions")
    
    def save_all(self) -> None:
        """Persist all configuration to files."""
        if self._global is not None:
            self._global.save()
        if self._user is not None:
            self._user.save()
        if self._session_config is not None and self._session_config.session_id:
            self._session_config.save(self.data_dir / "sessions")
    
    def reload(self) -> None:
        """Reload all configuration from files."""
        self._global = GlobalConfig.load(self.config_dir)
        if self._user is not None:
            self._user = UserConfig.load_for_user(self._user.user_id, self.users_dir)
        if self._session_config is not None and self._session_config.session_id:
            self._session_config = SessionConfig.load_for_session(
                self._session_config.session_id,
                self.data_dir / "sessions"
            )

    def ensure_data_dir(self) -> Path:
        """Ensure the data directory exists and return its path."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir

    def to_dict(self) -> dict:
        """Export configuration as a dictionary."""
        return {
            "mlflow_enabled": self.mlflow_enabled,
            "telemetry_enabled": self.telemetry_enabled,
            "log_level": self.log_level,
            "data_dir": str(self.data_dir),
            "config_dir": str(self.config_dir),
            "users_dir": str(self.users_dir),
            "global": {
                "default_model": self.global_config.default_model,
                "max_concurrent_sessions": self.global_config.max_concurrent_sessions,
                "enable_anonymous_users": self.global_config.enable_anonymous_users,
                "artifact_retention_days": self.global_config.artifact_retention_days,
                "log_retention_days": self.global_config.log_retention_days,
                "enable_experiment_tracking": self.global_config.enable_experiment_tracking,
                "enable_telemetry": self.global_config.enable_telemetry,
            },
            "ollama": {
                "host": self.ollama.host,
                "default_model": self.ollama.default_model,
                "timeout": self.ollama.timeout,
            },
            "mlflow": {
                "tracking_uri": self.mlflow.tracking_uri,
                "experiment_name": self.mlflow.experiment_name,
                "artifact_location": self.mlflow.artifact_location,
            },
            "telemetry": {
                "endpoint": self.telemetry.exporter_otlp_endpoint,
                "service_name": self.telemetry.service_name,
            },
            "vectordb": {
                "backend": self.vectordb.backend,
                "path": str(self.vectordb.path),
                "embedding_model": self.vectordb.embedding_model,
                "embedding_dimension": self.vectordb.embedding_dimension,
            },
            "session": {
                "database_path": str(self.session.database_path),
                "default_session_name": self.session.default_session_name,
                "auto_save": self.session.auto_save,
            },
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "enable_mcp": self.server.enable_mcp,
                "enable_rest": self.server.enable_rest,
            },
            "data_layer": {
                "cache_enabled": self.data_layer.cache_enabled,
                "cache_max_size": self.data_layer.cache_max_size,
                "cache_ttl_seconds": self.data_layer.cache_ttl_seconds,
                "prefer_parquet": self.data_layer.prefer_parquet,
            },
            "user": {
                "user_id": self.user.user_id,
                "home_dir": str(self.user.home_dir),
                "theme": self.user.theme,
                "preferences": self.user.preferences,
            },
            "session_config": {
                "session_id": self.session_config.session_id,
                "memory_limit_mb": self.session_config.memory_limit_mb,
                "persist_interactions": self.session_config.persist_interactions,
                "context_window_size": self.session_config.context_window_size,
            },
        }
    
    def to_yaml(self) -> str:
        """Export configuration as YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False)
    
    def to_json(self) -> str:
        """Export configuration as JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_yaml_file(cls, path: Path) -> "AgenticConfig":
        """Load configuration from a YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        return cls(**data)
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.users_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "sessions").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "artifacts").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "shared").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "vectors").mkdir(parents=True, exist_ok=True)

