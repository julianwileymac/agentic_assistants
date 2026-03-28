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

import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.foundation.types import AdapterRunMetadata
from agentic_assistants.core.mlflow_tracker import MLFlowTracker
from agentic_assistants.core.telemetry import TelemetryManager
from agentic_assistants.utils.logging import get_logger

if TYPE_CHECKING:
    from agentic_assistants.knowledge import KnowledgeBase
    from agentic_assistants.memory import AgentMemory
    from agentic_assistants.observability import UsageTracker

logger = get_logger(__name__)


class BaseAdapter(ABC):
    """
    Abstract base class for agent framework adapters.
    
    This class provides common functionality for:
    - MLFlow experiment tracking
    - OpenTelemetry tracing
    - Standardized logging
    - Usage tracking for meta-analysis
    - RAG knowledge base integration
    - Persistent memory support
    
    Subclasses should implement framework-specific logic while
    using the provided observability methods.
    
    Attributes:
        config: Agentic configuration instance
        tracker: MLFlow tracker instance
        telemetry: Telemetry manager instance
        name: Adapter name for logging/tracing
        framework_name: Name of the agent framework (e.g., "crewai")
        usage_tracker: Optional usage tracker for analytics
        knowledge_base: Optional RAG knowledge base
        memory: Optional persistent memory store
    """

    # Override in subclasses to specify the framework name
    framework_name: str = "base"

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        name: Optional[str] = None,
        usage_tracker: Optional["UsageTracker"] = None,
        knowledge_base: Optional["KnowledgeBase"] = None,
        memory: Optional["AgentMemory"] = None,
    ):
        """
        Initialize the adapter.
        
        Args:
            config: Configuration instance. If None, uses default config.
            name: Adapter name. If None, uses class name.
            usage_tracker: Optional usage tracker for analytics.
            knowledge_base: Optional RAG knowledge base for context.
            memory: Optional persistent memory store.
        """
        self.config = config or AgenticConfig()
        self.name = name or self.__class__.__name__
        self.tracker = MLFlowTracker(self.config)
        self.telemetry = TelemetryManager(self.config)
        
        # Optional components
        self._usage_tracker = usage_tracker
        self._knowledge_base = knowledge_base
        self._memory = memory

        # Initialize telemetry if enabled
        if self.config.telemetry_enabled:
            self.telemetry.initialize()
    
    @property
    def usage_tracker(self) -> Optional["UsageTracker"]:
        """Get the usage tracker, lazily initializing if configured."""
        if self._usage_tracker is None and self.config.assistant.usage_tracking_enabled:
            try:
                from agentic_assistants.observability import UsageTracker
                self._usage_tracker = UsageTracker(self.config)
            except ImportError:
                pass
        return self._usage_tracker
    
    @usage_tracker.setter
    def usage_tracker(self, tracker: "UsageTracker") -> None:
        """Set the usage tracker."""
        self._usage_tracker = tracker
    
    @property
    def knowledge_base(self) -> Optional["KnowledgeBase"]:
        """Get the knowledge base."""
        return self._knowledge_base
    
    @knowledge_base.setter
    def knowledge_base(self, kb: "KnowledgeBase") -> None:
        """Set the knowledge base for RAG."""
        self._knowledge_base = kb
    
    @property
    def memory(self) -> Optional["AgentMemory"]:
        """Get the memory store."""
        return self._memory
    
    @memory.setter
    def memory(self, mem: "AgentMemory") -> None:
        """Set the memory store."""
        self._memory = mem
    
    def connect_rag(self, knowledge_base: "KnowledgeBase") -> "BaseAdapter":
        """
        Connect a RAG knowledge base to the adapter.
        
        Args:
            knowledge_base: The knowledge base to use for RAG
            
        Returns:
            Self for chaining
        """
        self._knowledge_base = knowledge_base
        logger.info(f"Connected RAG knowledge base to {self.name}")
        return self
    
    def connect_memory(self, memory: "AgentMemory") -> "BaseAdapter":
        """
        Connect a memory store to the adapter.
        
        Args:
            memory: The memory store to use
            
        Returns:
            Self for chaining
        """
        self._memory = memory
        logger.info(f"Connected memory store to {self.name}")
        return self
    
    def get_rag_context(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get relevant context from the RAG knowledge base.
        
        Args:
            query: The query to search for
            top_k: Number of results to return
            filters: Optional filters for the search
            
        Returns:
            List of search results with content and metadata
        """
        if self._knowledge_base is None:
            return []
        
        start_time = time.time()
        results = self._knowledge_base.search(query, top_k=top_k, filters=filters)
        duration_ms = (time.time() - start_time) * 1000
        
        # Track the RAG query if usage tracking is enabled
        if self.usage_tracker:
            self.usage_tracker.track_rag_query(
                knowledge_base=getattr(self._knowledge_base, 'name', 'default'),
                query=query[:200],  # Truncate for storage
                num_results=len(results),
                duration_ms=duration_ms,
                top_score=results[0].score if results else None,
                avg_score=sum(r.score for r in results) / len(results) if results else None,
                used_for_generation=True,
            )
        
        return [
            {"content": r.content, "source": r.source, "score": r.score, "metadata": r.metadata}
            for r in results
        ]
    
    def get_memory_context(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get relevant memories from the memory store.
        
        Args:
            query: The query to search for
            limit: Maximum number of memories to return
            
        Returns:
            List of relevant memories
        """
        if self._memory is None:
            return []
        
        try:
            results = self._memory.search_memories(query, limit=limit)
            return results
        except Exception as e:
            logger.warning(f"Failed to get memory context: {e}")
            return []
    
    def store_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Store a new memory.
        
        Args:
            content: The memory content
            metadata: Optional metadata
            
        Returns:
            Memory ID if stored successfully
        """
        if self._memory is None:
            return None
        
        try:
            return self._memory.add_memory(content, metadata or {})
        except Exception as e:
            logger.warning(f"Failed to store memory: {e}")
            return None

    @contextmanager
    def track_run(
        self,
        run_name: str,
        tags: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        agent_name: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Context manager for tracking a run with MLFlow, OpenTelemetry, and usage tracking.
        
        Args:
            run_name: Name for the run
            tags: Optional tags for MLFlow
            params: Optional parameters to log
            agent_name: Optional agent name for usage tracking
            model: Optional model name for usage tracking
        
        Yields:
            Tuple of (mlflow_run, span)
        
        Example:
            >>> with self.track_run("agent-task", params={"model": "llama3.2"}):
            ...     result = self.execute()
        """
        all_tags: dict[str, str] = {"adapter": self.name, "framework": self.framework_name}
        if tags:
            all_tags.update(tags)

        start_time = time.time()
        success = True
        error_message = None
        metadata: AdapterRunMetadata = {
            "framework": self.framework_name,
            "run_name": run_name,
            "agent_name": agent_name or run_name,
            "model": model or (params.get("model", "unknown") if params else "unknown"),
            "tags": all_tags,
            "params": params or {},
        }
        
        with self.tracker.start_run(run_name=run_name, tags=all_tags) as mlflow_run:
            with self.telemetry.span(
                f"{self.name}.{run_name}",
                attributes={"adapter": self.name, "run_name": run_name, "framework": self.framework_name},
            ) as span:
                # Log parameters
                if params:
                    self.tracker.log_params(params)
                    for key, value in params.items():
                        span.set_attribute(f"param.{key}", str(value))

                try:
                    yield mlflow_run, span
                except Exception as e:
                    success = False
                    error_message = str(e)
                    raise
                finally:
                    # Track usage
                    duration = time.time() - start_time
                    if self.usage_tracker:
                        self.usage_tracker.track_agent_run(
                            agent_name=agent_name or run_name,
                            framework=self.framework_name,
                            model=metadata["model"],
                            duration_seconds=duration,
                            success=success,
                            error_message=error_message,
                            metadata=dict(metadata),
                        )

    @contextmanager
    def track_step(
        self,
        step_name: str,
        step_number: Optional[int] = None,
        attributes: Optional[Dict[str, Any]] = None,
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
        span_attrs: Dict[str, Any] = {"step.name": step_name}
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
        success: bool = True,
    ) -> None:
        """
        Log an agent interaction with full observability.
        
        This method logs to both MLFlow (as artifacts/metrics) and
        OpenTelemetry (as metrics), plus usage tracking.
        
        Args:
            agent_name: Name of the agent
            input_text: Input to the agent
            output_text: Output from the agent
            model: Model used
            duration_seconds: Execution time
            tokens_used: Optional token count
            step: Optional step number
            success: Whether the interaction was successful
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
            success=success,
        )
        
        # Track model inference for usage analytics
        if self.usage_tracker:
            self.usage_tracker.track_model_inference(
                model=model,
                duration_ms=duration_seconds * 1000,
                prompt_tokens=tokens_used or 0,
                success=success,
            )
    
    def log_error(
        self,
        error: Exception,
        component: str,
        recoverable: bool = True,
        resolution: Optional[str] = None,
    ) -> None:
        """
        Log an error with usage tracking.
        
        Args:
            error: The exception that occurred
            component: Component where error occurred
            recoverable: Whether the error was recoverable
            resolution: How the error was resolved (if at all)
        """
        import traceback
        
        if self.usage_tracker:
            self.usage_tracker.track_error(
                error_type=type(error).__name__,
                error_message=str(error),
                component=component,
                stack_trace=traceback.format_exc(),
                framework=self.framework_name,
                recoverable=recoverable,
                resolution=resolution,
            )
        
        logger.error(f"Error in {component}: {error}")

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
    
    def get_framework_info(self) -> Dict[str, Any]:
        """
        Get information about this adapter's framework.
        
        Returns:
            Dictionary with framework information
        """
        return {
            "name": self.name,
            "framework": self.framework_name,
            "has_rag": self._knowledge_base is not None,
            "has_memory": self._memory is not None,
            "usage_tracking": self.usage_tracker is not None,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, framework={self.framework_name!r})"

