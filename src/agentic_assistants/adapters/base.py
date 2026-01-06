"""
Base adapter class for agent framework integrations.

This module provides the abstract base class that all framework adapters
inherit from, ensuring consistent interfaces for observability.

Example:
    >>> class MyAdapter(BaseAdapter):
    ...     def run(self, inputs):
    ...         with self.track_run("my-run"):
    ...             return self._execute(inputs)
"""

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.mlflow_tracker import MLFlowTracker
from agentic_assistants.core.telemetry import TelemetryManager
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class BaseAdapter(ABC):
    """
    Abstract base class for agent framework adapters.
    
    This class provides common functionality for:
    - MLFlow experiment tracking
    - OpenTelemetry tracing
    - Standardized logging
    
    Subclasses should implement framework-specific logic while
    using the provided observability methods.
    
    Attributes:
        config: Agentic configuration instance
        tracker: MLFlow tracker instance
        telemetry: Telemetry manager instance
        name: Adapter name for logging/tracing
    """

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        name: Optional[str] = None,
    ):
        """
        Initialize the adapter.
        
        Args:
            config: Configuration instance. If None, uses default config.
            name: Adapter name. If None, uses class name.
        """
        self.config = config or AgenticConfig()
        self.name = name or self.__class__.__name__
        self.tracker = MLFlowTracker(self.config)
        self.telemetry = TelemetryManager(self.config)

        # Initialize telemetry if enabled
        if self.config.telemetry_enabled:
            self.telemetry.initialize()

    @contextmanager
    def track_run(
        self,
        run_name: str,
        tags: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
    ):
        """
        Context manager for tracking a run with both MLFlow and OpenTelemetry.
        
        Args:
            run_name: Name for the run
            tags: Optional tags for MLFlow
            params: Optional parameters to log
        
        Yields:
            Tuple of (mlflow_run, span)
        
        Example:
            >>> with self.track_run("agent-task", params={"model": "llama3.2"}):
            ...     result = self.execute()
        """
        all_tags = {"adapter": self.name}
        if tags:
            all_tags.update(tags)

        with self.tracker.start_run(run_name=run_name, tags=all_tags) as mlflow_run:
            with self.telemetry.span(
                f"{self.name}.{run_name}",
                attributes={"adapter": self.name, "run_name": run_name},
            ) as span:
                # Log parameters
                if params:
                    self.tracker.log_params(params)
                    for key, value in params.items():
                        span.set_attribute(f"param.{key}", str(value))

                yield mlflow_run, span

    @contextmanager
    def track_step(
        self,
        step_name: str,
        step_number: Optional[int] = None,
        attributes: Optional[dict[str, Any]] = None,
    ):
        """
        Context manager for tracking an individual step within a run.
        
        Args:
            step_name: Name of the step
            step_number: Optional step number for ordering
            attributes: Optional attributes for the span
        
        Yields:
            The span instance
        """
        span_name = f"{self.name}.step.{step_name}"
        span_attrs = {"step.name": step_name}
        if step_number is not None:
            span_attrs["step.number"] = step_number
        if attributes:
            span_attrs.update(attributes)

        with self.telemetry.span(span_name, attributes=span_attrs) as span:
            yield span

    def log_interaction(
        self,
        agent_name: str,
        input_text: str,
        output_text: str,
        model: str,
        duration_seconds: float,
        tokens_used: Optional[int] = None,
        step: Optional[int] = None,
    ) -> None:
        """
        Log an agent interaction with full observability.
        
        This method logs to both MLFlow (as artifacts/metrics) and
        OpenTelemetry (as metrics).
        
        Args:
            agent_name: Name of the agent
            input_text: Input to the agent
            output_text: Output from the agent
            model: Model used
            duration_seconds: Execution time
            tokens_used: Optional token count
            step: Optional step number
        """
        # Log to MLFlow
        self.tracker.log_agent_interaction(
            agent_name=agent_name,
            input_text=input_text,
            output_text=output_text,
            model=model,
            duration_seconds=duration_seconds,
            tokens_used=tokens_used,
            step=step,
        )

        # Record telemetry metrics
        self.telemetry.record_agent_metrics(
            agent_name=agent_name,
            model=model,
            duration_seconds=duration_seconds,
            tokens_input=tokens_used or 0,
            tokens_output=0,  # Would need separate tracking
            success=True,
        )

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """
        Execute the agent framework task.
        
        This method should be implemented by subclasses to provide
        framework-specific execution logic.
        
        Returns:
            Framework-specific result
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"

