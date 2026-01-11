"""
Trigger definitions for the scheduler.

Provides convenient wrappers around APScheduler triggers.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union


@dataclass
class IntervalTrigger:
    """
    Interval-based trigger for recurring jobs.
    
    Example:
        >>> trigger = IntervalTrigger(hours=1)
        >>> trigger = IntervalTrigger(minutes=30)
    """
    
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    def to_dict(self):
        return {
            "weeks": self.weeks,
            "days": self.days,
            "hours": self.hours,
            "minutes": self.minutes,
            "seconds": self.seconds,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }


@dataclass
class CronTrigger:
    """
    Cron-based trigger for scheduled jobs.
    
    Example:
        >>> trigger = CronTrigger(hour=2, minute=30)  # Daily at 2:30 AM
        >>> trigger = CronTrigger(day_of_week="mon-fri", hour=9)  # Weekdays at 9 AM
    """
    
    year: Optional[Union[int, str]] = None
    month: Optional[Union[int, str]] = None
    day: Optional[Union[int, str]] = None
    week: Optional[Union[int, str]] = None
    day_of_week: Optional[Union[int, str]] = None
    hour: Optional[Union[int, str]] = None
    minute: Optional[Union[int, str]] = None
    second: Optional[Union[int, str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    def to_dict(self):
        result = {}
        for field_name in [
            "year", "month", "day", "week", "day_of_week",
            "hour", "minute", "second", "start_date", "end_date"
        ]:
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value
        return result


@dataclass
class DateTrigger:
    """
    One-time trigger for a specific date/time.
    
    Example:
        >>> trigger = DateTrigger(run_date=datetime(2024, 12, 31, 23, 59))
    """
    
    run_date: datetime
    
    def to_dict(self):
        return {"run_date": self.run_date}


# Convenience functions for creating triggers
def every_minutes(minutes: int) -> IntervalTrigger:
    """Create an interval trigger for every N minutes."""
    return IntervalTrigger(minutes=minutes)


def every_hours(hours: int) -> IntervalTrigger:
    """Create an interval trigger for every N hours."""
    return IntervalTrigger(hours=hours)


def daily_at(hour: int, minute: int = 0) -> CronTrigger:
    """Create a cron trigger for daily at a specific time."""
    return CronTrigger(hour=hour, minute=minute)


def weekly_on(day_of_week: str, hour: int = 0, minute: int = 0) -> CronTrigger:
    """Create a cron trigger for weekly on a specific day."""
    return CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)


def monthly_on(day: int, hour: int = 0, minute: int = 0) -> CronTrigger:
    """Create a cron trigger for monthly on a specific day."""
    return CronTrigger(day=day, hour=hour, minute=minute)


def at_time(run_date: datetime) -> DateTrigger:
    """Create a one-time trigger for a specific datetime."""
    return DateTrigger(run_date=run_date)
