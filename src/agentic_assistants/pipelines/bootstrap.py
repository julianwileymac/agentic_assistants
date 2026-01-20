"""
Pipeline bootstrap utilities.

Registers built-in pipelines with the global pipeline registry.
"""

from __future__ import annotations

from typing import Optional

from agentic_assistants.pipelines.registry import get_pipeline_registry
from agentic_assistants.pipelines.templates import create_repo_ingestion_pipeline
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


def register_builtin_pipelines(
    config_path: Optional[str] = None,
    overwrite: bool = False,
) -> None:
    """Register built-in pipelines for the server and UI."""
    registry = get_pipeline_registry()

    def repo_ingestion_factory():
        return create_repo_ingestion_pipeline(config_path=config_path)

    if overwrite or not registry.has_pipeline("global_repo_ingestion"):
        registry.register("global_repo_ingestion", repo_ingestion_factory, overwrite=overwrite)
        logger.info("Registered pipeline: global_repo_ingestion")
