"""
Server bootstrap utilities for starter assets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Optional

import yaml

from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.server.api.components import BASE_COMPONENTS
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

STARTER_ID = "global-knowledgebase-starter"
STARTER_NAME = "Global Knowledgebase Starter"
DEFAULT_STARTER_MANIFEST = "examples/starters/starter_manifest.yaml"


@dataclass
class StarterSpec:
    starter_id: str
    name: str
    description: str
    config_path: str
    tags: list[str] = field(default_factory=lambda: ["starter"])
    flow_name: Optional[str] = None
    pipeline: Optional[str] = None
    pipeline_template: Optional[str] = None


def _legacy_starter(config_path: str) -> StarterSpec:
    resolved = str(Path(config_path).resolve())
    return StarterSpec(
        starter_id=STARTER_ID,
        name=STARTER_NAME,
        description="Seed project for global repo ingestion into the knowledge base.",
        config_path=resolved,
        tags=["starter", "knowledgebase", "global"],
        flow_name="Global Repo Ingestion",
        pipeline="global_repo_ingestion",
        pipeline_template="repo_ingestion",
    )


def _resolve_manifest_path(starter_manifest: Optional[str]) -> Path:
    return Path(
        starter_manifest
        or os.environ.get("AGENTIC_STARTER_MANIFEST", DEFAULT_STARTER_MANIFEST)
    )


def load_starter_specs(
    config_path: str,
    starter_manifest: Optional[str] = None,
) -> list[StarterSpec]:
    manifest_path = _resolve_manifest_path(starter_manifest)
    if not manifest_path.exists():
        logger.info("Starter manifest not found at %s, using legacy starter", manifest_path)
        return [_legacy_starter(config_path)]

    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    entries = raw.get("starters", [])
    if not entries:
        logger.warning("Starter manifest has no entries, using legacy starter")
        return [_legacy_starter(config_path)]

    starters: list[StarterSpec] = []
    for entry in entries:
        starter_id = entry.get("id")
        name = entry.get("name")
        if not starter_id or not name:
            logger.warning("Skipping invalid starter entry: %s", entry)
            continue

        resolved_config = str(Path(entry.get("config_path", config_path)).resolve())
        starters.append(
            StarterSpec(
                starter_id=starter_id,
                name=name,
                description=entry.get("description", f"Starter project for {name}."),
                config_path=resolved_config,
                tags=entry.get("tags", ["starter"]),
                flow_name=entry.get("flow_name"),
                pipeline=entry.get("pipeline"),
                pipeline_template=entry.get("pipeline_template"),
            )
        )

    return starters or [_legacy_starter(config_path)]


def seed_starter_project(starter: StarterSpec) -> Optional[str]:
    """Ensure a starter project exists in the control panel store."""
    store = ControlPanelStore.get_instance()
    projects, _ = store.list_projects()
    for project in projects:
        if project.metadata.get("starter_id") == starter.starter_id or project.name == starter.name:
            return project.id

    config_lines = [
        f"starter_id: {starter.starter_id}",
        f"starter_config_path: {starter.config_path}",
    ]
    if starter.pipeline_template == "repo_ingestion":
        config_lines.append(f"repo_ingestion_config: {starter.config_path}")

    project = store.create_project(
        name=starter.name,
        description=starter.description,
        config_yaml="\n".join(config_lines),
        status="active",
        tags=starter.tags,
        metadata={
            "starter_id": starter.starter_id,
            "config_path": starter.config_path,
            "pipeline": starter.pipeline,
            "pipeline_template": starter.pipeline_template,
        },
    )
    logger.info("Seeded starter project: %s (%s)", starter.starter_id, project.id)
    return project.id


def seed_starter_flow(project_id: Optional[str], starter: StarterSpec) -> None:
    """Ensure starter flow exists in the control panel store."""
    if not project_id or not starter.pipeline or not starter.flow_name:
        return

    store = ControlPanelStore.get_instance()
    flows, _ = store.list_flows(project_id=project_id)
    for flow in flows:
        if flow.metadata.get("starter_id") == starter.starter_id or flow.name == starter.flow_name:
            return

    flow_yaml = (
        f"name: {starter.pipeline}\n"
        "type: pipeline\n"
        f"pipeline: {starter.pipeline}\n"
        f"config_path: {starter.config_path}\n"
        f"description: {starter.description}\n"
    )
    store.create_flow(
        name=starter.flow_name,
        description=starter.description,
        flow_yaml=flow_yaml,
        flow_type="pipeline",
        status="published",
        project_id=project_id,
        tags=starter.tags,
        metadata={
            "starter_id": starter.starter_id,
            "pipeline": starter.pipeline,
        },
    )
    logger.info("Seeded starter flow for project %s (%s)", project_id, starter.starter_id)


def seed_base_components() -> None:
    """Install base components into the Control Panel store."""
    store = ControlPanelStore.get_instance()
    installed = 0
    for component_data in BASE_COMPONENTS:
        existing, _ = store.list_components(search=component_data["name"])
        if any(c.name == component_data["name"] for c in existing):
            continue
        store.create_component(**component_data)
        installed += 1
    if installed:
        logger.info("Installed %d base components", installed)


def seed_starter_assets(
    config_path: str,
    starter_manifest: Optional[str] = None,
) -> Optional[str]:
    """Seed starter projects, flows, and base components."""
    seed_base_components()
    starters = load_starter_specs(config_path, starter_manifest=starter_manifest)

    primary_project_id: Optional[str] = None
    for starter in starters:
        project_id = seed_starter_project(starter)
        if primary_project_id is None:
            primary_project_id = project_id
        seed_starter_flow(project_id, starter)

    return primary_project_id
