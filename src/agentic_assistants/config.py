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
from typing import Any, Optional, List

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


class LLMSettings(BaseSettings):
    """Configuration for generic chat inference providers."""

    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    provider: str = Field(
        default="ollama",
        description="Active chat provider (ollama, huggingface_local, openai_compatible)",
    )
    model: Optional[str] = Field(
        default=None,
        description="Default chat model for the active provider",
    )
    timeout: int = Field(
        default=120,
        description="Default request timeout in seconds",
    )

    # Ollama settings
    ollama_host: Optional[str] = Field(
        default=None,
        description="Optional Ollama host override for chat inference",
    )

    # OpenAI-compatible settings
    openai_base_url: str = Field(
        default="http://localhost:8000/v1",
        description="Base URL for OpenAI-compatible endpoints (vLLM, TGI, etc.)",
    )
    openai_api_key_env: str = Field(
        default="OPENAI_API_KEY",
        description="Environment variable name that stores the OpenAI-compatible API key",
    )

    # Hugging Face local settings
    hf_execution_mode: str = Field(
        default="hybrid",
        description="Hugging Face execution mode (local, remote, hybrid)",
    )
    hf_local_model: Optional[str] = Field(
        default=None,
        description="Default Hugging Face model ID for local inference",
    )
    hf_device_map: str = Field(
        default="auto",
        description="Transformers device_map for local Hugging Face inference",
    )
    hf_torch_dtype: Optional[str] = Field(
        default=None,
        description="Optional torch dtype for local Hugging Face inference",
    )
    hf_trust_remote_code: bool = Field(
        default=False,
        description="Trust remote model code when loading Hugging Face models",
    )

    fallback_provider: Optional[str] = Field(
        default=None,
        description="Optional fallback provider when the primary provider fails",
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
        description="MLFlow tracking server URI (defaults to cluster service if available)",
    )
    experiment_name: str = Field(
        default="agentic-experiments",
        description="Default experiment name",
    )
    artifact_location: Optional[str] = Field(
        default=None,
        description="Location for storing artifacts (defaults to MinIO S3 if configured)",
    )
    backend_store_uri: Optional[str] = Field(
        default=None,
        description="PostgreSQL backend store URI for MLflow (defaults to config.postgresql.dsn if enabled)",
    )
    s3_endpoint_url: Optional[str] = Field(
        default=None,
        description="S3/MinIO endpoint URL for artifacts (defaults to config.minio.endpoint if enabled)",
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
    fallback_to_file: bool = Field(
        default=True,
        description="Fall back to file-based OTLP JSON export when no collector is reachable",
    )
    file_export_path: str = Field(
        default="data/traces",
        description="Directory for file-based trace export (OTLP JSON)",
    )
    file_export_format: str = Field(
        default="otlp_json",
        description="Export format for file-based traces (otlp_json)",
    )


class EmbeddingSettings(BaseSettings):
    """Configuration for embedding providers with local/remote mode support."""

    model_config = SettingsConfigDict(
        env_prefix="EMBEDDING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Mode selection
    mode: str = Field(
        default="local",
        description="Embedding mode: 'local' or 'remote'",
    )
    
    # Local provider settings
    local_provider: str = Field(
        default="ollama",
        description="Local embedding provider (ollama, sentence_transformers)",
    )
    local_model: str = Field(
        default="nomic-embed-text",
        description="Local embedding model name",
    )
    
    # Remote provider settings
    remote_provider: str = Field(
        default="openai",
        description="Remote embedding provider (openai, huggingface, cohere)",
    )
    remote_model: str = Field(
        default="text-embedding-3-small",
        description="Remote embedding model name",
    )
    remote_api_key_env: str = Field(
        default="OPENAI_API_KEY",
        description="Environment variable for remote API key",
    )
    
    # HuggingFace Inference API settings
    huggingface_inference_endpoint: Optional[str] = Field(
        default=None,
        description="Custom HuggingFace inference endpoint URL",
    )
    huggingface_api_key_env: str = Field(
        default="HF_API_KEY",
        description="Environment variable for HuggingFace API key",
    )
    
    # Fallback behavior
    fallback_to_local: bool = Field(
        default=True,
        description="Fall back to local embeddings if remote fails",
    )
    
    # Performance settings
    batch_size: int = Field(
        default=32,
        description="Batch size for embedding generation",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retries for remote embedding calls",
    )
    timeout: float = Field(
        default=60.0,
        description="Timeout in seconds for embedding requests",
    )
    
    # Caching
    cache_embeddings: bool = Field(
        default=True,
        description="Cache embeddings to avoid recomputation",
    )
    cache_backend: str = Field(
        default="redis",
        description="Cache backend: 'redis', 'memory', 'disk'",
    )
    
    # Model dimensions (auto-detected but can be overridden)
    dimension_overrides: dict = Field(
        default_factory=dict,
        description="Model-specific dimension overrides",
    )
    
    @property
    def active_provider(self) -> str:
        """Get the currently active provider based on mode."""
        return self.local_provider if self.mode == "local" else self.remote_provider
    
    @property
    def active_model(self) -> str:
        """Get the currently active model based on mode."""
        return self.local_model if self.mode == "local" else self.remote_model


class VectorDBSettings(BaseSettings):
    """Configuration for vector database storage with multi-level scoping."""

    model_config = SettingsConfigDict(
        env_prefix="VECTORDB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    backend: str = Field(
        default="lancedb",
        description="Vector database backend (lancedb, chroma, both)",
    )
    path: Path = Field(
        default=Path("./data/vectors"),
        description="Path for vector database storage",
    )
    embedding_provider: str = Field(
        default="ollama",
        description="Embedding provider (ollama, sentence_transformers, openai)",
    )
    embedding_model: str = Field(
        default="nomic-embed-text",
        description="Default embedding model for vector operations",
    )
    embedding_dimension: int = Field(
        default=768,
        description="Embedding vector dimension",
    )
    use_both_backends: bool = Field(
        default=False,
        description="Store in both LanceDB and ChromaDB simultaneously",
    )
    
    # Multi-level scope configuration
    default_scope: str = Field(
        default="project",
        description="Default vector store scope (global, user, project, experiment)",
    )
    global_namespace: str = Field(
        default="global",
        description="Namespace prefix for global collections",
    )
    user_namespace_template: str = Field(
        default="user_{user_id}",
        description="Template for user-scoped collection namespaces",
    )
    project_namespace_template: str = Field(
        default="project_{project_id}",
        description="Template for project-scoped collection namespaces",
    )
    experiment_namespace_template: str = Field(
        default="exp_{experiment_id}",
        description="Template for experiment-scoped collection namespaces",
    )
    
    # Scope-specific paths
    global_path: Optional[Path] = Field(
        default=None,
        description="Override path for global vector storage",
    )
    user_path_template: str = Field(
        default="./users/{user_id}/vectors",
        description="Path template for user vector storage",
    )
    project_path_template: str = Field(
        default="./data/projects/{project_id}/vectors",
        description="Path template for project vector storage",
    )
    
    # Cross-scope features
    enable_cross_scope_search: bool = Field(
        default=False,
        description="Allow searching across multiple scopes",
    )
    enable_scope_inheritance: bool = Field(
        default=True,
        description="Project collections can inherit from global in search",
    )
    
    # Lineage tracking
    track_lineage: bool = Field(
        default=True,
        description="Track document lineage by default",
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


class IndexingSettings(BaseSettings):
    """Configuration for codebase indexing."""

    model_config = SettingsConfigDict(
        env_prefix="INDEXING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    version: str = Field(
        default="2.0",
        description="Current indexing schema version",
    )
    auto_index_new_projects: bool = Field(
        default=False,
        description="Automatically index new projects (prompts user by default)",
    )
    chunk_size: int = Field(
        default=1024,
        description="Default chunk size for indexing",
    )
    chunk_overlap: int = Field(
        default=128,
        description="Overlap between chunks",
    )
    max_file_size_mb: int = Field(
        default=1,
        description="Maximum file size to index in MB",
    )
    excluded_patterns: list[str] = Field(
        default_factory=lambda: [
            "*.pyc", "__pycache__", "node_modules", ".git",
            "*.egg-info", "dist", "build", ".venv", "venv"
        ],
        description="Patterns to exclude from indexing",
    )


class KubernetesSettings(BaseSettings):
    """Configuration for Kubernetes cluster connection and management."""

    model_config = SettingsConfigDict(
        env_prefix="K8S_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(
        default=False,
        description="Enable Kubernetes cluster integration",
    )
    kubeconfig_path: Optional[str] = Field(
        default=None,
        description="Path to kubeconfig file (uses default if None)",
    )
    context: Optional[str] = Field(
        default=None,
        description="Kubernetes context to use (uses current-context if None)",
    )
    namespace: str = Field(
        default="agentic",
        description="Default namespace for deployments",
    )
    cluster_endpoint: Optional[str] = Field(
        default=None,
        description="Direct cluster API endpoint (alternative to kubeconfig)",
    )
    cluster_token: Optional[str] = Field(
        default=None,
        description="Bearer token for cluster authentication",
    )
    verify_ssl: bool = Field(
        default=True,
        description="Verify SSL certificates for cluster connections",
    )
    default_deploy_namespace: str = Field(
        default="agentic-workloads",
        description="Namespace for deploying agents and flows",
    )
    enable_distributed: bool = Field(
        default=True,
        description="Enable distributed computing with Dask/Ray",
    )
    model_serving_namespace: str = Field(
        default="model-serving",
        description="Namespace for LLM model deployments",
    )
    # Resource defaults
    default_cpu_request: str = Field(
        default="100m",
        description="Default CPU request for deployments",
    )
    default_memory_request: str = Field(
        default="256Mi",
        description="Default memory request for deployments",
    )
    default_cpu_limit: str = Field(
        default="1000m",
        description="Default CPU limit for deployments",
    )
    default_memory_limit: str = Field(
        default="1Gi",
        description="Default memory limit for deployments",
    )
    # Auto-detection and debugging
    autodetect_enabled: bool = Field(
        default=True,
        description="Enable automatic kubeconfig discovery",
    )
    autodetect_extra_paths: str = Field(
        default="",
        description="Comma-separated list of additional kubeconfig paths to try",
    )
    request_timeout_seconds: int = Field(
        default=10,
        description="Request timeout for API calls in seconds",
    )
    insecure_skip_tls_verify: bool = Field(
        default=False,
        description="Skip TLS verification for cluster connections (insecure)",
    )
    prefer_incluster: Optional[bool] = Field(
        default=None,  # Auto-detect: True if running in cluster, False otherwise
        description="Prefer in-cluster config over kubeconfig (auto-detected if None)",
    )


class MinIOSettings(BaseSettings):
    """Configuration for MinIO/S3-compatible object storage."""

    model_config = SettingsConfigDict(
        env_prefix="MINIO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(
        default=True,
        description="Enable MinIO storage integration",
    )
    endpoint: str = Field(
        default="minio.data-services.svc.cluster.local:9000",
        description="MinIO server endpoint",
    )
    external_endpoint: Optional[str] = Field(
        default=None,
        description="External MinIO endpoint for access outside cluster",
    )
    access_key: Optional[str] = Field(
        default="minioadmin",
        description="MinIO access key",
    )
    secret_key: Optional[str] = Field(
        default="minioadmin123",
        description="MinIO secret key",
    )
    secure: bool = Field(
        default=False,
        description="Use HTTPS for MinIO connections",
    )
    default_bucket: str = Field(
        default="agentic-artifacts",
        description="Default bucket for artifact storage",
    )
    model_bucket: str = Field(
        default="model-cache",
        description="Bucket for cached model files",
    )
    region: str = Field(
        default="us-east-1",
        description="S3 region (for compatibility)",
    )


class JupyterSettings(BaseSettings):
    """Configuration for the managed Jupyter notebook server."""

    model_config = SettingsConfigDict(
        env_prefix="JUPYTER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(
        default=True,
        description="Enable managed notebook server (auto-starts with backend)",
    )
    port: int = Field(
        default=8888,
        description="Notebook server port",
    )
    host: str = Field(
        default="127.0.0.1",
        description="Notebook server bind address",
    )
    token: str = Field(
        default="",
        description="Notebook auth token (empty = no auth for local dev)",
    )
    notebook_dir: str = Field(
        default="./notebooks",
        description="Root directory served by the notebook server",
    )
    base_url: str = Field(
        default="/",
        description="Base URL path for the notebook server",
    )
    external_url: Optional[str] = Field(
        default=None,
        description="External JupyterHub URL; when set, disables local managed server",
    )
    kernel_name: str = Field(
        default="agentic",
        description="Name of the IPython kernel registered for the framework environment",
    )
    startup_timeout: int = Field(
        default=30,
        description="Seconds to wait for notebook server readiness",
    )
    log_to_stdout: bool = Field(
        default=True,
        description="Pipe notebook server logs through structured logger to stdout",
    )


class PostgreSQLSettings(BaseSettings):
    """Configuration for PostgreSQL database persistence."""

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(
        default=False,
        description="Enable PostgreSQL database integration",
    )
    host: str = Field(
        default="postgresql.data-services.svc.cluster.local",
        description="PostgreSQL server host",
    )
    port: int = Field(
        default=5432,
        description="PostgreSQL server port",
    )
    database: str = Field(
        default="mlflow",
        description="Default database name",
    )
    user: str = Field(
        default="mlflow",
        description="PostgreSQL user",
    )
    password: Optional[str] = Field(
        default="mlflow123",
        description="PostgreSQL password",
    )
    connection_string: Optional[str] = Field(
        default=None,
        description="Full PostgreSQL connection string (overrides individual settings)",
    )
    
    # Connection pool settings
    pool_size: int = Field(
        default=5,
        description="Connection pool size",
    )
    max_overflow: int = Field(
        default=10,
        description="Maximum overflow connections",
    )
    pool_timeout: int = Field(
        default=30,
        description="Pool connection timeout in seconds",
    )
    
    @property
    def dsn(self) -> str:
        """Get PostgreSQL connection DSN."""
        if self.connection_string:
            return self.connection_string
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def async_dsn(self) -> str:
        """Get PostgreSQL async connection DSN."""
        if self.connection_string:
            return self.connection_string.replace("postgresql://", "postgresql+asyncpg://")
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class SupabaseSettings(BaseSettings):
    """Configuration for Supabase integration."""

    model_config = SettingsConfigDict(
        env_prefix="SUPABASE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(
        default=False,
        description="Enable Supabase integration",
    )
    url: Optional[str] = Field(
        default=None,
        description="Supabase project URL",
    )
    key: Optional[str] = Field(
        default=None,
        description="Supabase anon/service key",
    )
    service_key: Optional[str] = Field(
        default=None,
        description="Supabase service role key (for admin operations)",
    )
    jwt_secret: Optional[str] = Field(
        default=None,
        description="JWT secret for token verification",
    )
    db_url: Optional[str] = Field(
        default=None,
        description="Direct database URL (alternative to Supabase client)",
    )
    realtime_enabled: bool = Field(
        default=True,
        description="Enable realtime subscriptions",
    )
    auto_refresh_token: bool = Field(
        default=True,
        description="Automatically refresh auth tokens",
    )


class DatabaseSettings(BaseSettings):
    """Configuration for database layer with hybrid support."""

    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    type: str = Field(
        default="sqlite",
        description="Database type (sqlite, postgres, supabase)",
    )
    auto_migrate: bool = Field(
        default=True,
        description="Automatically run migrations on startup",
    )
    backup_enabled: bool = Field(
        default=True,
        description="Enable automatic database backups",
    )
    backup_interval_hours: int = Field(
        default=24,
        description="Backup interval in hours",
    )
    backup_retention_days: int = Field(
        default=7,
        description="Days to retain backups",
    )


class RedisSettings(BaseSettings):
    """Configuration for Redis cache and solution store."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(
        default=False,
        description="Enable Redis integration",
    )
    url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL",
    )
    host: str = Field(
        default="localhost",
        description="Redis server host",
    )
    port: int = Field(
        default=6379,
        description="Redis server port",
    )
    db: int = Field(
        default=0,
        description="Redis database number",
    )
    password: Optional[str] = Field(
        default=None,
        description="Redis password",
    )
    prefix: str = Field(
        default="agentic:",
        description="Key prefix for all Redis keys",
    )
    
    # Connection pool settings
    max_connections: int = Field(
        default=10,
        description="Maximum number of connections in the pool",
    )
    socket_timeout: float = Field(
        default=5.0,
        description="Socket timeout in seconds",
    )
    socket_connect_timeout: float = Field(
        default=5.0,
        description="Socket connection timeout in seconds",
    )
    
    # TTL settings for different cache types
    default_ttl: int = Field(
        default=3600,
        description="Default TTL in seconds (1 hour)",
    )
    solution_cache_ttl: int = Field(
        default=86400,
        description="TTL for cached solutions (24 hours)",
    )
    workflow_state_ttl: int = Field(
        default=3600,
        description="TTL for workflow state (1 hour)",
    )
    session_cache_ttl: int = Field(
        default=7200,
        description="TTL for session data (2 hours)",
    )
    embedding_cache_ttl: int = Field(
        default=604800,
        description="TTL for cached embeddings (7 days)",
    )
    
    # Feature flags
    cache_embeddings: bool = Field(
        default=True,
        description="Cache embedding vectors in Redis",
    )
    cache_solutions: bool = Field(
        default=True,
        description="Cache agent solutions in Redis",
    )
    cache_workflow_state: bool = Field(
        default=True,
        description="Cache workflow state in Redis",
    )
    
    @property
    def connection_url(self) -> str:
        """Get Redis connection URL."""
        if self.url and self.url != "redis://localhost:6379":
            return self.url
        
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class HuggingFaceSettings(BaseSettings):
    """Configuration for HuggingFace Hub and library integration."""

    model_config = SettingsConfigDict(
        env_prefix="HF_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    token: Optional[str] = Field(
        default=None,
        description="HuggingFace API token (also reads HUGGINGFACE_TOKEN)",
    )
    cache_dir: Path = Field(
        default=Path("./data/models/hf_cache"),
        description="Local cache directory for HuggingFace downloads",
    )
    datasets_cache_dir: Path = Field(
        default=Path("./data/datasets/hf_cache"),
        description="Local cache directory for HuggingFace datasets",
    )
    default_org: Optional[str] = Field(
        default=None,
        description="Default HuggingFace organization for push operations",
    )
    hub_url: str = Field(
        default="https://huggingface.co",
        description="HuggingFace Hub URL",
    )
    offline_mode: bool = Field(
        default=False,
        description="Run in offline mode (no Hub requests)",
    )
    papers_enabled: bool = Field(
        default=True,
        description="Enable paper search/retrieval from HuggingFace",
    )
    default_revision: str = Field(
        default="main",
        description="Default revision/branch for model downloads",
    )


class NemotronSettings(BaseSettings):
    """Configuration for Nemotron model integration."""

    model_config = SettingsConfigDict(
        env_prefix="NEMOTRON_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    default_model: str = Field(
        default="nvidia/Llama-3.1-Nemotron-Nano-8B-v1",
        description="Default Nemotron model ID",
    )
    cache_dir: Path = Field(
        default=Path("./data/models/nemotron"),
        description="Local cache directory for Nemotron model weights",
    )
    serving_backend: str = Field(
        default="ollama",
        description="Preferred serving backend: ollama, vllm, tgi",
    )
    serving_url: Optional[str] = Field(
        default=None,
        description="URL of the running Nemotron serving endpoint",
    )
    quantization: str = Field(
        default="none",
        description="Default quantization: none, int8, int4, gptq, awq",
    )
    trust_remote_code: bool = Field(
        default=True,
        description="Trust remote code when loading models",
    )


class DataHubSettings(BaseSettings):
    """Configuration for DataHub data catalog integration."""

    model_config = SettingsConfigDict(
        env_prefix="DATAHUB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(
        default=False,
        description="Enable DataHub catalog integration",
    )
    gms_url: str = Field(
        default="http://localhost:8080",
        description="DataHub GMS REST API endpoint",
    )
    frontend_url: str = Field(
        default="http://datahub.local",
        description="DataHub frontend UI URL (for external links)",
    )
    token: Optional[str] = Field(
        default=None,
        description="DataHub personal access token for API authentication",
    )
    iceberg_enabled: bool = Field(
        default=True,
        description="Enable Iceberg catalog features via DataHub GMS",
    )


class IcebergSettings(BaseSettings):
    """Configuration for Apache Iceberg catalog backed by MinIO."""

    model_config = SettingsConfigDict(
        env_prefix="ICEBERG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    catalog_uri: str = Field(
        default="http://localhost:8080/iceberg",
        description="Iceberg REST catalog endpoint (DataHub GMS /iceberg)",
    )
    warehouse: str = Field(
        default="s3://iceberg-warehouse/",
        description="Default warehouse location in S3/MinIO",
    )
    s3_endpoint: str = Field(
        default="http://localhost:9000",
        description="S3-compatible endpoint (MinIO)",
    )
    s3_access_key: str = Field(
        default="minioadmin",
        description="S3 access key",
    )
    s3_secret_key: str = Field(
        default="minioadmin123",
        description="S3 secret key",
    )


class DbtSettings(BaseSettings):
    """Configuration for dbt-core data transformations."""

    model_config = SettingsConfigDict(
        env_prefix="DBT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(
        default=False,
        description="Enable dbt integration",
    )
    project_dir: str = Field(
        default="",
        description="Path to the dbt project directory",
    )
    profiles_dir: str = Field(
        default="",
        description="Path to the dbt profiles directory",
    )
    target: str = Field(
        default="dev",
        description="dbt target profile to use",
    )
    postgres_host: str = Field(
        default="localhost",
        description="PostgreSQL host for dbt connections",
    )
    postgres_port: int = Field(
        default=5432,
        description="PostgreSQL port for dbt connections",
    )
    postgres_database: str = Field(
        default="agentic",
        description="PostgreSQL database for dbt",
    )
    postgres_user: str = Field(
        default="postgres",
        description="PostgreSQL user for dbt",
    )
    postgres_password: str = Field(
        default="",
        description="PostgreSQL password for dbt",
    )


class FrameworkAssistantSettings(BaseSettings):
    """Configuration for the built-in Framework Assistant Agent."""

    model_config = SettingsConfigDict(
        env_prefix="ASSISTANT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(
        default=True,
        description="Enable the framework assistant agent",
    )
    default_framework: str = Field(
        default="crewai",
        description="Default agent framework (crewai, langgraph, autogen, google_adk, agno, langflow)",
    )
    model: str = Field(
        default="llama3.2",
        description="LLM model for the assistant",
    )
    provider: str = Field(
        default="ollama",
        description="Assistant LLM provider (ollama, huggingface_local, openai_compatible)",
    )
    endpoint: Optional[str] = Field(
        default=None,
        description="Optional assistant endpoint override for remote inference providers",
    )
    openai_api_key_env: str = Field(
        default="OPENAI_API_KEY",
        description="API key environment variable for OpenAI-compatible assistant requests",
    )
    hf_execution_mode: str = Field(
        default="hybrid",
        description="Assistant Hugging Face execution mode (local, remote, hybrid)",
    )
    enable_coding_helper: bool = Field(
        default=True,
        description="Enable coding assistance features",
    )
    enable_framework_guide: bool = Field(
        default=True,
        description="Enable framework guidance features",
    )
    enable_meta_analysis: bool = Field(
        default=True,
        description="Enable meta-analysis for self-improvement suggestions",
    )
    rag_enabled: bool = Field(
        default=True,
        description="Enable RAG for context-aware responses",
    )
    memory_enabled: bool = Field(
        default=True,
        description="Enable persistent memory for conversation context",
    )
    code_kb_project_id: Optional[str] = Field(
        default=None,
        description="Project ID for the code knowledge base",
    )
    docs_kb_name: str = Field(
        default="framework_docs",
        description="Knowledge base name for framework documentation",
    )
    usage_tracking_enabled: bool = Field(
        default=True,
        description="Enable usage tracking for analytics and meta-analysis",
    )
    usage_db_path: Path = Field(
        default=Path("./data/observability/usage.db"),
        description="Path to the usage tracking database",
    )
    meta_analysis_interval_hours: int = Field(
        default=24,
        description="Interval for automatic meta-analysis runs (in hours)",
    )
    max_context_messages: int = Field(
        default=20,
        description="Maximum number of messages to include in conversation context",
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Custom system prompt for the assistant (uses default if None)",
    )


class ServiceConfig(BaseSettings):
    """Configuration for an external service resource."""

    model_config = SettingsConfigDict(extra="ignore")

    name: str = Field(default="", description="Service name")
    service_type: str = Field(
        default="api_endpoint",
        description="Service type (web_ui, api_endpoint, file_store, background_service, database, ml_deployment)",
    )
    endpoint_url: str = Field(default="", description="Service endpoint URL")
    health_endpoint: Optional[str] = Field(default=None, description="Health check endpoint")
    auth_type: Optional[str] = Field(default=None, description="Authentication type (none, api_key, oauth, basic)")
    credentials_ref: Optional[str] = Field(default=None, description="Reference to credentials in secrets store")
    config_yaml: str = Field(default="", description="Additional service configuration in YAML")


class GitConfig(BaseSettings):
    """Configuration for git integration."""

    model_config = SettingsConfigDict(extra="ignore")

    remote_url: Optional[str] = Field(default=None, description="Git remote URL")
    branch: str = Field(default="main", description="Default branch")
    auto_sync: bool = Field(default=False, description="Automatically sync with remote")
    ssh_key_ref: Optional[str] = Field(default=None, description="Reference to SSH key in secrets store")


class TestingSettings(BaseSettings):
    """Configuration for the testing / execution sandbox subsystem."""

    model_config = SettingsConfigDict(
        env_prefix="TESTING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(
        default=True,
        description="Enable testing features",
    )
    sandbox_default: bool = Field(
        default=False,
        description="Run tests in a sandboxed environment by default",
    )
    tracking_default: bool = Field(
        default=True,
        description="Enable MLFlow tracking for test runs by default",
    )
    agent_eval_default: bool = Field(
        default=False,
        description="Enable agent-based evaluation by default",
    )
    rl_metrics_default: bool = Field(
        default=False,
        description="Enable RL metrics collection by default",
    )
    eval_provider: Optional[str] = Field(
        default=None,
        description="Default provider for LLM-based evaluation (falls back to global LLM provider)",
    )
    eval_model: Optional[str] = Field(
        default=None,
        description="Default model for LLM-based evaluation (falls back to global LLM model)",
    )
    eval_endpoint: Optional[str] = Field(
        default=None,
        description="Optional endpoint override for evaluation provider",
    )
    eval_hf_execution_mode: str = Field(
        default="hybrid",
        description="Hugging Face execution mode used by evaluation (local, remote, hybrid)",
    )
    timeout_seconds: Optional[int] = Field(
        default=300,
        description="Default timeout in seconds for test execution",
    )
    allowed_imports: List[str] = Field(
        default=[
            "math", "json", "datetime", "collections", "itertools",
            "functools", "operator", "string", "re", "textwrap",
            "typing", "dataclasses", "enum", "pathlib", "os",
        ],
        description="Modules allowed in sandboxed code execution",
    )
    max_output_chars: Optional[int] = Field(
        default=10000,
        description="Maximum characters to capture from test output",
    )
    dataset_sample_size: int = Field(
        default=100,
        description="Default number of dataset samples to load for tests",
    )


class ProjectSettings(BaseSettings):
    """
    Project-specific configuration with persistence support.
    
    Project configuration is persisted to projects/{project_id}/config.yaml
    """
    
    model_config = SettingsConfigDict(
        env_prefix="AGENTIC_PROJECT_",
        extra="ignore",
    )
    
    project_id: Optional[str] = Field(default=None, description="Project ID")
    git: Optional[GitConfig] = Field(default=None, description="Git configuration")
    auto_index: bool = Field(default=False, description="Enable automatic codebase indexing")
    indexing_version: str = Field(default="2.0", description="Indexing schema version used")
    data_sources: list[str] = Field(default_factory=list, description="List of DataSource IDs")
    services: dict[str, ServiceConfig] = Field(default_factory=dict, description="Associated services")
    environment_vars: dict[str, str] = Field(default_factory=dict, description="Project environment variables")
    
    @classmethod
    def load_for_project(cls, project_id: str, base_dir: Path = Path("./projects")) -> "ProjectSettings":
        """Load configuration for a specific project."""
        config_file = base_dir / project_id / "config.yaml"
        
        if config_file.exists():
            with open(config_file, "r") as f:
                data = yaml.safe_load(f) or {}
            
            # Parse nested configs
            if "git" in data and data["git"]:
                data["git"] = GitConfig(**data["git"])
            if "services" in data:
                data["services"] = {
                    k: ServiceConfig(**v) for k, v in data["services"].items()
                }
            
            return cls(project_id=project_id, **data)
        
        return cls(project_id=project_id)
    
    def save(self, base_dir: Path = Path("./projects")) -> None:
        """Persist project configuration to file."""
        if not self.project_id:
            return
        
        config_file = base_dir / self.project_id / "config.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "auto_index": self.auto_index,
            "indexing_version": self.indexing_version,
            "data_sources": self.data_sources,
            "environment_vars": self.environment_vars,
        }
        
        if self.git:
            data["git"] = {
                "remote_url": self.git.remote_url,
                "branch": self.git.branch,
                "auto_sync": self.git.auto_sync,
                "ssh_key_ref": self.git.ssh_key_ref,
            }
        
        if self.services:
            data["services"] = {
                k: {
                    "name": v.name,
                    "service_type": v.service_type,
                    "endpoint_url": v.endpoint_url,
                    "health_endpoint": v.health_endpoint,
                    "auth_type": v.auth_type,
                    "credentials_ref": v.credentials_ref,
                    "config_yaml": v.config_yaml,
                }
                for k, v in self.services.items()
            }
        
        with open(config_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def update(self, **kwargs) -> None:
        """Update project configuration and persist."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()


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
    framework_model: Optional[str] = Field(
        default=None,
        description="Model the framework uses for built-in assistant/docs help (falls back to Ollama default)",
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
    _llm: Optional[LLMSettings] = None
    _mlflow: Optional[MLFlowSettings] = None
    _telemetry: Optional[TelemetrySettings] = None
    _vectordb: Optional[VectorDBSettings] = None
    _embedding: Optional[EmbeddingSettings] = None
    _session: Optional[SessionSettings] = None
    _server: Optional[ServerSettings] = None
    _data_layer: Optional[DataLayerSettings] = None
    _indexing: Optional[IndexingSettings] = None
    _kubernetes: Optional[KubernetesSettings] = None
    _minio: Optional[MinIOSettings] = None
    _jupyter: Optional[JupyterSettings] = None
    _postgresql: Optional[PostgreSQLSettings] = None
    _redis: Optional[RedisSettings] = None
    _user: Optional[UserConfig] = None
    _session_config: Optional[SessionConfig] = None
    _global: Optional[GlobalConfig] = None
    _project: Optional[ProjectSettings] = None
    _assistant: Optional[FrameworkAssistantSettings] = None
    _testing: Optional[TestingSettings] = None
    _huggingface: Optional[HuggingFaceSettings] = None
    _nemotron: Optional[NemotronSettings] = None
    _datahub: Optional[DataHubSettings] = None
    _iceberg: Optional[IcebergSettings] = None
    _dbt: Optional[DbtSettings] = None

    @property
    def ollama(self) -> OllamaSettings:
        """Get Ollama configuration."""
        if self._ollama is None:
            self._ollama = OllamaSettings()
        return self._ollama

    @property
    def llm(self) -> LLMSettings:
        """Get generic LLM provider configuration."""
        if self._llm is None:
            self._llm = LLMSettings()
        return self._llm

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
    def embedding(self) -> EmbeddingSettings:
        """Get embedding configuration."""
        if self._embedding is None:
            self._embedding = EmbeddingSettings()
        return self._embedding

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
    def indexing(self) -> IndexingSettings:
        """Get indexing configuration."""
        if self._indexing is None:
            self._indexing = IndexingSettings()
        return self._indexing

    @property
    def testing(self) -> TestingSettings:
        """Get testing configuration."""
        if self._testing is None:
            self._testing = TestingSettings()
        return self._testing

    @property
    def huggingface(self) -> HuggingFaceSettings:
        """Get HuggingFace configuration."""
        if self._huggingface is None:
            self._huggingface = HuggingFaceSettings()
        return self._huggingface

    @property
    def nemotron(self) -> NemotronSettings:
        """Get Nemotron model configuration."""
        if self._nemotron is None:
            self._nemotron = NemotronSettings()
        return self._nemotron

    @property
    def datahub(self) -> DataHubSettings:
        """Get DataHub catalog configuration."""
        if self._datahub is None:
            self._datahub = DataHubSettings()
        return self._datahub

    @property
    def iceberg(self) -> IcebergSettings:
        """Get Iceberg catalog configuration."""
        if self._iceberg is None:
            self._iceberg = IcebergSettings()
        return self._iceberg

    @property
    def dbt(self) -> DbtSettings:
        """Get dbt transformation configuration."""
        if self._dbt is None:
            self._dbt = DbtSettings()
        return self._dbt

    @property
    def kubernetes(self) -> KubernetesSettings:
        """Get Kubernetes configuration."""
        if self._kubernetes is None:
            self._kubernetes = KubernetesSettings()
        return self._kubernetes

    @property
    def minio(self) -> MinIOSettings:
        """Get MinIO storage configuration."""
        if self._minio is None:
            self._minio = MinIOSettings()
        return self._minio

    @property
    def jupyter(self) -> JupyterSettings:
        """Get Jupyter notebook server configuration."""
        if self._jupyter is None:
            self._jupyter = JupyterSettings()
        return self._jupyter

    @property
    def postgresql(self) -> PostgreSQLSettings:
        """Get PostgreSQL database configuration."""
        if self._postgresql is None:
            self._postgresql = PostgreSQLSettings()
        return self._postgresql

    @property
    def supabase(self) -> SupabaseSettings:
        """Get Supabase configuration."""
        if self._supabase is None:
            self._supabase = SupabaseSettings()
        return self._supabase

    @property
    def database(self) -> DatabaseSettings:
        """Get database layer configuration."""
        if self._database is None:
            self._database = DatabaseSettings()
        return self._database

    @property
    def redis(self) -> RedisSettings:
        """Get Redis cache configuration."""
        if self._redis is None:
            self._redis = RedisSettings()
        return self._redis

    @property
    def project(self) -> ProjectSettings:
        """Get project configuration."""
        if self._project is None:
            self._project = ProjectSettings()
        return self._project

    @property
    def assistant(self) -> FrameworkAssistantSettings:
        """Get framework assistant configuration."""
        if self._assistant is None:
            self._assistant = FrameworkAssistantSettings()
        return self._assistant

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
    
    @classmethod
    def for_project(cls, project_id: str, user_id: Optional[str] = None, **kwargs) -> "AgenticConfig":
        """
        Create a configuration instance for a specific project.
        
        Args:
            project_id: The project identifier
            user_id: Optional user identifier
            **kwargs: Additional configuration overrides
        
        Returns:
            AgenticConfig instance with project-specific settings
        """
        config = cls(**kwargs)
        config._project = ProjectSettings.load_for_project(project_id, config.data_dir / "projects")
        
        if user_id:
            config._user = UserConfig.load_for_user(user_id, config.users_dir)
        
        return config
    
    def switch_project(self, project_id: str) -> None:
        """Switch to a different project's configuration."""
        self._project = ProjectSettings.load_for_project(project_id, self.data_dir / "projects")
    
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
        if self._project is not None and self._project.project_id:
            self._project.save(self.data_dir / "projects")
    
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
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "timeout": self.llm.timeout,
                "ollama_host": self.llm.ollama_host,
                "openai_base_url": self.llm.openai_base_url,
                "openai_api_key_env": self.llm.openai_api_key_env,
                "hf_execution_mode": self.llm.hf_execution_mode,
                "hf_local_model": self.llm.hf_local_model,
                "hf_device_map": self.llm.hf_device_map,
                "hf_torch_dtype": self.llm.hf_torch_dtype,
                "hf_trust_remote_code": self.llm.hf_trust_remote_code,
                "fallback_provider": self.llm.fallback_provider,
            },
            "framework_model": (
                self.framework_model
                or self.assistant.model
                or self.llm.model
                or self.ollama.default_model
            ),
            "telemetry": {
                "endpoint": self.telemetry.exporter_otlp_endpoint,
                "service_name": self.telemetry.service_name,
            },
            "vectordb": {
                "backend": self.vectordb.backend,
                "path": str(self.vectordb.path),
                "embedding_model": self.vectordb.embedding_model,
                "embedding_dimension": self.vectordb.embedding_dimension,
                "default_scope": self.vectordb.default_scope,
                "global_namespace": self.vectordb.global_namespace,
                "enable_cross_scope_search": self.vectordb.enable_cross_scope_search,
                "enable_scope_inheritance": self.vectordb.enable_scope_inheritance,
                "track_lineage": self.vectordb.track_lineage,
            },
            "embedding": {
                "mode": self.embedding.mode,
                "local_provider": self.embedding.local_provider,
                "local_model": self.embedding.local_model,
                "remote_provider": self.embedding.remote_provider,
                "remote_model": self.embedding.remote_model,
                "fallback_to_local": self.embedding.fallback_to_local,
                "batch_size": self.embedding.batch_size,
                "cache_embeddings": self.embedding.cache_embeddings,
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
            "indexing": {
                "version": self.indexing.version,
                "auto_index_new_projects": self.indexing.auto_index_new_projects,
                "chunk_size": self.indexing.chunk_size,
                "chunk_overlap": self.indexing.chunk_overlap,
                "max_file_size_mb": self.indexing.max_file_size_mb,
            },
            "kubernetes": {
                "enabled": self.kubernetes.enabled,
                "kubeconfig_path": self.kubernetes.kubeconfig_path,
                "context": self.kubernetes.context,
                "namespace": self.kubernetes.namespace,
                "cluster_endpoint": self.kubernetes.cluster_endpoint,
                "default_deploy_namespace": self.kubernetes.default_deploy_namespace,
                "enable_distributed": self.kubernetes.enable_distributed,
                "model_serving_namespace": self.kubernetes.model_serving_namespace,
            },
            "minio": {
                "enabled": self.minio.enabled,
                "endpoint": self.minio.endpoint,
                "external_endpoint": self.minio.external_endpoint,
                "secure": self.minio.secure,
                "default_bucket": self.minio.default_bucket,
                "model_bucket": self.minio.model_bucket,
            },
            "redis": {
                "enabled": self.redis.enabled,
                "url": self.redis.connection_url,
                "prefix": self.redis.prefix,
                "default_ttl": self.redis.default_ttl,
                "solution_cache_ttl": self.redis.solution_cache_ttl,
                "workflow_state_ttl": self.redis.workflow_state_ttl,
                "cache_embeddings": self.redis.cache_embeddings,
                "cache_solutions": self.redis.cache_solutions,
            },
            "project": {
                "project_id": self.project.project_id,
                "auto_index": self.project.auto_index,
                "indexing_version": self.project.indexing_version,
                "data_sources": self.project.data_sources,
            },
            "assistant": {
                "enabled": self.assistant.enabled,
                "default_framework": self.assistant.default_framework,
                "model": self.assistant.model,
                "provider": self.assistant.provider,
                "endpoint": self.assistant.endpoint,
                "openai_api_key_env": self.assistant.openai_api_key_env,
                "hf_execution_mode": self.assistant.hf_execution_mode,
                "enable_coding_helper": self.assistant.enable_coding_helper,
                "enable_framework_guide": self.assistant.enable_framework_guide,
                "enable_meta_analysis": self.assistant.enable_meta_analysis,
                "rag_enabled": self.assistant.rag_enabled,
                "memory_enabled": self.assistant.memory_enabled,
                "code_kb_project_id": self.assistant.code_kb_project_id,
                "docs_kb_name": self.assistant.docs_kb_name,
                "usage_tracking_enabled": self.assistant.usage_tracking_enabled,
                "usage_db_path": str(self.assistant.usage_db_path),
                "meta_analysis_interval_hours": self.assistant.meta_analysis_interval_hours,
                "max_context_messages": self.assistant.max_context_messages,
            },
            "testing": {
                "enabled": self.testing.enabled,
                "sandbox_default": self.testing.sandbox_default,
                "tracking_default": self.testing.tracking_default,
                "agent_eval_default": self.testing.agent_eval_default,
                "rl_metrics_default": self.testing.rl_metrics_default,
                "eval_provider": self.testing.eval_provider,
                "eval_model": self.testing.eval_model,
                "eval_endpoint": self.testing.eval_endpoint,
                "eval_hf_execution_mode": self.testing.eval_hf_execution_mode,
                "timeout_seconds": self.testing.timeout_seconds,
                "dataset_sample_size": self.testing.dataset_sample_size,
                "max_output_chars": self.testing.max_output_chars,
            },
            "huggingface": {
                "cache_dir": str(self.huggingface.cache_dir),
                "datasets_cache_dir": str(self.huggingface.datasets_cache_dir),
                "default_org": self.huggingface.default_org,
                "hub_url": self.huggingface.hub_url,
                "offline_mode": self.huggingface.offline_mode,
                "papers_enabled": self.huggingface.papers_enabled,
                "default_revision": self.huggingface.default_revision,
                "token_set": self.huggingface.token is not None,
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
        (self.data_dir / "projects").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "datasources").mkdir(parents=True, exist_ok=True)

