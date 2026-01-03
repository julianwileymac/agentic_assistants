"""
Configuration management for Agentic Assistants.

This module provides a centralized configuration system using Pydantic Settings,
supporting environment variables, .env files, and programmatic configuration.

Example:
    >>> config = AgenticConfig()
    >>> print(config.ollama_host)
    'http://localhost:11434'
    
    >>> # Override settings programmatically
    >>> config = AgenticConfig(mlflow_enabled=False)
"""

from pathlib import Path
from typing import Optional

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


class AgenticConfig(BaseSettings):
    """
    Main configuration class for Agentic Assistants.
    
    This class aggregates all sub-configurations and provides
    top-level settings for the framework.
    
    Configuration sources (in order of precedence):
        1. Programmatic values passed to __init__
        2. Environment variables
        3. .env file
        4. Default values
    
    Example:
        >>> config = AgenticConfig()
        >>> config.ollama.host
        'http://localhost:11434'
        
        >>> config = AgenticConfig(mlflow_enabled=False)
        >>> config.mlflow_enabled
        False
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

    # Sub-configurations (populated in __init__)
    _ollama: Optional[OllamaSettings] = None
    _mlflow: Optional[MLFlowSettings] = None
    _telemetry: Optional[TelemetrySettings] = None

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
        }

