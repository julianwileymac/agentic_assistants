"""
Usage tracker for monitoring framework interactions.

This module provides the UsageTracker class for recording and querying
usage events across the framework.
"""

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

from agentic_assistants.config import AgenticConfig
from agentic_assistants.observability.models import (
    AgentRunEvent,
    APICallEvent,
    ConfigChangeEvent,
    ErrorEvent,
    EventType,
    Framework,
    FrameworkUsageStats,
    MemoryAccessEvent,
    ModelInferenceEvent,
    RAGQueryEvent,
    UsageAnalytics,
    UsageEvent,
    UserInteractionEvent,
)
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=UsageEvent)


class UsageTracker:
    """
    Track and store usage events for the framework.
    
    This class provides methods to:
    - Record various types of usage events
    - Query historical usage data
    - Generate usage statistics and analytics
    
    Events are stored in a SQLite database for persistence and
    efficient querying.
    
    Example:
        >>> tracker = UsageTracker()
        >>> tracker.track_agent_run(
        ...     agent_name="researcher",
        ...     framework="crewai",
        ...     model="llama3.2",
        ...     duration_seconds=15.5,
        ...     success=True,
        ... )
        >>> stats = tracker.get_framework_stats("crewai")
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        db_path: Optional[Path] = None,
    ):
        """
        Initialize the usage tracker.
        
        Args:
            config: Configuration instance
            db_path: Path to the SQLite database (uses config default if None)
        """
        self.config = config or AgenticConfig()
        self.db_path = db_path or self.config.assistant.usage_db_path
        self._ensure_db()
    
    def _ensure_db(self) -> None:
        """Ensure the database and tables exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    project_id TEXT,
                    data JSON NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_type 
                ON usage_events(event_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_timestamp 
                ON usage_events(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_project 
                ON usage_events(project_id)
            """)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _generate_id(self) -> str:
        """Generate a unique event ID."""
        return str(uuid.uuid4())
    
    def track_event(self, event: UsageEvent) -> str:
        """
        Track a generic usage event.
        
        Args:
            event: The usage event to track
            
        Returns:
            The event ID
        """
        if event.id is None:
            event.id = self._generate_id()
        
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO usage_events 
                (id, event_type, timestamp, user_id, session_id, project_id, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.event_type,
                    event.timestamp.isoformat(),
                    event.user_id,
                    event.session_id,
                    event.project_id,
                    event.model_dump_json(),
                ),
            )
            conn.commit()
        
        logger.debug(f"Tracked event: {event.event_type} ({event.id})")
        return event.id
    
    def track_agent_run(
        self,
        agent_name: str,
        framework: str,
        model: str,
        duration_seconds: float,
        success: bool,
        agent_id: Optional[str] = None,
        error_message: Optional[str] = None,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
        task_type: Optional[str] = None,
        tools_used: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Track an agent run event.
        
        Args:
            agent_name: Name of the agent
            framework: Framework used (crewai, langgraph, etc.)
            model: LLM model used
            duration_seconds: Execution duration
            success: Whether the run succeeded
            agent_id: Optional agent ID
            error_message: Error message if failed
            tokens_input: Input tokens used
            tokens_output: Output tokens generated
            task_type: Type of task performed
            tools_used: List of tools used
            user_id: User ID
            session_id: Session ID
            project_id: Project ID
            metadata: Additional metadata
            
        Returns:
            The event ID
        """
        event = AgentRunEvent(
            agent_name=agent_name,
            agent_id=agent_id,
            framework=Framework(framework),
            model=model,
            duration_seconds=duration_seconds,
            success=success,
            error_message=error_message,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            task_type=task_type,
            tools_used=tools_used or [],
            user_id=user_id,
            session_id=session_id,
            project_id=project_id,
            metadata=metadata or {},
        )
        return self.track_event(event)
    
    def track_api_call(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
        success: bool,
        error_message: Optional[str] = None,
        request_size_bytes: Optional[int] = None,
        response_size_bytes: Optional[int] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Track an API call event."""
        event = APICallEvent(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
            request_size_bytes=request_size_bytes,
            response_size_bytes=response_size_bytes,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {},
        )
        return self.track_event(event)
    
    def track_rag_query(
        self,
        knowledge_base: str,
        query: str,
        num_results: int,
        duration_ms: float,
        top_score: Optional[float] = None,
        avg_score: Optional[float] = None,
        embedding_model: Optional[str] = None,
        used_for_generation: bool = False,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Track a RAG query event."""
        event = RAGQueryEvent(
            knowledge_base=knowledge_base,
            query=query,
            num_results=num_results,
            duration_ms=duration_ms,
            top_score=top_score,
            avg_score=avg_score,
            embedding_model=embedding_model,
            used_for_generation=used_for_generation,
            user_id=user_id,
            session_id=session_id,
            project_id=project_id,
            metadata=metadata or {},
        )
        return self.track_event(event)
    
    def track_model_inference(
        self,
        model: str,
        duration_ms: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        provider: str = "ollama",
        success: bool = True,
        error_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Track a model inference event."""
        event = ModelInferenceEvent(
            model=model,
            provider=provider,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
            temperature=temperature,
            max_tokens=max_tokens,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {},
        )
        return self.track_event(event)
    
    def track_error(
        self,
        error_type: str,
        error_message: str,
        component: str,
        stack_trace: Optional[str] = None,
        framework: Optional[str] = None,
        recoverable: bool = True,
        resolution: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Track an error event."""
        event = ErrorEvent(
            error_type=error_type,
            error_message=error_message,
            component=component,
            stack_trace=stack_trace,
            framework=Framework(framework) if framework else None,
            recoverable=recoverable,
            resolution=resolution,
            user_id=user_id,
            session_id=session_id,
            project_id=project_id,
            metadata=metadata or {},
        )
        return self.track_event(event)
    
    def track_user_interaction(
        self,
        interaction_type: str,
        feature_used: str,
        input_length: int = 0,
        response_length: int = 0,
        duration_ms: float = 0,
        satisfaction_score: Optional[int] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Track a user interaction event."""
        event = UserInteractionEvent(
            interaction_type=interaction_type,
            feature_used=feature_used,
            input_length=input_length,
            response_length=response_length,
            duration_ms=duration_ms,
            satisfaction_score=satisfaction_score,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {},
        )
        return self.track_event(event)
    
    def track_config_change(
        self,
        config_section: str,
        setting_name: str,
        new_value: str,
        old_value: Optional[str] = None,
        changed_by: str = "user",
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Track a configuration change event."""
        event = ConfigChangeEvent(
            config_section=config_section,
            setting_name=setting_name,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
            user_id=user_id,
            metadata=metadata or {},
        )
        return self.track_event(event)
    
    def get_events(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Query usage events with filters.
        
        Args:
            event_type: Filter by event type
            start_time: Filter events after this time
            end_time: Filter events before this time
            project_id: Filter by project
            user_id: Filter by user
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of event dictionaries
        """
        query = "SELECT * FROM usage_events WHERE 1=1"
        params = []
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        
        return [
            {**json.loads(row["data"]), "id": row["id"]}
            for row in rows
        ]
    
    def get_framework_stats(
        self,
        framework: str,
        days: int = 7,
    ) -> FrameworkUsageStats:
        """
        Get usage statistics for a specific framework.
        
        Args:
            framework: Framework name
            days: Number of days to analyze
            
        Returns:
            Framework usage statistics
        """
        start_time = datetime.utcnow() - timedelta(days=days)
        
        events = self.get_events(
            event_type=EventType.AGENT_RUN.value,
            start_time=start_time,
            limit=10000,
        )
        
        # Filter for the specific framework
        framework_events = [
            e for e in events 
            if e.get("framework") == framework
        ]
        
        if not framework_events:
            return FrameworkUsageStats(
                framework=Framework(framework),
                total_runs=0,
            )
        
        total_runs = len(framework_events)
        successful_runs = sum(1 for e in framework_events if e.get("success", False))
        failed_runs = total_runs - successful_runs
        total_duration = sum(e.get("duration_seconds", 0) for e in framework_events)
        total_tokens = sum(
            (e.get("tokens_input", 0) or 0) + (e.get("tokens_output", 0) or 0)
            for e in framework_events
        )
        
        # Get most used models
        model_counts: Dict[str, int] = {}
        for e in framework_events:
            model = e.get("model", "unknown")
            model_counts[model] = model_counts.get(model, 0) + 1
        most_used_models = sorted(model_counts.keys(), key=lambda m: model_counts[m], reverse=True)[:5]
        
        # Get common error types
        error_types: Dict[str, int] = {}
        for e in framework_events:
            if not e.get("success") and e.get("error_message"):
                error_type = e.get("error_message", "").split(":")[0][:50]
                error_types[error_type] = error_types.get(error_type, 0) + 1
        common_errors = sorted(error_types.keys(), key=lambda t: error_types[t], reverse=True)[:5]
        
        return FrameworkUsageStats(
            framework=Framework(framework),
            total_runs=total_runs,
            successful_runs=successful_runs,
            failed_runs=failed_runs,
            total_duration_seconds=total_duration,
            avg_duration_seconds=total_duration / total_runs if total_runs > 0 else 0,
            total_tokens=total_tokens,
            error_rate=failed_runs / total_runs if total_runs > 0 else 0,
            most_used_models=most_used_models,
            common_error_types=common_errors,
        )
    
    def get_analytics(
        self,
        days: int = 7,
        project_id: Optional[str] = None,
    ) -> UsageAnalytics:
        """
        Get aggregated usage analytics.
        
        Args:
            days: Number of days to analyze
            project_id: Optional project filter
            
        Returns:
            Aggregated usage analytics
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        # Get all events in the period
        events = self.get_events(
            start_time=start_time,
            end_time=end_time,
            project_id=project_id,
            limit=100000,
        )
        
        # Count by type
        agent_runs = [e for e in events if e.get("event_type") == EventType.AGENT_RUN.value]
        api_calls = [e for e in events if e.get("event_type") == EventType.API_CALL.value]
        rag_queries = [e for e in events if e.get("event_type") == EventType.RAG_QUERY.value]
        errors = [e for e in events if e.get("event_type") == EventType.ERROR.value]
        
        # Get framework stats for all frameworks
        frameworks = set(e.get("framework") for e in agent_runs if e.get("framework"))
        framework_stats = [
            self.get_framework_stats(fw, days) for fw in frameworks
        ]
        
        # Calculate average API response time
        api_durations = [e.get("duration_ms", 0) for e in api_calls]
        avg_response_time = sum(api_durations) / len(api_durations) if api_durations else 0
        
        # Calculate RAG effectiveness
        rag_scores = [e.get("avg_score", 0) for e in rag_queries if e.get("avg_score")]
        rag_effectiveness = sum(rag_scores) / len(rag_scores) if rag_scores else 0
        
        # Get most active projects
        project_counts: Dict[str, int] = {}
        for e in events:
            pid = e.get("project_id")
            if pid:
                project_counts[pid] = project_counts.get(pid, 0) + 1
        most_active = sorted(project_counts.keys(), key=lambda p: project_counts[p], reverse=True)[:5]
        
        # Get peak usage hours
        hour_counts: Dict[int, int] = {}
        for e in events:
            try:
                ts = datetime.fromisoformat(e.get("timestamp", ""))
                hour_counts[ts.hour] = hour_counts.get(ts.hour, 0) + 1
            except (ValueError, TypeError):
                pass
        peak_hours = sorted(hour_counts.keys(), key=lambda h: hour_counts[h], reverse=True)[:5]
        
        return UsageAnalytics(
            period_start=start_time,
            period_end=end_time,
            total_events=len(events),
            total_agent_runs=len(agent_runs),
            total_api_calls=len(api_calls),
            total_rag_queries=len(rag_queries),
            total_errors=len(errors),
            framework_stats=framework_stats,
            most_active_projects=most_active,
            peak_usage_hours=peak_hours,
            avg_response_time_ms=avg_response_time,
            rag_effectiveness_score=rag_effectiveness,
        )
    
    def get_event_count(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> int:
        """Get the count of events matching the filters."""
        query = "SELECT COUNT(*) FROM usage_events WHERE 1=1"
        params = []
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()[0]
    
    def cleanup_old_events(self, days_to_keep: int = 90) -> int:
        """
        Remove events older than the specified number of days.
        
        Args:
            days_to_keep: Number of days of events to keep
            
        Returns:
            Number of events deleted
        """
        cutoff = datetime.utcnow() - timedelta(days=days_to_keep)
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM usage_events WHERE timestamp < ?",
                (cutoff.isoformat(),),
            )
            deleted = cursor.rowcount
            conn.commit()
        
        logger.info(f"Cleaned up {deleted} old usage events")
        return deleted


# Global tracker instance
_tracker: Optional[UsageTracker] = None


def get_usage_tracker(config: Optional[AgenticConfig] = None) -> UsageTracker:
    """
    Get or create the global usage tracker instance.
    
    Args:
        config: Optional configuration instance
        
    Returns:
        The global UsageTracker instance
    """
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker(config)
    return _tracker
