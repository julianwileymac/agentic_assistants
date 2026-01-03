"""
Tests for Ollama manager.
"""

import pytest
from unittest.mock import MagicMock, patch

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.ollama import (
    OllamaManager,
    OllamaError,
    OllamaNotFoundError,
    OllamaConnectionError,
    ModelInfo,
)


class TestModelInfo:
    """Tests for ModelInfo dataclass."""

    def test_size_gb_calculation(self):
        """Test size_gb property calculation."""
        model = ModelInfo(
            name="llama3.2:latest",
            size=4 * 1024 * 1024 * 1024,  # 4 GB in bytes
            modified_at="2024-01-15T10:00:00Z",
            digest="abc123",
        )
        
        assert model.size_gb == 4.0


class TestOllamaManager:
    """Tests for OllamaManager class."""

    def test_init_with_config(self, config):
        """Test initialization with config."""
        manager = OllamaManager(config)
        
        assert manager.config == config
        assert manager.host == config.ollama.host
        assert manager.timeout == config.ollama.timeout

    def test_init_without_config(self):
        """Test initialization without config uses defaults."""
        manager = OllamaManager()
        
        assert manager.config is not None
        assert manager.host == "http://localhost:11434"

    def test_is_running_when_running(self, config, mock_httpx_client):
        """Test is_running returns True when server responds."""
        manager = OllamaManager(config)
        manager._client = mock_httpx_client
        
        assert manager.is_running() is True

    def test_is_running_when_not_running(self, config):
        """Test is_running returns False when server doesn't respond."""
        with patch("agentic_assistants.core.ollama.httpx.Client") as mock_class:
            mock_client = MagicMock()
            mock_class.return_value = mock_client
            
            import httpx
            mock_client.get.side_effect = httpx.RequestError("Connection refused")
            
            manager = OllamaManager(config)
            manager._client = mock_client
            
            assert manager.is_running() is False

    def test_list_models(self, config, mock_httpx_client, mock_ollama_models):
        """Test listing models."""
        manager = OllamaManager(config)
        manager._client = mock_httpx_client
        
        models = manager.list_models()
        
        assert len(models) == 2
        assert models[0].name == "llama3.2:latest"
        assert models[1].name == "mistral:latest"

    def test_model_exists_true(self, config, mock_httpx_client):
        """Test model_exists returns True for existing model."""
        manager = OllamaManager(config)
        manager._client = mock_httpx_client
        
        assert manager.model_exists("llama3.2") is True

    def test_model_exists_false(self, config, mock_httpx_client):
        """Test model_exists returns False for non-existing model."""
        manager = OllamaManager(config)
        manager._client = mock_httpx_client
        
        assert manager.model_exists("nonexistent") is False

    def test_chat(self, config, mock_httpx_client, mock_ollama_response):
        """Test chat method."""
        manager = OllamaManager(config)
        manager._client = mock_httpx_client
        
        messages = [{"role": "user", "content": "Hello!"}]
        response = manager.chat(messages)
        
        assert response["message"]["content"] == "This is a test response from the mock."

    def test_get_status_when_running(self, config, mock_httpx_client):
        """Test get_status when server is running."""
        manager = OllamaManager(config)
        manager._client = mock_httpx_client
        
        status = manager.get_status()
        
        assert status["running"] is True
        assert status["host"] == config.ollama.host
        assert status["model_count"] == 2

    def test_context_manager(self, config, mock_httpx_client):
        """Test using OllamaManager as context manager."""
        with patch.object(OllamaManager, "ensure_running"):
            with OllamaManager(config) as manager:
                manager._client = mock_httpx_client
                assert manager.is_running() is True


class TestOllamaExceptions:
    """Tests for Ollama exceptions."""

    def test_ollama_error_inheritance(self):
        """Test exception inheritance."""
        assert issubclass(OllamaNotFoundError, OllamaError)
        assert issubclass(OllamaConnectionError, OllamaError)

    def test_ollama_not_found_error(self):
        """Test OllamaNotFoundError message."""
        with pytest.raises(OllamaNotFoundError) as exc_info:
            raise OllamaNotFoundError("Ollama not found")
        
        assert "Ollama not found" in str(exc_info.value)

