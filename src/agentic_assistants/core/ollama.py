"""
Ollama server and model management.

This module provides functionality to:
- Start/stop the Ollama server process
- Pull, list, and delete models
- Health checks and status monitoring

Example:
    >>> from agentic_assistants import AgenticConfig, OllamaManager
    >>> 
    >>> config = AgenticConfig()
    >>> ollama = OllamaManager(config)
    >>> 
    >>> # Ensure Ollama is running
    >>> ollama.ensure_running()
    >>> 
    >>> # Pull a model
    >>> ollama.pull_model("llama3.2")
    >>> 
    >>> # List available models
    >>> models = ollama.list_models()
"""

import platform
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

import httpx

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ModelInfo:
    """Information about an Ollama model."""

    name: str
    size: int
    modified_at: str
    digest: str

    @property
    def size_gb(self) -> float:
        """Get model size in gigabytes."""
        return self.size / (1024**3)


class OllamaError(Exception):
    """Base exception for Ollama-related errors."""

    pass


class OllamaNotFoundError(OllamaError):
    """Raised when Ollama executable is not found."""

    pass


class OllamaConnectionError(OllamaError):
    """Raised when unable to connect to Ollama server."""

    pass


class OllamaManager:
    """
    Manage Ollama server and models.
    
    This class provides a high-level interface for interacting with Ollama,
    including server lifecycle management and model operations.
    
    Attributes:
        config: Agentic configuration instance
        host: Ollama server URL
        timeout: Request timeout in seconds
    """

    def __init__(self, config: Optional[AgenticConfig] = None):
        """
        Initialize the Ollama manager.
        
        Args:
            config: Configuration instance. If None, uses default config.
        """
        self.config = config or AgenticConfig()
        self.host = self.config.ollama.host
        self.timeout = self.config.ollama.timeout
        self._client = httpx.Client(timeout=self.timeout)
        self._process: Optional[subprocess.Popen] = None

    def _get_ollama_path(self) -> str:
        """Get the path to the Ollama executable."""
        ollama_path = shutil.which("ollama")
        if ollama_path:
            return ollama_path

        # Check common installation locations
        system = platform.system()
        if system == "Windows":
            common_paths = [
                r"C:\Program Files\Ollama\ollama.exe",
                r"C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe",
            ]
        elif system == "Darwin":
            common_paths = [
                "/usr/local/bin/ollama",
                "/opt/homebrew/bin/ollama",
            ]
        else:  # Linux
            common_paths = [
                "/usr/local/bin/ollama",
                "/usr/bin/ollama",
            ]

        for path in common_paths:
            expanded_path = path.replace("%USERNAME%", "")
            if shutil.which(expanded_path):
                return expanded_path

        raise OllamaNotFoundError(
            "Ollama executable not found. Please install Ollama from https://ollama.ai"
        )

    def is_running(self) -> bool:
        """
        Check if Ollama server is running and responding.
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            response = self._client.get(f"{self.host}/api/tags")
            return response.status_code == 200
        except httpx.RequestError:
            return False

    def start(self, wait: bool = True, timeout: int = 30) -> bool:
        """
        Start the Ollama server.
        
        Args:
            wait: Wait for server to be ready
            timeout: Maximum seconds to wait for server
        
        Returns:
            True if server started successfully
        
        Raises:
            OllamaNotFoundError: If Ollama is not installed
            OllamaError: If server fails to start
        """
        if self.is_running():
            logger.info("Ollama server is already running")
            return True

        ollama_path = self._get_ollama_path()
        logger.info(f"Starting Ollama server from {ollama_path}")

        try:
            # Start Ollama serve in background
            if platform.system() == "Windows":
                # On Windows, use CREATE_NEW_PROCESS_GROUP to detach
                self._process = subprocess.Popen(
                    [ollama_path, "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                )
            else:
                self._process = subprocess.Popen(
                    [ollama_path, "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )

            if wait:
                return self._wait_for_ready(timeout)

            return True

        except Exception as e:
            raise OllamaError(f"Failed to start Ollama server: {e}") from e

    def _wait_for_ready(self, timeout: int) -> bool:
        """Wait for Ollama server to become ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_running():
                logger.info("Ollama server is ready")
                return True
            time.sleep(0.5)

        raise OllamaError(f"Ollama server did not start within {timeout} seconds")

    def stop(self) -> bool:
        """
        Stop the Ollama server.
        
        Returns:
            True if server was stopped or wasn't running
        """
        if self._process:
            logger.info("Stopping Ollama server")
            self._process.terminate()
            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None
            return True

        # Try to stop via process name if we didn't start it
        logger.warning("No managed Ollama process to stop")
        return False

    def ensure_running(self) -> None:
        """
        Ensure Ollama server is running, starting it if necessary.
        
        Raises:
            OllamaError: If unable to start or connect to Ollama
        """
        if not self.is_running():
            self.start()

    def get_status(self) -> dict:
        """
        Get detailed status of the Ollama server.
        
        Returns:
            Dictionary with status information
        """
        running = self.is_running()
        status = {
            "running": running,
            "host": self.host,
            "managed_process": self._process is not None,
        }

        if running:
            try:
                models = self.list_models()
                status["model_count"] = len(models)
                status["models"] = [m.name for m in models]
            except Exception:
                status["model_count"] = 0
                status["models"] = []

        return status

    def list_models(self) -> list[ModelInfo]:
        """
        List all available models.
        
        Returns:
            List of ModelInfo objects
        
        Raises:
            OllamaConnectionError: If unable to connect to Ollama
        """
        try:
            response = self._client.get(f"{self.host}/api/tags")
            response.raise_for_status()
            data = response.json()

            return [
                ModelInfo(
                    name=model["name"],
                    size=model.get("size", 0),
                    modified_at=model.get("modified_at", ""),
                    digest=model.get("digest", ""),
                )
                for model in data.get("models", [])
            ]
        except httpx.RequestError as e:
            raise OllamaConnectionError(f"Failed to connect to Ollama: {e}") from e

    def pull_model(
        self,
        model_name: str,
        stream: bool = True,
        callback: Optional[callable] = None,
    ) -> bool:
        """
        Pull a model from the Ollama registry.
        
        Args:
            model_name: Name of the model to pull (e.g., "llama3.2", "mistral")
            stream: Stream progress updates
            callback: Optional callback for progress updates
        
        Returns:
            True if model was pulled successfully
        """
        logger.info(f"Pulling model: {model_name}")

        try:
            with self._client.stream(
                "POST",
                f"{self.host}/api/pull",
                json={"name": model_name, "stream": stream},
                timeout=None,  # Model pulls can take a long time
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if line and callback:
                        import json

                        try:
                            data = json.loads(line)
                            callback(data)
                        except json.JSONDecodeError:
                            pass

            logger.info(f"Successfully pulled model: {model_name}")
            return True

        except httpx.RequestError as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            raise OllamaConnectionError(f"Failed to pull model: {e}") from e

    def delete_model(self, model_name: str) -> bool:
        """
        Delete a model from local storage.
        
        Args:
            model_name: Name of the model to delete
        
        Returns:
            True if model was deleted successfully
        """
        logger.info(f"Deleting model: {model_name}")

        try:
            response = self._client.delete(
                f"{self.host}/api/delete",
                json={"name": model_name},
            )
            response.raise_for_status()
            logger.info(f"Successfully deleted model: {model_name}")
            return True

        except httpx.RequestError as e:
            logger.error(f"Failed to delete model {model_name}: {e}")
            return False

    def model_exists(self, model_name: str) -> bool:
        """
        Check if a model exists locally.
        
        Args:
            model_name: Name of the model to check
        
        Returns:
            True if model exists
        """
        models = self.list_models()
        return any(m.name == model_name or m.name.startswith(f"{model_name}:") for m in models)

    def ensure_model(self, model_name: Optional[str] = None) -> str:
        """
        Ensure a model is available, pulling it if necessary.
        
        Args:
            model_name: Model name. If None, uses default from config.
        
        Returns:
            The model name that is available
        """
        model = model_name or self.config.ollama.default_model

        if not self.model_exists(model):
            logger.info(f"Model {model} not found, pulling...")
            self.pull_model(model)

        return model

    def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """
        Send a chat completion request to Ollama.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name. If None, uses default from config.
            **kwargs: Additional parameters to pass to Ollama
        
        Returns:
            Response dictionary from Ollama
        """
        model = model or self.config.ollama.default_model

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **kwargs,
        }

        response = self._client.post(
            f"{self.host}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def __enter__(self):
        """Context manager entry - ensures Ollama is running."""
        self.ensure_running()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - optionally stops Ollama."""
        # Don't stop automatically as other processes might be using it
        self._client.close()
        return False

