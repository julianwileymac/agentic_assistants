"""
Job Scheduling System for Data Operations.

This module provides a scheduling system for automating data operations
like RSS monitoring, website scraping, and feature materialization.

Example:
    >>> from agentic_assistants.scheduling import Scheduler, RSSMonitorJob
    >>> 
    >>> scheduler = Scheduler()
    >>> 
    >>> # Add an RSS monitoring job
    >>> scheduler.add_job(
    ...     RSSMonitorJob(
    ...         feed_url="https://example.com/feed",
    ...         collection="news"
    ...     ),
    ...     trigger="interval",
    ...     minutes=30
    ... )
    >>> 
    >>> scheduler.start()
"""

from agentic_assistants.scheduling.scheduler import Scheduler, get_scheduler
from agentic_assistants.scheduling.jobs import (
    Job,
    RSSMonitorJob,
    WebsiteMonitorJob,
    DataSyncJob,
    FeatureMaterializationJob,
    RepoIngestionJob,
)
from agentic_assistants.scheduling.triggers import (
    IntervalTrigger,
    CronTrigger,
    DateTrigger,
)
from agentic_assistants.scheduling.repo_ingestion import (
    register_repo_ingestion_jobs,
    parse_cron_expression,
)

__all__ = [
    # Core
    "Scheduler",
    "get_scheduler",
    # Jobs
    "Job",
    "RSSMonitorJob",
    "WebsiteMonitorJob",
    "DataSyncJob",
    "FeatureMaterializationJob",
    "RepoIngestionJob",
    # Triggers
    "IntervalTrigger",
    "CronTrigger",
    "DateTrigger",
    "register_repo_ingestion_jobs",
    "parse_cron_expression",
]
