"""
Framework Assistant API endpoints.

This module provides REST API endpoints for interacting with the
Framework Assistant, including chat, configuration, and analytics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.agents import FrameworkAssistantAgent, create_framework_assistant
from agentic_assistants.observability import MetaAnalyzer, UsageTracker
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/assistant", tags=["assistant"])

# Global assistant instance
_assistant: Optional[FrameworkAssistantAgent] = None


def get_config() -> AgenticConfig:
    """Get the global configuration."""
    return AgenticConfig()


def get_assistant() -> FrameworkAssistantAgent:
    """Get or create the global assistant instance."""
    global _assistant
    if _assistant is None:
        _assistant = create_framework_assistant()
    return _assistant


def get_usage_tracker() -> UsageTracker:
    """Get the usage tracker."""
    return UsageTracker(get_config())


def get_meta_analyzer() -> MetaAnalyzer:
    """Get the meta analyzer."""
    return MetaAnalyzer(get_usage_tracker(), get_config())


# Request/Response Models

class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    message: str = Field(..., description="User message")
    include_rag: bool = Field(default=True, description="Include RAG context")
    session_id: Optional[str] = Field(default=None, description="Session ID for continuity")


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    response: str = Field(..., description="Assistant response")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CodeGenerationRequest(BaseModel):
    """Request for code generation."""
    request: str = Field(..., description="Code generation request")
    language: Optional[str] = Field(default=None, description="Target language")


class CodeReviewRequest(BaseModel):
    """Request for code review."""
    code: str = Field(..., description="Code to review")
    focus_areas: Optional[List[str]] = Field(default=None, description="Areas to focus on")
    language: Optional[str] = Field(default=None, description="Programming language")


class AssistantConfigResponse(BaseModel):
    """Assistant configuration response."""
    enabled: bool
    defaultFramework: str
    model: str
    enableCodingHelper: bool
    enableFrameworkGuide: bool
    enableMetaAnalysis: bool
    ragEnabled: bool
    memoryEnabled: bool
    codeKbProjectId: Optional[str]
    docsKbName: str
    usageTrackingEnabled: bool
    metaAnalysisIntervalHours: int
    maxContextMessages: int
    systemPrompt: Optional[str]


class AssistantConfigUpdate(BaseModel):
    """Assistant configuration update request."""
    enabled: Optional[bool] = None
    defaultFramework: Optional[str] = None
    model: Optional[str] = None
    enableCodingHelper: Optional[bool] = None
    enableFrameworkGuide: Optional[bool] = None
    enableMetaAnalysis: Optional[bool] = None
    ragEnabled: Optional[bool] = None
    memoryEnabled: Optional[bool] = None
    codeKbProjectId: Optional[str] = None
    docsKbName: Optional[str] = None
    usageTrackingEnabled: Optional[bool] = None
    metaAnalysisIntervalHours: Optional[int] = None
    maxContextMessages: Optional[int] = None
    systemPrompt: Optional[str] = None


class AnalyticsResponse(BaseModel):
    """Usage analytics response."""
    periodStart: str
    periodEnd: str
    totalEvents: int
    totalAgentRuns: int
    totalApiCalls: int
    totalRagQueries: int
    totalErrors: int
    frameworkStats: List[Dict[str, Any]]
    avgResponseTimeMs: float
    ragEffectivenessScore: float


class HealthResponse(BaseModel):
    """Health summary response."""
    healthScore: float
    status: str
    trends: Dict[str, str]
    totalEvents: int
    totalErrors: int
    errorRate: float
    topIssues: List[str]


class SuggestionResponse(BaseModel):
    """Suggestion response."""
    suggestions: List[Dict[str, Any]]


class MetaAnalysisResponse(BaseModel):
    """Meta-analysis response."""
    timestamp: str
    healthScore: float
    suggestionsCount: int
    summary: str


# Endpoints

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the Framework Assistant.
    
    Send a message and receive a response from the assistant.
    """
    try:
        assistant = get_assistant()
        
        if not assistant.config.assistant.enabled:
            raise HTTPException(status_code=503, detail="Assistant is disabled")
        
        response = assistant.chat(request.message, include_rag=request.include_rag)
        
        return ChatResponse(
            response=response,
            session_id=request.session_id,
            metadata={
                "model": assistant.config.assistant.model,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-code")
async def generate_code(request: CodeGenerationRequest):
    """Generate code based on a request."""
    try:
        assistant = get_assistant()
        
        if not assistant.config.assistant.enable_coding_helper:
            raise HTTPException(status_code=503, detail="Coding helper is disabled")
        
        code = assistant.generate_code(request.request, language=request.language)
        
        return {"code": code}
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review-code")
async def review_code(request: CodeReviewRequest):
    """Review code and provide feedback."""
    try:
        assistant = get_assistant()
        
        if not assistant.config.assistant.enable_coding_helper:
            raise HTTPException(status_code=503, detail="Coding helper is disabled")
        
        review = assistant.review_code(request.code)
        
        return review
    except Exception as e:
        logger.error(f"Code review failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/help")
async def get_help(question: str = Query(..., description="Help question")):
    """Get help with a framework question."""
    try:
        assistant = get_assistant()
        
        if not assistant.config.assistant.enable_framework_guide:
            raise HTTPException(status_code=503, detail="Framework guide is disabled")
        
        response = assistant.get_help(question)
        
        return {"response": response}
    except Exception as e:
        logger.error(f"Help request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=AssistantConfigResponse)
async def get_assistant_config():
    """Get the current assistant configuration."""
    config = get_config()
    assistant_config = config.assistant
    
    return AssistantConfigResponse(
        enabled=assistant_config.enabled,
        defaultFramework=assistant_config.default_framework,
        model=assistant_config.model,
        enableCodingHelper=assistant_config.enable_coding_helper,
        enableFrameworkGuide=assistant_config.enable_framework_guide,
        enableMetaAnalysis=assistant_config.enable_meta_analysis,
        ragEnabled=assistant_config.rag_enabled,
        memoryEnabled=assistant_config.memory_enabled,
        codeKbProjectId=assistant_config.code_kb_project_id,
        docsKbName=assistant_config.docs_kb_name,
        usageTrackingEnabled=assistant_config.usage_tracking_enabled,
        metaAnalysisIntervalHours=assistant_config.meta_analysis_interval_hours,
        maxContextMessages=assistant_config.max_context_messages,
        systemPrompt=assistant_config.system_prompt,
    )


@router.put("/config", response_model=AssistantConfigResponse)
async def update_assistant_config(update: AssistantConfigUpdate):
    """Update the assistant configuration."""
    # In a real implementation, this would persist to YAML
    # For now, we just acknowledge the update
    config = get_config()
    
    # Apply updates to the in-memory config
    # Note: This doesn't persist - would need to save to YAML
    if update.enabled is not None:
        config.assistant._assistant.enabled = update.enabled
    # ... similar for other fields
    
    logger.info("Assistant configuration updated")
    
    return await get_assistant_config()


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(days: int = Query(default=7, ge=1, le=90)):
    """Get usage analytics for the specified number of days."""
    try:
        tracker = get_usage_tracker()
        analytics = tracker.get_analytics(days=days)
        
        return AnalyticsResponse(
            periodStart=analytics.period_start.isoformat(),
            periodEnd=analytics.period_end.isoformat(),
            totalEvents=analytics.total_events,
            totalAgentRuns=analytics.total_agent_runs,
            totalApiCalls=analytics.total_api_calls,
            totalRagQueries=analytics.total_rag_queries,
            totalErrors=analytics.total_errors,
            frameworkStats=[s.model_dump() for s in analytics.framework_stats],
            avgResponseTimeMs=analytics.avg_response_time_ms,
            ragEffectivenessScore=analytics.rag_effectiveness_score,
        )
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Get the framework health summary."""
    try:
        assistant = get_assistant()
        
        if not assistant.config.assistant.enable_meta_analysis:
            return HealthResponse(
                healthScore=0,
                status="meta_analysis_disabled",
                trends={},
                totalEvents=0,
                totalErrors=0,
                errorRate=0,
                topIssues=[],
            )
        
        health = assistant.get_health_summary()
        
        return HealthResponse(
            healthScore=health.get("health_score", 0),
            status=health.get("status", "unknown"),
            trends=health.get("trends", {}),
            totalEvents=health.get("total_events", 0),
            totalErrors=health.get("total_errors", 0),
            errorRate=health.get("error_rate", 0),
            topIssues=health.get("top_issues", []),
        )
    except Exception as e:
        logger.error(f"Failed to get health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions", response_model=SuggestionResponse)
async def get_suggestions(
    category: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
):
    """Get improvement suggestions from meta-analysis."""
    try:
        assistant = get_assistant()
        
        if not assistant.config.assistant.enable_meta_analysis:
            return SuggestionResponse(suggestions=[])
        
        suggestions = assistant.get_improvement_suggestions()
        
        # Apply filters
        if category:
            suggestions = [s for s in suggestions if s.get("category") == category]
        if priority:
            suggestions = [s for s in suggestions if s.get("priority") == priority]
        
        return SuggestionResponse(suggestions=suggestions[:limit])
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=MetaAnalysisResponse)
async def run_meta_analysis(days: int = Query(default=7, ge=1, le=90)):
    """Run a meta-analysis and generate suggestions."""
    try:
        analyzer = get_meta_analyzer()
        report = analyzer.run_analysis(days=days)
        
        return MetaAnalysisResponse(
            timestamp=report.generated_at.isoformat(),
            healthScore=report.health_score,
            suggestionsCount=len(report.suggestions),
            summary=report.summary,
        )
    except Exception as e:
        logger.error(f"Meta-analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_conversation():
    """Reset the assistant conversation history."""
    try:
        assistant = get_assistant()
        assistant.reset_conversation()
        return {"status": "ok", "message": "Conversation reset"}
    except Exception as e:
        logger.error(f"Reset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session")
async def get_session_info():
    """Get information about the current session."""
    try:
        assistant = get_assistant()
        return assistant.get_session_info()
    except Exception as e:
        logger.error(f"Failed to get session info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_connection():
    """Test the assistant connection."""
    try:
        assistant = get_assistant()
        
        # Simple test - check if we can access the config
        if assistant.config.assistant.enabled:
            return {"status": "ok", "model": assistant.config.assistant.model}
        else:
            return {"status": "disabled"}
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
