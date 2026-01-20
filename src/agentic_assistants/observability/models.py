"""
Pydantic models for observability and usage tracking.

This module defines the data models for tracking framework usage,
including agent runs, API calls, RAG queries, and errors.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of usage events."""
    AGENT_RUN = "agent_run"
    API_CALL = "api_call"
    RAG_QUERY = "rag_query"
    MEMORY_ACCESS = "memory_access"
    MODEL_INFERENCE = "model_inference"
    PIPELINE_RUN = "pipeline_run"
    ERROR = "error"
    CONFIG_CHANGE = "config_change"
    USER_INTERACTION = "user_interaction"


class Framework(str, Enum):
    """Supported agent frameworks."""
    CREWAI = "crewai"
    LANGGRAPH = "langgraph"
    AUTOGEN = "autogen"
    GOOGLE_ADK = "google_adk"
    AGNO = "agno"
    LANGFLOW = "langflow"
    NATIVE = "native"  # Built-in framework functionality


class SuggestionPriority(str, Enum):
    """Priority levels for meta-analysis suggestions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SuggestionCategory(str, Enum):
    """Categories for meta-analysis suggestions."""
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    COST_OPTIMIZATION = "cost_optimization"
    CONFIGURATION = "configuration"
    FEATURE_ADOPTION = "feature_adoption"
    ERROR_PREVENTION = "error_prevention"
    WORKFLOW_IMPROVEMENT = "workflow_improvement"


class UsageEvent(BaseModel):
    """Base model for all usage events."""
    
    id: Optional[str] = Field(default=None, description="Unique event ID")
    event_type: EventType = Field(..., description="Type of the event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    user_id: Optional[str] = Field(default=None, description="User who triggered the event")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    project_id: Optional[str] = Field(default=None, description="Associated project ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        use_enum_values = True


class AgentRunEvent(UsageEvent):
    """Event for tracking agent executions."""
    
    event_type: EventType = Field(default=EventType.AGENT_RUN)
    agent_name: str = Field(..., description="Name of the agent")
    agent_id: Optional[str] = Field(default=None, description="Agent ID")
    framework: Framework = Field(..., description="Agent framework used")
    model: str = Field(..., description="LLM model used")
    duration_seconds: float = Field(..., description="Execution duration in seconds")
    success: bool = Field(..., description="Whether the run succeeded")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    tokens_input: Optional[int] = Field(default=None, description="Input tokens used")
    tokens_output: Optional[int] = Field(default=None, description="Output tokens generated")
    task_type: Optional[str] = Field(default=None, description="Type of task performed")
    tools_used: List[str] = Field(default_factory=list, description="Tools used during execution")


class APICallEvent(UsageEvent):
    """Event for tracking API calls."""
    
    event_type: EventType = Field(default=EventType.API_CALL)
    endpoint: str = Field(..., description="API endpoint called")
    method: str = Field(..., description="HTTP method")
    status_code: int = Field(..., description="Response status code")
    duration_ms: float = Field(..., description="Request duration in milliseconds")
    success: bool = Field(..., description="Whether the call succeeded")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    request_size_bytes: Optional[int] = Field(default=None, description="Request size")
    response_size_bytes: Optional[int] = Field(default=None, description="Response size")


class RAGQueryEvent(UsageEvent):
    """Event for tracking RAG queries."""
    
    event_type: EventType = Field(default=EventType.RAG_QUERY)
    knowledge_base: str = Field(..., description="Knowledge base queried")
    query: str = Field(..., description="Query text")
    num_results: int = Field(..., description="Number of results returned")
    top_score: Optional[float] = Field(default=None, description="Highest similarity score")
    avg_score: Optional[float] = Field(default=None, description="Average similarity score")
    duration_ms: float = Field(..., description="Query duration in milliseconds")
    embedding_model: Optional[str] = Field(default=None, description="Embedding model used")
    used_for_generation: bool = Field(default=False, description="Whether results were used for LLM generation")


class MemoryAccessEvent(UsageEvent):
    """Event for tracking memory accesses."""
    
    event_type: EventType = Field(default=EventType.MEMORY_ACCESS)
    operation: str = Field(..., description="Operation type (read, write, search)")
    memory_type: str = Field(..., description="Type of memory (episodic, semantic, etc.)")
    num_memories: int = Field(default=0, description="Number of memories accessed/stored")
    duration_ms: float = Field(..., description="Operation duration in milliseconds")
    success: bool = Field(default=True, description="Whether the operation succeeded")


class ModelInferenceEvent(UsageEvent):
    """Event for tracking model inference calls."""
    
    event_type: EventType = Field(default=EventType.MODEL_INFERENCE)
    model: str = Field(..., description="Model used for inference")
    provider: str = Field(default="ollama", description="Model provider")
    prompt_tokens: int = Field(default=0, description="Number of prompt tokens")
    completion_tokens: int = Field(default=0, description="Number of completion tokens")
    duration_ms: float = Field(..., description="Inference duration in milliseconds")
    success: bool = Field(default=True, description="Whether inference succeeded")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    temperature: Optional[float] = Field(default=None, description="Temperature setting")
    max_tokens: Optional[int] = Field(default=None, description="Max tokens setting")


class ErrorEvent(UsageEvent):
    """Event for tracking errors."""
    
    event_type: EventType = Field(default=EventType.ERROR)
    error_type: str = Field(..., description="Type/class of error")
    error_message: str = Field(..., description="Error message")
    stack_trace: Optional[str] = Field(default=None, description="Stack trace")
    component: str = Field(..., description="Component where error occurred")
    framework: Optional[Framework] = Field(default=None, description="Framework involved")
    recoverable: bool = Field(default=True, description="Whether the error was recoverable")
    resolution: Optional[str] = Field(default=None, description="How the error was resolved")


class ConfigChangeEvent(UsageEvent):
    """Event for tracking configuration changes."""
    
    event_type: EventType = Field(default=EventType.CONFIG_CHANGE)
    config_section: str = Field(..., description="Configuration section changed")
    setting_name: str = Field(..., description="Setting that was changed")
    old_value: Optional[str] = Field(default=None, description="Previous value")
    new_value: str = Field(..., description="New value")
    changed_by: str = Field(default="user", description="Who/what made the change")


class UserInteractionEvent(UsageEvent):
    """Event for tracking user interactions with the assistant."""
    
    event_type: EventType = Field(default=EventType.USER_INTERACTION)
    interaction_type: str = Field(..., description="Type of interaction (chat, command, etc.)")
    feature_used: str = Field(..., description="Feature being used")
    input_length: int = Field(default=0, description="Length of user input")
    response_length: int = Field(default=0, description="Length of assistant response")
    duration_ms: float = Field(default=0, description="Interaction duration")
    satisfaction_score: Optional[int] = Field(default=None, description="User satisfaction (1-5)")


class FrameworkUsageStats(BaseModel):
    """Statistics for a specific framework."""
    
    framework: Framework
    total_runs: int = Field(default=0, description="Total number of runs")
    successful_runs: int = Field(default=0, description="Number of successful runs")
    failed_runs: int = Field(default=0, description="Number of failed runs")
    total_duration_seconds: float = Field(default=0, description="Total execution time")
    avg_duration_seconds: float = Field(default=0, description="Average execution time")
    total_tokens: int = Field(default=0, description="Total tokens used")
    error_rate: float = Field(default=0, description="Error rate (0-1)")
    most_used_models: List[str] = Field(default_factory=list, description="Most frequently used models")
    common_error_types: List[str] = Field(default_factory=list, description="Most common error types")
    
    class Config:
        use_enum_values = True


class UsageAnalytics(BaseModel):
    """Aggregated usage analytics."""
    
    period_start: datetime = Field(..., description="Start of analytics period")
    period_end: datetime = Field(..., description="End of analytics period")
    total_events: int = Field(default=0, description="Total number of events")
    total_agent_runs: int = Field(default=0, description="Total agent runs")
    total_api_calls: int = Field(default=0, description="Total API calls")
    total_rag_queries: int = Field(default=0, description="Total RAG queries")
    total_errors: int = Field(default=0, description="Total errors")
    framework_stats: List[FrameworkUsageStats] = Field(
        default_factory=list, description="Stats per framework"
    )
    most_active_projects: List[str] = Field(
        default_factory=list, description="Most active project IDs"
    )
    peak_usage_hours: List[int] = Field(
        default_factory=list, description="Hours with peak usage (0-23)"
    )
    avg_response_time_ms: float = Field(default=0, description="Average API response time")
    rag_effectiveness_score: float = Field(
        default=0, description="RAG effectiveness (avg relevance score)"
    )


class MetaAnalysisSuggestion(BaseModel):
    """A suggestion generated by meta-analysis."""
    
    id: Optional[str] = Field(default=None, description="Suggestion ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When generated")
    category: SuggestionCategory = Field(..., description="Suggestion category")
    priority: SuggestionPriority = Field(..., description="Suggestion priority")
    title: str = Field(..., description="Short title")
    description: str = Field(..., description="Detailed description")
    evidence: List[str] = Field(default_factory=list, description="Evidence supporting the suggestion")
    recommended_action: str = Field(..., description="Recommended action to take")
    estimated_impact: str = Field(default="", description="Estimated impact of the change")
    affected_components: List[str] = Field(
        default_factory=list, description="Components that would be affected"
    )
    implemented: bool = Field(default=False, description="Whether the suggestion has been implemented")
    dismissed: bool = Field(default=False, description="Whether the suggestion was dismissed")
    dismissed_reason: Optional[str] = Field(default=None, description="Reason for dismissal")
    
    class Config:
        use_enum_values = True


class MetaAnalysisReport(BaseModel):
    """A complete meta-analysis report."""
    
    id: Optional[str] = Field(default=None, description="Report ID")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When generated")
    analysis_period_days: int = Field(default=7, description="Days of data analyzed")
    analytics: UsageAnalytics = Field(..., description="Usage analytics summary")
    suggestions: List[MetaAnalysisSuggestion] = Field(
        default_factory=list, description="Generated suggestions"
    )
    health_score: float = Field(
        default=0, description="Overall framework health score (0-100)"
    )
    trends: Dict[str, str] = Field(
        default_factory=dict, description="Trend indicators (improving, stable, declining)"
    )
    summary: str = Field(default="", description="Natural language summary")
