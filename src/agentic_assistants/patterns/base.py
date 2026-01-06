"""
Base classes for agentic design patterns.

This module provides the abstract base classes and common utilities
for implementing agentic design patterns.

Example:
    >>> from agentic_assistants.patterns.base import AgenticPattern
    >>> 
    >>> class MyPattern(AgenticPattern):
    ...     def execute(self, input_data):
    ...         # Pattern implementation
    ...         pass
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.mlflow_tracker import MLFlowTracker
from agentic_assistants.core.telemetry import TelemetryManager, trace_function
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PatternConfig:
    """
    Base configuration for agentic patterns.
    
    Attributes:
        name: Pattern name
        description: Pattern description
        max_iterations: Maximum iterations for iterative patterns
        timeout_seconds: Timeout for pattern execution
        verbose: Enable verbose output
        track_experiment: Enable MLFlow tracking
        trace_spans: Enable OpenTelemetry tracing
    """
    
    name: str = "unnamed_pattern"
    description: str = ""
    max_iterations: int = 10
    timeout_seconds: float = 300.0
    verbose: bool = True
    track_experiment: bool = True
    trace_spans: bool = True
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "max_iterations": self.max_iterations,
            "timeout_seconds": self.timeout_seconds,
            "verbose": self.verbose,
            "track_experiment": self.track_experiment,
            "trace_spans": self.trace_spans,
        }


@dataclass
class PatternResult:
    """
    Result from pattern execution.
    
    Attributes:
        success: Whether execution succeeded
        output: Pattern output
        iterations: Number of iterations (if applicable)
        duration_seconds: Execution duration
        steps: List of execution steps
        metadata: Additional metadata
        error: Error message if failed
    """
    
    success: bool
    output: Any = None
    iterations: int = 0
    duration_seconds: float = 0.0
    steps: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "output": str(self.output) if self.output else None,
            "iterations": self.iterations,
            "duration_seconds": self.duration_seconds,
            "steps": self.steps,
            "metadata": self.metadata,
            "error": self.error,
        }


@dataclass
class ExecutionStep:
    """
    A single step in pattern execution.
    
    Attributes:
        step_number: Step sequence number
        action: Action taken
        input_data: Input to the step
        output_data: Output from the step
        duration_ms: Step duration in milliseconds
        timestamp: When the step was executed
    """
    
    step_number: int
    action: str
    input_data: Any = None
    output_data: Any = None
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "step_number": self.step_number,
            "action": self.action,
            "input_data": str(self.input_data)[:200] if self.input_data else None,
            "output_data": str(self.output_data)[:200] if self.output_data else None,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }


class AgenticPattern(ABC):
    """
    Abstract base class for agentic design patterns.
    
    This class provides:
    - Common execution framework
    - MLFlow experiment tracking
    - OpenTelemetry tracing
    - Step tracking
    - Error handling
    
    Subclasses must implement:
    - _execute(): The pattern logic
    
    Attributes:
        config: Framework configuration
        pattern_config: Pattern-specific configuration
        tracker: MLFlow tracker
        telemetry: Telemetry manager
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        pattern_config: Optional[PatternConfig] = None,
    ):
        """
        Initialize the pattern.
        
        Args:
            config: Framework configuration
            pattern_config: Pattern configuration
        """
        self.config = config or AgenticConfig()
        self.pattern_config = pattern_config or PatternConfig()
        
        # Initialize tracking
        self.tracker = MLFlowTracker(self.config)
        self.telemetry = TelemetryManager(self.config)
        
        if self.config.telemetry_enabled and self.pattern_config.trace_spans:
            self.telemetry.initialize()
        
        # Execution state
        self._steps: list[ExecutionStep] = []
        self._current_step = 0
    
    @abstractmethod
    def _execute(self, input_data: Any) -> Any:
        """
        Execute the pattern logic.
        
        Args:
            input_data: Input data for the pattern
        
        Returns:
            Pattern output
        """
        pass
    
    def execute(
        self,
        input_data: Any,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> PatternResult:
        """
        Execute the pattern with full tracking.
        
        Args:
            input_data: Input data for the pattern
            experiment_name: MLFlow experiment name
            run_name: Run name
            tags: Additional tags
        
        Returns:
            PatternResult with output and metadata
        """
        start_time = time.time()
        self._steps = []
        self._current_step = 0
        
        result = PatternResult(success=False)
        
        # Set up tracking
        if experiment_name:
            self.tracker.experiment_name = experiment_name
        
        actual_run_name = run_name or f"{self.pattern_config.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        all_tags = {
            "pattern": self.pattern_config.name,
        }
        if tags:
            all_tags.update(tags)
        
        params = self.pattern_config.to_dict()
        
        with self.tracker.start_run(run_name=actual_run_name, tags=all_tags) as mlflow_run:
            with self.telemetry.span(
                f"pattern.{self.pattern_config.name}",
                attributes={"pattern": self.pattern_config.name},
            ) as span:
                try:
                    self.tracker.log_params(params)
                    
                    # Execute pattern
                    output = self._execute(input_data)
                    
                    # Build result
                    result.success = True
                    result.output = output
                    result.iterations = self._current_step
                    result.duration_seconds = time.time() - start_time
                    result.steps = [s.to_dict() for s in self._steps]
                    
                    # Log success
                    self.tracker.log_metrics({
                        "success": 1,
                        "duration_seconds": result.duration_seconds,
                        "iterations": result.iterations,
                    })
                    
                    span.set_attribute("success", True)
                    
                except Exception as e:
                    result.error = str(e)
                    result.duration_seconds = time.time() - start_time
                    result.steps = [s.to_dict() for s in self._steps]
                    
                    self.tracker.log_metrics({
                        "success": 0,
                        "duration_seconds": result.duration_seconds,
                    })
                    self.tracker.set_tag("error", str(e)[:200])
                    
                    span.set_attribute("success", False)
                    span.record_exception(e)
                    
                    logger.error(f"Pattern execution failed: {e}")
        
        return result
    
    def record_step(
        self,
        action: str,
        input_data: Any = None,
        output_data: Any = None,
        duration_ms: float = 0.0,
    ) -> None:
        """
        Record an execution step.
        
        Args:
            action: Action description
            input_data: Input to the step
            output_data: Output from the step
            duration_ms: Step duration
        """
        self._current_step += 1
        step = ExecutionStep(
            step_number=self._current_step,
            action=action,
            input_data=input_data,
            output_data=output_data,
            duration_ms=duration_ms,
        )
        self._steps.append(step)
        
        if self.pattern_config.verbose:
            logger.debug(f"Step {self._current_step}: {action}")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.pattern_config.name!r})"


