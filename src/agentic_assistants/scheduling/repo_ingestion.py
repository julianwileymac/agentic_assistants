"""
Scheduling helpers for repository ingestion.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from agentic_assistants.pipelines.templates.repo_ingestion import (
    load_repo_ingestion_config,
    load_repo_manifest,
    prepare_repo_queue,
)
from agentic_assistants.scheduling.jobs import RepoIngestionJob
from agentic_assistants.scheduling.scheduler import Scheduler, get_scheduler
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

CRON_ALIASES = {
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
}


def parse_cron_expression(expr: str) -> Dict[str, str]:
    """Parse a 5-field cron expression into APScheduler args."""
    expr = CRON_ALIASES.get(expr.strip(), expr.strip())
    fields = expr.split()
    if len(fields) != 5:
        raise ValueError(f"Invalid cron expression: {expr}")
    minute, hour, day, month, day_of_week = fields
    return {
        "minute": minute,
        "hour": hour,
        "day": day,
        "month": month,
        "day_of_week": day_of_week,
    }


def register_repo_ingestion_jobs(
    config_path: str,
    scheduler: Optional[Scheduler] = None,
    respect_manual_override: bool = True,
) -> List[str]:
    """
    Register scheduled ingestion jobs for each repo in the manifest.

    Returns a list of scheduled job IDs.
    """
    scheduler = scheduler or get_scheduler()
    config = load_repo_ingestion_config(config_path)
    manifest = load_repo_manifest(config)
    repo_queue = prepare_repo_queue(config, manifest)

    job_ids = []
    for repo in repo_queue:
        if not repo.get("enabled", True):
            continue
        if respect_manual_override and repo.get("manual_override"):
            logger.info("Skipping scheduling for %s due to manual override", repo["name"])
            continue

        cron_expr = repo.get("schedule")
        if not cron_expr:
            continue

        trigger_args = parse_cron_expression(cron_expr)
        trigger_args["timezone"] = config.get("scheduling_timezone", "UTC")

        job = RepoIngestionJob(
            config_path=config_path,
            repo_name=repo["name"],
            respect_manual_override=respect_manual_override,
        )
        job_id = f"repo_ingestion_{repo['name']}"
        scheduler.add_job(
            job,
            trigger="cron",
            id=job_id,
            name=job.name,
            replace_existing=True,
            **trigger_args,
        )
        job_ids.append(job_id)

    if job_ids:
        logger.info("Registered %d repo ingestion schedules", len(job_ids))

    return job_ids
