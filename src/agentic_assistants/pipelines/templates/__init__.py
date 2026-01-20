"""
Pipeline templates for data ingestion workflows.

This module provides pre-built pipeline templates for common data
ingestion scenarios.

Example:
    >>> from agentic_assistants.pipelines.templates import create_web_ingestion_pipeline
    >>> 
    >>> pipeline = create_web_ingestion_pipeline(
    ...     urls=["https://example.com/article"],
    ...     collection="articles"
    ... )
    >>> result = pipeline.run()
"""

from agentic_assistants.pipelines.templates.web_ingestion import (
    create_web_ingestion_pipeline,
    WebIngestionConfig,
)
from agentic_assistants.pipelines.templates.document_ingestion import (
    create_document_ingestion_pipeline,
    DocumentIngestionConfig,
)
from agentic_assistants.pipelines.templates.dataset_ingestion import (
    create_dataset_ingestion_pipeline,
    DatasetIngestionConfig,
)
from agentic_assistants.pipelines.templates.rss_monitoring import (
    create_rss_monitoring_pipeline,
    RSSMonitoringConfig,
)
from agentic_assistants.pipelines.templates.repo_ingestion import (
    create_repo_ingestion_pipeline,
    RepoIngestionConfig,
)

__all__ = [
    # Web ingestion
    "create_web_ingestion_pipeline",
    "WebIngestionConfig",
    # Document ingestion
    "create_document_ingestion_pipeline",
    "DocumentIngestionConfig",
    # Dataset ingestion
    "create_dataset_ingestion_pipeline",
    "DatasetIngestionConfig",
    # RSS monitoring
    "create_rss_monitoring_pipeline",
    "RSSMonitoringConfig",
    # Repo ingestion
    "create_repo_ingestion_pipeline",
    "RepoIngestionConfig",
]
