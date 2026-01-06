"""
Specialized telemetry for CrewAI crew execution.

This module provides verbose OpenTelemetry tracing specifically for:
- Crew execution lifecycle
- Agent task execution
- Tool invocations
- LLM calls within crews

Example:
    >>> from agentic_assistants.crews.telemetry import CrewTelemetry
    >>> 
    >>> telemetry = CrewTelemetry()
    >>> with telemetry.trace_crew_run("my-crew") as span:
    ...     span.set_attribute("agent_count", 3)
    ...     result = crew.kickoff()
"""

import functools
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.telemetry import TelemetryManager, get_tracer, get_meter
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class CrewTelemetry:
    """
    Specialized telemetry for CrewAI crews.
    
    This class provides:
    - Crew-level span management
    - Agent execution tracing
    - Task completion tracking
    - Tool invocation tracing
    - Token usage metrics
    
    All traces include rich attributes for debugging and analysis.
    
    Attributes:
        config: Framework configuration
        telemetry: Base telemetry manager
        tracer: OpenTelemetry tracer
        meter: OpenTelemetry meter
    """
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """
        Initialize crew telemetry.
        
        Args:
            config: Framework configuration
        """
        self.config = config or AgenticConfig()
        self.telemetry = TelemetryManager(self.config)
        self.enabled = self.config.telemetry_enabled
        
        if self.enabled:
            self.telemetry.initialize()
        
        # Get tracer and meter
        self.tracer = get_tracer("agentic-crews")
        self.meter = get_meter("agentic-crews")
        
        # Create metrics
        self._setup_metrics()
    
    def _setup_metrics(self) -> None:
        """Set up crew-specific metrics."""
        if not self.enabled:
            return
        
        try:
            # Crew execution metrics
            self._crew_duration = self.meter.create_histogram(
                "crew.duration",
                description="Crew execution duration in seconds",
                unit="s",
            )
            
            self._task_counter = self.meter.create_counter(
                "crew.tasks.completed",
                description="Number of completed tasks",
                unit="1",
            )
            
            self._agent_invocations = self.meter.create_counter(
                "crew.agent.invocations",
                description="Number of agent invocations",
                unit="1",
            )
            
            self._tool_calls = self.meter.create_counter(
                "crew.tool.calls",
                description="Number of tool calls",
                unit="1",
            )
            
            self._token_usage = self.meter.create_counter(
                "crew.tokens",
                description="Token usage",
                unit="tokens",
            )
            
            self._indexing_chunks = self.meter.create_counter(
                "crew.indexing.chunks",
                description="Number of chunks indexed",
                unit="1",
            )
            
        except Exception as e:
            logger.warning(f"Failed to setup crew metrics: {e}")
    
    @contextmanager
    def trace_crew_run(
        self,
        crew_name: str,
        attributes: Optional[dict[str, Any]] = None,
    ):
        """
        Trace a complete crew run.
        
        Args:
            crew_name: Name of the crew
            attributes: Additional span attributes
        
        Yields:
            Span for the crew run
        
        Example:
            >>> with telemetry.trace_crew_run("indexing-crew") as span:
            ...     span.set_attribute("repo_path", "/path/to/repo")
            ...     result = crew.kickoff()
        """
        if not self.enabled:
            yield _NoOpSpan()
            return
        
        span_name = f"crew.{crew_name}.run"
        span_attrs = {
            "crew.name": crew_name,
            "crew.start_time": datetime.utcnow().isoformat(),
        }
        if attributes:
            span_attrs.update(attributes)
        
        start_time = time.time()
        
        with self.tracer.start_as_current_span(span_name) as span:
            for key, value in span_attrs.items():
                span.set_attribute(key, str(value) if not isinstance(value, (int, float, bool)) else value)
            
            try:
                yield span
                span.set_attribute("crew.success", True)
            except Exception as e:
                span.set_attribute("crew.success", False)
                span.set_attribute("crew.error", str(e))
                span.record_exception(e)
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("crew.duration_seconds", duration)
                
                if self._crew_duration:
                    self._crew_duration.record(
                        duration,
                        {"crew.name": crew_name},
                    )
    
    @contextmanager
    def trace_agent_execution(
        self,
        agent_name: str,
        agent_role: str,
        task_description: Optional[str] = None,
    ):
        """
        Trace an agent's execution.
        
        Args:
            agent_name: Name of the agent
            agent_role: Agent's role
            task_description: Description of the task
        
        Yields:
            Span for agent execution
        """
        if not self.enabled:
            yield _NoOpSpan()
            return
        
        span_name = f"agent.{agent_name}.execute"
        span_attrs = {
            "agent.name": agent_name,
            "agent.role": agent_role,
            "agent.start_time": datetime.utcnow().isoformat(),
        }
        if task_description:
            span_attrs["agent.task"] = task_description[:200]
        
        start_time = time.time()
        
        with self.tracer.start_as_current_span(span_name) as span:
            for key, value in span_attrs.items():
                span.set_attribute(key, value)
            
            try:
                yield span
                span.set_attribute("agent.success", True)
                
                if self._agent_invocations:
                    self._agent_invocations.add(
                        1,
                        {"agent.name": agent_name, "agent.role": agent_role},
                    )
            except Exception as e:
                span.set_attribute("agent.success", False)
                span.set_attribute("agent.error", str(e))
                span.record_exception(e)
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("agent.duration_seconds", duration)
    
    @contextmanager
    def trace_task_execution(
        self,
        task_name: str,
        task_type: str,
        agent_name: Optional[str] = None,
    ):
        """
        Trace a task execution.
        
        Args:
            task_name: Name/description of the task
            task_type: Type of task
            agent_name: Assigned agent
        
        Yields:
            Span for task execution
        """
        if not self.enabled:
            yield _NoOpSpan()
            return
        
        span_name = f"task.{task_type}.execute"
        span_attrs = {
            "task.name": task_name[:100],
            "task.type": task_type,
            "task.start_time": datetime.utcnow().isoformat(),
        }
        if agent_name:
            span_attrs["task.agent"] = agent_name
        
        start_time = time.time()
        
        with self.tracer.start_as_current_span(span_name) as span:
            for key, value in span_attrs.items():
                span.set_attribute(key, value)
            
            try:
                yield span
                span.set_attribute("task.success", True)
                
                if self._task_counter:
                    self._task_counter.add(
                        1,
                        {"task.type": task_type, "task.success": "true"},
                    )
            except Exception as e:
                span.set_attribute("task.success", False)
                span.set_attribute("task.error", str(e))
                span.record_exception(e)
                
                if self._task_counter:
                    self._task_counter.add(
                        1,
                        {"task.type": task_type, "task.success": "false"},
                    )
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("task.duration_seconds", duration)
    
    @contextmanager
    def trace_tool_call(
        self,
        tool_name: str,
        tool_input: Optional[str] = None,
    ):
        """
        Trace a tool invocation.
        
        Args:
            tool_name: Name of the tool
            tool_input: Input to the tool
        
        Yields:
            Span for tool call
        """
        if not self.enabled:
            yield _NoOpSpan()
            return
        
        span_name = f"tool.{tool_name}.call"
        span_attrs = {
            "tool.name": tool_name,
            "tool.start_time": datetime.utcnow().isoformat(),
        }
        if tool_input:
            span_attrs["tool.input"] = tool_input[:200]
        
        start_time = time.time()
        
        with self.tracer.start_as_current_span(span_name) as span:
            for key, value in span_attrs.items():
                span.set_attribute(key, value)
            
            try:
                yield span
                span.set_attribute("tool.success", True)
                
                if self._tool_calls:
                    self._tool_calls.add(
                        1,
                        {"tool.name": tool_name, "tool.success": "true"},
                    )
            except Exception as e:
                span.set_attribute("tool.success", False)
                span.set_attribute("tool.error", str(e))
                span.record_exception(e)
                
                if self._tool_calls:
                    self._tool_calls.add(
                        1,
                        {"tool.name": tool_name, "tool.success": "false"},
                    )
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("tool.duration_ms", duration * 1000)
    
    @contextmanager
    def trace_llm_call(
        self,
        model: str,
        operation: str = "generate",
        prompt_tokens: Optional[int] = None,
    ):
        """
        Trace an LLM call.
        
        Args:
            model: Model name
            operation: Operation type
            prompt_tokens: Number of prompt tokens
        
        Yields:
            Span for LLM call
        """
        if not self.enabled:
            yield _NoOpSpan()
            return
        
        span_name = f"llm.{model}.{operation}"
        span_attrs = {
            "llm.model": model,
            "llm.operation": operation,
            "llm.start_time": datetime.utcnow().isoformat(),
        }
        if prompt_tokens:
            span_attrs["llm.prompt_tokens"] = prompt_tokens
        
        start_time = time.time()
        
        with self.tracer.start_as_current_span(span_name) as span:
            for key, value in span_attrs.items():
                span.set_attribute(key, str(value) if isinstance(value, (list, dict)) else value)
            
            try:
                yield span
                span.set_attribute("llm.success", True)
            except Exception as e:
                span.set_attribute("llm.success", False)
                span.set_attribute("llm.error", str(e))
                span.record_exception(e)
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("llm.duration_ms", duration * 1000)
    
    @contextmanager
    def trace_indexing(
        self,
        collection: str,
        source_path: str,
    ):
        """
        Trace an indexing operation.
        
        Args:
            collection: Vector store collection
            source_path: Source being indexed
        
        Yields:
            Span for indexing
        """
        if not self.enabled:
            yield _NoOpSpan()
            return
        
        span_name = f"indexing.{collection}"
        span_attrs = {
            "indexing.collection": collection,
            "indexing.source": source_path,
            "indexing.start_time": datetime.utcnow().isoformat(),
        }
        
        start_time = time.time()
        
        with self.tracer.start_as_current_span(span_name) as span:
            for key, value in span_attrs.items():
                span.set_attribute(key, value)
            
            try:
                yield span
                span.set_attribute("indexing.success", True)
            except Exception as e:
                span.set_attribute("indexing.success", False)
                span.set_attribute("indexing.error", str(e))
                span.record_exception(e)
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("indexing.duration_seconds", duration)
    
    def record_token_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        agent_name: Optional[str] = None,
    ) -> None:
        """
        Record token usage metrics.
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            agent_name: Agent that made the call
        """
        if not self.enabled or not self._token_usage:
            return
        
        attrs = {"llm.model": model}
        if agent_name:
            attrs["agent.name"] = agent_name
        
        self._token_usage.add(input_tokens, {**attrs, "token.type": "input"})
        self._token_usage.add(output_tokens, {**attrs, "token.type": "output"})
    
    def record_chunks_indexed(
        self,
        collection: str,
        chunk_count: int,
        file_count: Optional[int] = None,
    ) -> None:
        """
        Record indexing metrics.
        
        Args:
            collection: Collection name
            chunk_count: Number of chunks indexed
            file_count: Number of files processed
        """
        if not self.enabled or not self._indexing_chunks:
            return
        
        attrs = {"indexing.collection": collection}
        self._indexing_chunks.add(chunk_count, attrs)
    
    def add_event(
        self,
        name: str,
        attributes: Optional[dict] = None,
    ) -> None:
        """
        Add an event to the current span.
        
        Args:
            name: Event name
            attributes: Event attributes
        """
        if not self.enabled:
            return
        
        try:
            from opentelemetry import trace
            span = trace.get_current_span()
            if span:
                span.add_event(name, attributes=attributes)
        except Exception:
            pass


