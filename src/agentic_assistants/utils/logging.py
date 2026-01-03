"""
Structured logging utilities for Agentic Assistants.

This module provides logging setup with OpenTelemetry correlation,
structured output, and configurable log levels.

Example:
    >>> from agentic_assistants.utils.logging import setup_logging, get_logger
    >>> setup_logging(level="DEBUG")
    >>> logger = get_logger(__name__)
    >>> logger.info("Processing request", extra={"user_id": 123})
"""

import logging
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


# Global console for rich output
console = Console()

# Cache for loggers
_loggers: dict[str, logging.Logger] = {}


def setup_logging(
    level: str = "INFO",
    enable_rich: bool = True,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_rich: Use rich handler for colorful console output
        log_file: Optional file path for file logging
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Create formatters
    detailed_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    simple_format = "%(message)s"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add console handler
    if enable_rich:
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
        console_handler.setFormatter(logging.Formatter(simple_format))
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(detailed_format))

    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(detailed_format))
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)
    return _loggers[name]


class LogContext:
    """
    Context manager for adding contextual information to log messages.
    
    Example:
        >>> with LogContext(request_id="abc123", user="john"):
        ...     logger.info("Processing request")
    """

    _context: dict = {}

    def __init__(self, **kwargs):
        self.new_context = kwargs
        self.old_context = {}

    def __enter__(self):
        self.old_context = LogContext._context.copy()
        LogContext._context.update(self.new_context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        LogContext._context = self.old_context
        return False

    @classmethod
    def get_context(cls) -> dict:
        """Get the current logging context."""
        return cls._context.copy()

