"""Tests for template catalog and scaffolding."""

from pathlib import Path

from agentic_assistants.templates import get_template, load_template_catalog, scaffold_template


def test_catalog_contains_maximal_template_set() -> None:
    templates = load_template_catalog()
    assert len(templates) >= 24
    assert any(t.template_id == "llm-document-augmentation" for t in templates)


def test_get_template_returns_expected_metadata() -> None:
    template = get_template("multilevel-storage-kb")
    assert template is not None
    assert template.category == "storage"
    assert "vectors" in template.description.lower() or "storage" in template.description.lower()


def test_scaffold_template_renders_default_scaffold(tmp_path: Path) -> None:
    output = scaffold_template(
        template_id="offline-agent-workspace",
        output_dir=tmp_path,
        project_name="offline-demo",
    )
    assert output.exists()
    assert (output / "README.md").exists()
    assert (output / "config.yaml").exists()
    assert (output / "app.py").exists()
    assert "offline-demo" in (output / "README.md").read_text(encoding="utf-8")


def test_scaffold_template_uses_asset_directory_when_available(tmp_path: Path) -> None:
    output = scaffold_template(
        template_id="quickstart-chat-agent",
        output_dir=tmp_path,
        project_name="chat-template",
    )
    readme = (output / "README.md").read_text(encoding="utf-8")
    assert "chat-template" in readme
    assert (output / "app.py").exists()