class _NoOpSpan:
    """No-operation span for when telemetry is disabled."""
    
    def set_attribute(self, key: str, value: Any) -> None:
        pass
    
    def set_attributes(self, attributes: dict[str, Any]) -> None:
        pass
    
    def add_event(self, name: str, attributes: Optional[dict] = None) -> None:
        pass
    
    def record_exception(self, exception: Exception) -> None:
        pass


def trace_crew_function(
    crew_name: Optional[str] = None,
    record_args: bool = False,
) -> Callable:
    """
    Decorator for tracing crew-related functions.
    
    Args:
        crew_name: Name of the crew
        record_args: Whether to record function arguments
    
    Returns:
        Decorated function
    
    Example:
        >>> @trace_crew_function("indexing")
        >>> def run_indexing_crew(repo_path: str):
        ...     # Implementation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            telemetry = CrewTelemetry()
            name = crew_name or func.__name__
            
            attrs = {}
            if record_args:
                for i, arg in enumerate(args):
                    attrs[f"arg.{i}"] = str(arg)[:100]
                for key, value in kwargs.items():
                    attrs[f"kwarg.{key}"] = str(value)[:100]
            
            with telemetry.trace_crew_run(name, attrs) as span:
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Global telemetry instance
_crew_telemetry: Optional[CrewTelemetry] = None


def get_crew_telemetry(config: Optional[AgenticConfig] = None) -> CrewTelemetry:
    """
    Get or create the global crew telemetry instance.
    
    Args:
        config: Configuration instance
    
    Returns:
        CrewTelemetry instance
    """
    global _crew_telemetry
    if _crew_telemetry is None:
        _crew_telemetry = CrewTelemetry(config)
    return _crew_telemetry

