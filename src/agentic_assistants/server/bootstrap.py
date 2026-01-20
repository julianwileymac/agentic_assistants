"""
Server bootstrap utilities for starter assets.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.server.api.components import BASE_COMPONENTS
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

STARTER_ID = "global-knowledgebase-starter"
STARTER_NAME = "Global Knowledgebase Starter"


def seed_starter_project(config_path: str) -> Optional[str]:
    """Ensure the starter project exists in the control panel store."""
    store = ControlPanelStore.get_instance()
    projects, _ = store.list_projects()
    for project in projects:
        if project.name == STARTER_NAME or project.metadata.get("starter_id") == STARTER_ID:
            return project.id

    config_path = str(Path(config_path).resolve())
    project = store.create_project(
        name=STARTER_NAME,
        description="Seed project for global repo ingestion into the knowledge base.",
        config_yaml=f"repo_ingestion_config: {config_path}",
        status="active",
        tags=["starter", "knowledgebase", "global"],
        metadata={
            "starter_id": STARTER_ID,
            "config_path": config_path,
        },
    )
    logger.info("Seeded starter project: %s", project.id)
    return project.id


def seed_starter_flow(project_id: Optional[str], config_path: str) -> None:
    """Ensure starter flow exists in the control panel store."""
    store = ControlPanelStore.get_instance()
    flows, _ = store.list_flows(project_id=project_id)
    for flow in flows:
        if flow.name == "Global Repo Ingestion":
            return

    flow_yaml = f"""name: global_repo_ingestion
type: pipeline
pipeline: global_repo_ingestion
config_path: {config_path}
description: Run the repo ingestion pipeline for the global knowledgebase.
"""
    store.create_flow(
        name="Global Repo Ingestion",
        description="Pipeline flow for ingesting tracked Git repositories.",
        flow_yaml=flow_yaml,
        flow_type="pipeline",
        status="published",
        project_id=project_id,
        tags=["starter", "ingestion", "knowledgebase"],
        metadata={"starter_id": STARTER_ID},
    )
    logger.info("Seeded starter flow for project %s", project_id)


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


def seed_starter_assets(config_path: str) -> Optional[str]:
    """Seed starter project, flow, and base components."""
    seed_base_components()
    project_id = seed_starter_project(config_path)
    seed_starter_flow(project_id, config_path)
    return project_id
