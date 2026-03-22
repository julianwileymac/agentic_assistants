"""Tests for template-related CLI commands."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from agentic_assistants.cli import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_templates_list_json(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["templates", "list", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert isinstance(payload, list)
    assert any(item["id"] == "quickstart-chat-agent" for item in payload)


def test_templates_show_unknown_template_fails(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["templates", "show", "does-not-exist"])
    assert result.exit_code == 1
    assert "Unknown template" in result.output


def test_init_command_scaffolds_template(runner: CliRunner, tmp_path: Path) -> None:
    output_dir = tmp_path / "projects"
    result = runner.invoke(
        cli,
        [
            "init",
            "quickstart-chat-agent",
            "--output",
            str(output_dir),
            "--name",
            "demo-chat",
        ],
    )
    assert result.exit_code == 0
    project_dir = output_dir / "demo-chat"
    assert project_dir.exists()
    assert (project_dir / "README.md").exists()
    assert (project_dir / "app.py").exists()

