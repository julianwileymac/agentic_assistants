"""
Observability module for Agentic Assistants.

This module provides usage tracking and meta-analysis capabilities
for monitoring framework usage patterns and generating improvement suggestions.

Key components:
- UsageTracker: Track all framework interactions, API calls, agent runs
- MetaAnalyzer: Analyze usage patterns and generate optimization suggestions
- UsageEvent: Pydantic models for usage events

Example:
    >>> from agentic_assistants.observability import UsageTracker, MetaAnalyzer
    >>> 
    >>> # Track usage events
    >>> tracker = UsageTracker()
    >>> tracker.track_agent_run(
    ...     agent_name="research_agent",
    ...     framework="crewai",
    ...     duration_seconds=12.5,
    ...     success=True,
    ... )
    >>> 
    >>> # Analyze usage patterns
    >>> analyzer = MetaAnalyzer(tracker)
    >>> suggestions = analyzer.generate_suggestions()
"""

from agentic_assistants.observability.models import (
    UsageEvent,
    AgentRunEvent,
    APICallEvent,
    RAGQueryEvent,
    ErrorEvent,
    FrameworkUsageStats,
    UsageAnalytics,
    MetaAnalysisSuggestion,
    SuggestionPriority,
    SuggestionCategory,
)
from agentic_assistants.observability.usage_tracker import UsageTracker
from agentic_assistants.observability.meta_analyzer import MetaAnalyzer
from agentic_assistants.observability.trace_store import (
    FileSpanExporter,
    TraceStore,
)

__all__ = [
    # Models
    "UsageEvent",
    "AgentRunEvent",
    "APICallEvent",
    "RAGQueryEvent",
    "ErrorEvent",
    "FrameworkUsageStats",
    "UsageAnalytics",
    "MetaAnalysisSuggestion",
    "SuggestionPriority",
    "SuggestionCategory",
    # Tracker
    "UsageTracker",
    # Analyzer
    "MetaAnalyzer",
    # Trace storage
    "FileSpanExporter",
    "TraceStore",
]
