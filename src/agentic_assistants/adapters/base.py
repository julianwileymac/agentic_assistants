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
import time
from typing import Any, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.mlflow_tracker import MLFlowTracker
from agentic_assistants.core.telemetry import TelemetryManager, VerboseSpanLogger
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class BaseAdapter(ABC):
    """
    Abstract base class for agent framework adapters.
    
    This class provides common functionality for:
    - MLFlow experiment tracking
    - OpenTelemetry tracing with verbose logging
    - Standardized logging
    - LLM call instrumentation
    
    Subclasses should implement framework-specific logic while
    using the provided observability methods.
    
    Attributes:
        config: Agentic configuration instance
        tracker: MLFlow tracker instance
        telemetry: Telemetry manager instance
        name: Adapter name for logging/tracing
        verbose: Enable verbose span logging
    """

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        name: Optional[str] = None,
        verbose: bool = False,
    ):
        """
        Initialize the adapter.
        
        Args:
            config: Configuration instance. If None, uses default config.
            name: Adapter name. If None, uses class name.
            verbose: Enable verbose telemetry logging
        """
        self.config = config or AgenticConfig()
        self.name = name or self.__class__.__name__
        self.verbose = verbose or self.config.log_level == "DEBUG"
        self.tracker = MLFlowTracker(self.config)
        self.telemetry = TelemetryManager(self.config, verbose=self.verbose)

        # Initialize telemetry if enabled
        if self.config.telemetry_enabled:
            self.telemetry.initialize()
            if self.verbose:
                logger.debug(f"Initialized {self.name} adapter with verbose telemetry")

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
            Tuple of (mlflow_run, VerboseSpanLogger)
        
        Example:
            >>> with self.track_run("agent-task", params={"model": "llama3.2"}) as (run, span):
            ...     span.log_input(input_data)
            ...     result = self.execute()
            ...     span.log_output(result)
        """
        all_tags = {"adapter": self.name}
        if tags:
            all_tags.update(tags)

        start_time = time.time()
        
        with self.tracker.start_run(run_name=run_name, tags=all_tags) as mlflow_run:
            with self.telemetry.span(
                f"{self.name}.{run_name}",
                attributes={
                    "adapter": self.name,
                    "run_name": run_name,
                    "framework": self.name.lower(),
                },
            ) as span_logger:
                # Log parameters to both MLFlow and span
                if params:
                    self.tracker.log_params(params)
                    for key, value in params.items():
                        span_logger.span.set_attribute(f"param.{key}", str(value)[:500])
                    span_logger.log_event("params_logged", {"count": len(params)})

                try:
                    yield mlflow_run, span_logger
                except Exception as e:
                    # Log error to both MLFlow and telemetry
                    self.tracker.log_metric("success", 0)
                    self.tracker.set_tag("error", str(e)[:500])
                    span_logger.log_error(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    self.tracker.log_metric("duration_seconds", duration)

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
            VerboseSpanLogger instance
        """
        span_name = f"{self.name}.step.{step_name}"
        span_attrs = {
            "step.name": step_name,
            "adapter": self.name,
        }
        if step_number is not None:
            span_attrs["step.number"] = step_number
        if attributes:
            span_attrs.update({k: str(v)[:500] for k, v in attributes.items()})

        with self.telemetry.span(span_name, attributes=span_attrs) as span_logger:
            span_logger.log_event("step_started", {"step": step_name, "number": step_number})
            yield span_logger

    @contextmanager
    def track_llm_call(
        self,
        model: str,
        operation: str = "generate",
        temperature: float = 0.0,
    ):
        """
        Context manager for tracking an LLM call with detailed metrics.
        
        Args:
            model: Model name
            operation: Operation type (generate, chat, embed, etc.)
            temperature: Model temperature
        
        Yields:
            VerboseSpanLogger for logging input/output
        """
        span_name = f"{self.name}.llm.{operation}"
        
        with self.telemetry.span(
            span_name,
            attributes={
                "llm.model": model,
                "llm.operation": operation,
                "llm.temperature": temperature,
                "adapter": self.name,
            },
        ) as span_logger:
            span_logger.log_event("llm_call_started", {
                "model": model,
                "operation": operation,
            })
            yield span_logger

    def log_interaction(
        self,
        agent_name: str,
        input_text: str,
        output_text: str,
        model: str,
        duration_seconds: float,
        tokens_used: Optional[int] = None,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
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
            tokens_used: Total token count (deprecated, use tokens_input/output)
            tokens_input: Input token count
            tokens_output: Output token count
            step: Optional step number
        """
        # Calculate token counts
        total_tokens = tokens_used or ((tokens_input or 0) + (tokens_output or 0))
        
        # Log to MLFlow
        self.tracker.log_agent_interaction(
            agent_name=agent_name,
            input_text=input_text,
            output_text=output_text,
            model=model,
            duration_seconds=duration_seconds,
            tokens_used=total_tokens,
            step=step,
        )

        # Record telemetry metrics
        self.telemetry.record_agent_metrics(
            agent_name=agent_name,
            model=model,
            duration_seconds=duration_seconds,
            tokens_input=tokens_input or tokens_used or 0,
            tokens_output=tokens_output or 0,
            success=True,
        )
        
        if self.verbose:
            logger.debug(
                f"Agent '{agent_name}' interaction: "
                f"model={model}, duration={duration_seconds:.2f}s, tokens={total_tokens}"
            )

    def log_tool_call(
        self,
        tool_name: str,
        input_args: dict,
        output: Any,
        duration_seconds: float,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """
        Log a tool call with telemetry.
        
        Args:
            tool_name: Name of the tool
            input_args: Input arguments
            output: Tool output
            duration_seconds: Execution time
            success: Whether the call succeeded
            error: Error message if failed
        """
        # Log to MLFlow
        self.tracker.log_metric(f"tool.{tool_name}.duration", duration_seconds)
        self.tracker.log_metric(f"tool.{tool_name}.success", 1 if success else 0)
        
        if error:
            self.tracker.set_tag(f"tool.{tool_name}.error", error[:500])
        
        # Log artifact with tool call details
        tool_call = {
            "tool": tool_name,
            "input": {k: str(v)[:200] for k, v in input_args.items()},
            "output": str(output)[:500],
            "duration": duration_seconds,
            "success": success,
            "error": error,
        }
        self.tracker.log_dict(tool_call, f"tools/{tool_name}_call.json")
        
        if self.verbose:
            logger.debug(f"Tool '{tool_name}' called: success={success}, duration={duration_seconds:.2f}s")

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
        return f"{self.__class__.__name__}(name={self.name!r}, verbose={self.verbose})"
