"""
Tests for configuration management.
"""

import os
import pytest
from unittest.mock import patch

from agentic_assistants.config import AgenticConfig, OllamaSettings, MLFlowSettings


class TestAgenticConfig:
    """Tests for the main configuration class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = AgenticConfig()
        
        assert config.mlflow_enabled is True
        assert config.telemetry_enabled is True
        assert config.log_level == "INFO"

    def test_programmatic_override(self):
        """Test programmatic configuration override."""
        config = AgenticConfig(
            mlflow_enabled=False,
            log_level="DEBUG",
        )
        
        assert config.mlflow_enabled is False
        assert config.log_level == "DEBUG"

    def test_nested_config_access(self):
        """Test accessing nested configuration objects."""
        config = AgenticConfig()
        
        # Ollama settings
        assert config.ollama.host == "http://localhost:11434"
        assert config.ollama.default_model == "llama3.2"
        
        # MLFlow settings
        assert config.mlflow.tracking_uri == "http://localhost:5000"
        
        # Telemetry settings
        assert config.telemetry.service_name == "agentic-assistants"

    def test_to_dict(self):
        """Test exporting configuration as dictionary."""
        config = AgenticConfig()
        config_dict = config.to_dict()
        
        assert "mlflow_enabled" in config_dict
        assert "ollama" in config_dict
        assert "host" in config_dict["ollama"]

    @patch.dict(os.environ, {"AGENTIC_MLFLOW_ENABLED": "false"})
    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        config = AgenticConfig()
        assert config.mlflow_enabled is False

    @patch.dict(os.environ, {"AGENTIC_LOG_LEVEL": "WARNING"})
    def test_log_level_from_env(self):
        """Test log level from environment."""
        config = AgenticConfig()
        assert config.log_level == "WARNING"


class TestOllamaSettings:
    """Tests for Ollama configuration."""

    def test_default_values(self):
        """Test Ollama default values."""
        settings = OllamaSettings()
        
        assert settings.host == "http://localhost:11434"
        assert settings.default_model == "llama3.2"
        assert settings.timeout == 120

    @patch.dict(os.environ, {"OLLAMA_HOST": "http://custom:11434"})
    def test_custom_host(self):
        """Test custom Ollama host from environment."""
        settings = OllamaSettings()
        assert settings.host == "http://custom:11434"


class TestMLFlowSettings:
    """Tests for MLFlow configuration."""

    def test_default_values(self):
        """Test MLFlow default values."""
        settings = MLFlowSettings()
        
        assert settings.tracking_uri == "http://localhost:5000"
        assert settings.experiment_name == "agentic-experiments"

    @patch.dict(os.environ, {"MLFLOW_EXPERIMENT_NAME": "custom-exp"})
    def test_custom_experiment(self):
        """Test custom experiment name from environment."""
        settings = MLFlowSettings()
        assert settings.experiment_name == "custom-exp"

