"""
Manifest-driven template catalog loader and scaffolder.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class TemplateDefinition:
    """Single template entry loaded from catalog YAML."""

    template_id: str
    name: str
    category: str
    description: str
    level: str = "starter"
    tags: List[str] = field(default_factory=list)
    asset_dir: Optional[str] = None
    run_hint: Optional[str] = None


def _catalog_path() -> Path:
    return Path(__file__).with_name("catalog.yaml")


def _assets_root() -> Path:
    return Path(__file__).with_name("assets")


def load_template_catalog() -> List[TemplateDefinition]:
    """Load all templates from catalog.yaml."""
    path = _catalog_path()
    if not path.exists():
        return []

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    records = raw.get("templates", [])

    templates: List[TemplateDefinition] = []
    for record in records:
        templates.append(
            TemplateDefinition(
                template_id=record["id"],
                name=record.get("name", record["id"]),
                category=record.get("category", "general"),
                description=record.get("description", ""),
                level=record.get("level", "starter"),
                tags=record.get("tags", []),
                asset_dir=record.get("asset_dir"),
                run_hint=record.get("run_hint"),
            )
        )
    return templates


def list_templates(category: Optional[str] = None) -> List[TemplateDefinition]:
    """Return catalog templates, optionally filtered by category."""
    templates = load_template_catalog()
    if not category:
        return templates
    category_lower = category.strip().lower()
    return [t for t in templates if t.category.lower() == category_lower]


def get_template(template_id: str) -> Optional[TemplateDefinition]:
    """Fetch a template by ID."""
    template_id = template_id.strip().lower()
    for template in load_template_catalog():
        if template.template_id.lower() == template_id:
            return template
    return None


def _render_template_text(raw_text: str, context: Dict[str, Any]) -> str:
    """Render lightweight placeholders in template files."""
    rendered = raw_text

    for key, value in context.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        rendered = rendered.replace(f"${{{key}}}", str(value))

    # Last pass for Python-style format placeholders.
    # Unknown keys are left untouched.
    for key, value in context.items():
        rendered = rendered.replace(f"{{{key}}}", str(value))

    return rendered


def _is_text_file(path: Path) -> bool:
    text_exts = {
        ".md",
        ".txt",
        ".yaml",
        ".yml",
        ".json",
        ".jsonl",
        ".toml",
        ".ini",
        ".cfg",
        ".env",
        ".py",
        ".sh",
        ".ps1",
        ".sql",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".ipynb",
    }
    return path.suffix.lower() in text_exts


def _infer_entrypoint_filename(run_hint: Optional[str]) -> str:
    if not run_hint:
        return "app.py"
    hint = run_hint.strip()
    if hint.startswith("python "):
        parts = hint.split(maxsplit=1)
        if len(parts) == 2 and parts[1].strip():
            return parts[1].strip()
    return "app.py"


def _write_default_scaffold(
    destination: Path,
    template: TemplateDefinition,
    context: Dict[str, Any],
) -> None:
    """Create a minimal scaffold when no asset directory exists."""
    destination.mkdir(parents=True, exist_ok=True)

    readme = (
        f"# {template.name}\n\n"
        f"{template.description}\n\n"
        f"## Template Metadata\n\n"
        f"- ID: `{template.template_id}`\n"
        f"- Category: `{template.category}`\n"
        f"- Level: `{template.level}`\n"
        f"- Project Name: `{context['project_name']}`\n\n"
        "## Quick Start\n\n"
        "1. Review `config.yaml`.\n"
        "2. Run the entrypoint script.\n"
    )
    if template.run_hint:
        readme += f"3. Suggested command: `{template.run_hint}`\n"
    readme += "\n"
    (destination / "README.md").write_text(readme, encoding="utf-8")

    config_yaml = (
        "project:\n"
        f"  id: {template.template_id}\n"
        f"  name: {context['project_name']}\n"
        "storage:\n"
        "  artifacts_dir: ./data/artifacts\n"
        "  vectors_dir: ./data/vectors\n"
        "  usage_db: ./data/usage.db\n"
        "rag:\n"
        "  chunk_size: 1024\n"
        "  chunk_overlap: 128\n"
        "  augmenters: [metadata, keywords, summary]\n"
        "  llm_enabled: false\n"
        "vectordb:\n"
        "  backend: lancedb\n"
        "  embedding_model: nomic-embed-text\n"
    )
    (destination / "config.yaml").write_text(config_yaml, encoding="utf-8")

    entrypoint = _infer_entrypoint_filename(template.run_hint)
    entrypoint_path = destination / entrypoint
    entrypoint_path.parent.mkdir(parents=True, exist_ok=True)
    script = (
        '"""Generated starter entrypoint."""\n\n'
        "from pathlib import Path\n"
        "import yaml\n\n"
        "def main() -> None:\n"
        '    cfg = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8"))\n'
        f'    print("Template: {template.template_id}")\n'
        '    print(f"Project: {cfg.get(\'project\', {}).get(\'name\', \'unnamed\')}")\n'
        '    print("Edit README.md for next steps.")\n\n'
        'if __name__ == "__main__":\n'
        "    main()\n"
    )
    entrypoint_path.write_text(script, encoding="utf-8")


def scaffold_template(
    template_id: str,
    output_dir: Path,
    project_name: Optional[str] = None,
    force: bool = False,
    extra_context: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Materialize a template asset folder to an output directory.

    Returns the generated project path.
    """
    template = get_template(template_id)
    if template is None:
        raise ValueError(f"Unknown template: {template_id}")

    asset_dir = template.asset_dir or template.template_id
    source_root = _assets_root() / asset_dir

    destination = output_dir
    if project_name:
        destination = output_dir / project_name

    if destination.exists() and any(destination.iterdir()) and not force:
        raise FileExistsError(
            f"Output directory is not empty: {destination}. "
            "Use force=True to overwrite files."
        )

    destination.mkdir(parents=True, exist_ok=True)

    context: Dict[str, Any] = {
        "template_id": template.template_id,
        "template_name": template.name,
        "category": template.category,
        "project_name": project_name or destination.name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_hint": template.run_hint or "",
    }
    if extra_context:
        context.update(extra_context)

    if not source_root.exists():
        _write_default_scaffold(
            destination=destination,
            template=template,
            context=context,
        )
        return destination

    for src_path in source_root.rglob("*"):
        relative = src_path.relative_to(source_root)
        dest_path = destination / relative

        if src_path.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
            continue

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if _is_text_file(src_path):
            text = src_path.read_text(encoding="utf-8")
            dest_path.write_text(
                _render_template_text(text, context),
                encoding="utf-8",
            )
        else:
            shutil.copy2(src_path, dest_path)

    return destination

