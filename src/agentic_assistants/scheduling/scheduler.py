"""
Job Scheduler implementation using APScheduler.
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class Scheduler:
    """
    Job scheduler for automating data operations.
    
    Uses APScheduler for job scheduling with support for:
    - Interval-based scheduling
    - Cron-based scheduling
    - One-time scheduled execution
    
    Example:
        >>> scheduler = Scheduler()
        >>> scheduler.add_job(
        ...     my_function,
        ...     trigger="interval",
        ...     hours=1,
        ...     id="hourly_job"
        ... )
        >>> scheduler.start()
    """
    
    def __init__(self, timezone: str = "UTC"):
        """
        Initialize the scheduler.
        
        Args:
            timezone: Timezone for scheduling
        """
        self.timezone = timezone
        self._scheduler = None
        self._jobs: Dict[str, Any] = {}
        self._started = False
    
    @property
    def scheduler(self):
        """Get or create APScheduler instance."""
        if self._scheduler is None:
            try:
                from apscheduler.schedulers.background import BackgroundScheduler
                from apscheduler.jobstores.memory import MemoryJobStore
                from apscheduler.executors.pool import ThreadPoolExecutor
                
                jobstores = {
                    "default": MemoryJobStore()
                }
                
                executors = {
                    "default": ThreadPoolExecutor(max_workers=10)
                }
                
                job_defaults = {
                    "coalesce": True,
                    "max_instances": 3,
                    "misfire_grace_time": 60,
                }
                
                self._scheduler = BackgroundScheduler(
                    jobstores=jobstores,
                    executors=executors,
                    job_defaults=job_defaults,
                    timezone=self.timezone,
                )
                
            except ImportError:
                raise ImportError(
                    "apscheduler is required. Install with: pip install apscheduler"
                )
        
        return self._scheduler
    
    def add_job(
        self,
        func: Union[Callable, "Job"],
        trigger: str = "interval",
        id: Optional[str] = None,
        name: Optional[str] = None,
        replace_existing: bool = True,
        **trigger_args,
    ) -> str:
        """
        Add a job to the scheduler.
        
        Args:
            func: Function or Job instance to execute
            trigger: Trigger type (interval, cron, date)
            id: Job ID (auto-generated if None)
            name: Job name
            replace_existing: Replace job if ID exists
            **trigger_args: Trigger-specific arguments
            
        Returns:
            Job ID
        """
        from agentic_assistants.scheduling.jobs import Job
        
        # Handle Job instances
        if isinstance(func, Job):
            job_instance = func
            actual_func = job_instance.run
            job_id = id or job_instance.job_id
            job_name = name or job_instance.name
        else:
            actual_func = func
            job_id = id or f"job_{len(self._jobs)}"
            job_name = name or func.__name__
        
        # Build trigger
        trigger_obj = self._create_trigger(trigger, trigger_args)
        
        # Add to APScheduler
        job = self.scheduler.add_job(
            actual_func,
            trigger=trigger_obj,
            id=job_id,
            name=job_name,
            replace_existing=replace_existing,
        )
        
        self._jobs[job_id] = {
            "id": job_id,
            "name": job_name,
            "trigger": trigger,
            "trigger_args": trigger_args,
            "added_at": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Added job: {job_id} ({trigger})")
        return job_id
    
    def _create_trigger(self, trigger_type: str, args: Dict[str, Any]):
        """Create an APScheduler trigger."""
        from apscheduler.triggers.interval import IntervalTrigger
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.triggers.date import DateTrigger
        
        if trigger_type == "interval":
            return IntervalTrigger(**args)
        elif trigger_type == "cron":
            return CronTrigger(**args)
        elif trigger_type == "date":
            return DateTrigger(**args)
        else:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a job from the scheduler."""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self._jobs:
                del self._jobs[job_id]
            logger.info(f"Removed job: {job_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to remove job {job_id}: {e}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """Pause a job."""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused job: {job_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to pause job {job_id}: {e}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job."""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed job: {job_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to resume job {job_id}: {e}")
            return False
    
    def run_job(self, job_id: str) -> bool:
        """Run a job immediately."""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.func()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to run job {job_id}: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job information."""
        if job_id in self._jobs:
            job = self.scheduler.get_job(job_id)
            info = self._jobs[job_id].copy()
            if job:
                info["next_run"] = job.next_run_time.isoformat() if job.next_run_time else None
            return info
        return None
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all scheduled jobs."""
        jobs = []
        for job_id, info in self._jobs.items():
            job = self.scheduler.get_job(job_id)
            job_info = info.copy()
            if job:
                job_info["next_run"] = job.next_run_time.isoformat() if job.next_run_time else None
                job_info["pending"] = job.pending
            jobs.append(job_info)
        return jobs
    
    def start(self) -> None:
        """Start the scheduler."""
        if not self._started:
            self.scheduler.start()
            self._started = True
            logger.info("Scheduler started")
    
    def stop(self, wait: bool = True) -> None:
        """Stop the scheduler."""
        if self._started:
            self.scheduler.shutdown(wait=wait)
            self._started = False
            logger.info("Scheduler stopped")
    
    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._started and self.scheduler.running
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        return {
            "running": self.is_running,
            "job_count": len(self._jobs),
            "timezone": self.timezone,
            "jobs": self.list_jobs(),
        }


# Global scheduler instance
_global_scheduler: Optional[Scheduler] = None


def get_scheduler() -> Scheduler:
    """Get the global scheduler instance."""
    global _global_scheduler
    if _global_scheduler is None:
        _global_scheduler = Scheduler()
    return _global_scheduler