class ComposablePattern(AgenticPattern):
    """
    A pattern that can be composed with other patterns.
    
    This enables chaining and combining patterns:
    
    Example:
        >>> pattern = pattern1.then(pattern2).then(pattern3)
        >>> result = pattern.execute(input_data)
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        pattern_config: Optional[PatternConfig] = None,
    ):
        super().__init__(config, pattern_config)
        self._next_pattern: Optional[ComposablePattern] = None
    
    def then(self, pattern: "ComposablePattern") -> "ComposablePattern":
        """
        Chain another pattern after this one.
        
        Args:
            pattern: Pattern to chain
        
        Returns:
            Self for fluent chaining
        """
        if self._next_pattern is None:
            self._next_pattern = pattern
        else:
            self._next_pattern.then(pattern)
        return self
    
    def _execute(self, input_data: Any) -> Any:
        """Execute this pattern and chain to next."""
        output = self._execute_self(input_data)
        
        if self._next_pattern is not None:
            return self._next_pattern._execute(output)
        
        return output
    
    @abstractmethod
    def _execute_self(self, input_data: Any) -> Any:
        """Execute just this pattern's logic."""
        pass


# Utility functions for pattern creation
def create_simple_pattern(
    name: str,
    execute_fn: Callable[[Any], Any],
    config: Optional[AgenticConfig] = None,
) -> AgenticPattern:
    """
    Create a simple pattern from a function.
    
    Args:
        name: Pattern name
        execute_fn: Function to execute
        config: Configuration
    
    Returns:
        AgenticPattern instance
    
    Example:
        >>> def my_logic(data):
        ...     return data.upper()
        >>> 
        >>> pattern = create_simple_pattern("uppercase", my_logic)
        >>> result = pattern.execute("hello")
    """
    class SimplePattern(AgenticPattern):
        def _execute(self, input_data: Any) -> Any:
            return execute_fn(input_data)
    
    pattern_config = PatternConfig(name=name)
    return SimplePattern(config=config, pattern_config=pattern_config)

