"""
Pytest fixtures for Agentic Assistants tests.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from agentic_assistants.config import AgenticConfig


@pytest.fixture
def config():
    """Create a test configuration with tracking disabled."""
    return AgenticConfig(
        mlflow_enabled=False,
        telemetry_enabled=False,
        log_level="DEBUG",
    )


@pytest.fixture
def mock_ollama_response():
    """Mock response from Ollama API."""
    return {
        "model": "llama3.2",
        "message": {
            "role": "assistant",
            "content": "This is a test response from the mock.",
        },
        "done": True,
    }


@pytest.fixture
def mock_ollama_models():
    """Mock model list from Ollama API."""
    return {
        "models": [
            {
                "name": "llama3.2:latest",
                "size": 4000000000,
                "modified_at": "2024-01-15T10:00:00Z",
                "digest": "abc123",
            },
            {
                "name": "mistral:latest",
                "size": 3500000000,
                "modified_at": "2024-01-14T10:00:00Z",
                "digest": "def456",
            },
        ]
    }


@pytest.fixture
def mock_httpx_client(mock_ollama_response, mock_ollama_models):
    """Mock httpx client for Ollama tests."""
    with patch("agentic_assistants.core.ollama.httpx.Client") as mock_class:
        mock_client = MagicMock()
        mock_class.return_value = mock_client
        
        # Mock different endpoints
        def mock_get(url, **kwargs):
            response = MagicMock()
            if "/api/tags" in url:
                response.status_code = 200
                response.json.return_value = mock_ollama_models
            else:
                response.status_code = 200
            return response
        
        def mock_post(url, **kwargs):
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = mock_ollama_response
            return response
        
        mock_client.get.side_effect = mock_get
        mock_client.post.side_effect = mock_post
        
        yield mock_client


@pytest.fixture
def temp_env(tmp_path):
    """Create a temporary environment with .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text("""
OLLAMA_HOST=http://test:11434
OLLAMA_DEFAULT_MODEL=test-model
AGENTIC_MLFLOW_ENABLED=false
    """)
    
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    
    yield tmp_path
    
    os.chdir(original_dir)

