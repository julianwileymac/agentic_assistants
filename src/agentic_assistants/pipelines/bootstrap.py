"""
Pipeline bootstrap utilities.

Registers built-in pipelines with the global pipeline registry.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml

from agentic_assistants.pipelines.registry import get_pipeline_registry
from agentic_assistants.pipelines.templates import create_repo_ingestion_pipeline
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

DEFAULT_REPO_INGESTION_CONFIG = "examples/global-knowledgebase-starter/config.yaml"
DEFAULT_STARTER_MANIFEST = "examples/starters/starter_manifest.yaml"


def _register_repo_ingestion_pipeline(
    pipeline_name: str,
    pipeline_config_path: str,
    overwrite: bool,
) -> None:
    registry = get_pipeline_registry()

    def repo_ingestion_factory(config_path: str = pipeline_config_path):
        return create_repo_ingestion_pipeline(config_path=config_path)

    if overwrite or not registry.has_pipeline(pipeline_name):
        registry.register(pipeline_name, repo_ingestion_factory, overwrite=overwrite)
        logger.info(
            "Registered pipeline: %s (config: %s)",
            pipeline_name,
            pipeline_config_path,
        )


def _load_repo_ingestion_entries(starter_manifest: Optional[str]) -> list[dict]:
    manifest_path = Path(
        starter_manifest
        or os.environ.get("AGENTIC_STARTER_MANIFEST", DEFAULT_STARTER_MANIFEST)
    )
    if not manifest_path.exists():
        return []

    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    starters = raw.get("starters", [])
    return [
        entry
        for entry in starters
        if entry.get("pipeline_template") == "repo_ingestion" and entry.get("pipeline")
    ]


def register_builtin_pipelines(
    config_path: Optional[str] = None,
    overwrite: bool = False,
    starter_manifest: Optional[str] = None,
) -> None:
    """Register built-in pipelines for the server and UI."""
    default_config = str(Path(config_path or DEFAULT_REPO_INGESTION_CONFIG).resolve())
    _register_repo_ingestion_pipeline(
        pipeline_name="global_repo_ingestion",
        pipeline_config_path=default_config,
        overwrite=overwrite,
    )

    for entry in _load_repo_ingestion_entries(starter_manifest):
        pipeline_name = entry.get("pipeline")
        if not pipeline_name:
            continue
        entry_config = str(Path(entry.get("config_path", default_config)).resolve())
        _register_repo_ingestion_pipeline(
            pipeline_name=pipeline_name,
            pipeline_config_path=entry_config,
            overwrite=overwrite,
        )
