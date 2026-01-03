"""
Tests for CLI interface.
"""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch

from agentic_assistants.cli import cli


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestCLIBasics:
    """Tests for basic CLI functionality."""

    def test_cli_version(self, runner):
        """Test --version flag."""
        result = runner.invoke(cli, ["--version"])
        
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_help(self, runner):
        """Test --help flag."""
        result = runner.invoke(cli, ["--help"])
        
        assert result.exit_code == 0
        assert "Agentic Assistants" in result.output
        assert "ollama" in result.output
        assert "mlflow" in result.output


class TestOllamaCommands:
    """Tests for Ollama CLI commands."""

    def test_ollama_help(self, runner):
        """Test ollama --help."""
        result = runner.invoke(cli, ["ollama", "--help"])
        
        assert result.exit_code == 0
        assert "start" in result.output
        assert "stop" in result.output
        assert "status" in result.output
        assert "list" in result.output
        assert "pull" in result.output

    @patch("agentic_assistants.cli.OllamaManager")
    def test_ollama_status(self, mock_manager_class, runner):
        """Test ollama status command."""
        mock_manager = MagicMock()
        mock_manager.get_status.return_value = {
            "running": True,
            "host": "http://localhost:11434",
            "managed_process": False,
            "model_count": 2,
            "models": ["llama3.2", "mistral"],
        }
        mock_manager_class.return_value = mock_manager
        
        result = runner.invoke(cli, ["ollama", "status"])
        
        assert result.exit_code == 0
        assert "Running" in result.output

    @patch("agentic_assistants.cli.OllamaManager")
    def test_ollama_start_already_running(self, mock_manager_class, runner):
        """Test ollama start when already running."""
        mock_manager = MagicMock()
        mock_manager.is_running.return_value = True
        mock_manager_class.return_value = mock_manager
        
        result = runner.invoke(cli, ["ollama", "start"])
        
        assert result.exit_code == 0
        assert "already running" in result.output


class TestMLFlowCommands:
    """Tests for MLFlow CLI commands."""

    def test_mlflow_help(self, runner):
        """Test mlflow --help."""
        result = runner.invoke(cli, ["mlflow", "--help"])
        
        assert result.exit_code == 0
        assert "start" in result.output
        assert "ui" in result.output
        assert "status" in result.output


class TestConfigCommands:
    """Tests for config CLI commands."""

    def test_config_help(self, runner):
        """Test config --help."""
        result = runner.invoke(cli, ["config", "--help"])
        
        assert result.exit_code == 0
        assert "show" in result.output
        assert "init" in result.output

    def test_config_show(self, runner):
        """Test config show command."""
        result = runner.invoke(cli, ["config", "show"])
        
        assert result.exit_code == 0
        assert "MLFlow Enabled" in result.output
        assert "Ollama" in result.output

    def test_config_show_json(self, runner):
        """Test config show --json command."""
        result = runner.invoke(cli, ["config", "show", "--json"])
        
        assert result.exit_code == 0
        assert "{" in result.output
        assert "mlflow_enabled" in result.output


class TestServicesCommands:
    """Tests for services CLI commands."""

    def test_services_help(self, runner):
        """Test services --help."""
        result = runner.invoke(cli, ["services", "--help"])
        
        assert result.exit_code == 0
        assert "start" in result.output
        assert "status" in result.output

