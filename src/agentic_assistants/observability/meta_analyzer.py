"""
Meta-analyzer for generating framework improvement suggestions.

This module analyzes usage patterns from the UsageTracker and generates
actionable suggestions for improving the framework.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.observability.models import (
    EventType,
    Framework,
    FrameworkUsageStats,
    MetaAnalysisReport,
    MetaAnalysisSuggestion,
    SuggestionCategory,
    SuggestionPriority,
    UsageAnalytics,
)
from agentic_assistants.observability.usage_tracker import UsageTracker
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class MetaAnalyzer:
    """
    Analyzes framework usage patterns and generates improvement suggestions.
    
    This class examines:
    - Error patterns and failure modes
    - Performance bottlenecks
    - Underutilized features
    - Configuration optimizations
    - Workflow improvements
    
    Example:
        >>> tracker = UsageTracker()
        >>> analyzer = MetaAnalyzer(tracker)
        >>> report = analyzer.run_analysis(days=7)
        >>> for suggestion in report.suggestions:
        ...     print(f"{suggestion.priority}: {suggestion.title}")
    """
    
    # Thresholds for generating suggestions
    ERROR_RATE_THRESHOLD = 0.1  # 10% error rate triggers suggestion
    SLOW_DURATION_THRESHOLD = 30.0  # Seconds - flag slow agent runs
    LOW_RAG_SCORE_THRESHOLD = 0.5  # RAG effectiveness threshold
    UNDERUTILIZED_THRESHOLD = 0.05  # 5% usage for underutilized features
    
    def __init__(
        self,
        tracker: Optional[UsageTracker] = None,
        config: Optional[AgenticConfig] = None,
    ):
        """
        Initialize the meta-analyzer.
        
        Args:
            tracker: Usage tracker instance
            config: Configuration instance
        """
        self.config = config or AgenticConfig()
        self.tracker = tracker or UsageTracker(self.config)
    
    def run_analysis(self, days: int = 7) -> MetaAnalysisReport:
        """
        Run a complete meta-analysis and generate a report.
        
        Args:
            days: Number of days of data to analyze
            
        Returns:
            Complete meta-analysis report with suggestions
        """
        logger.info(f"Running meta-analysis for the past {days} days")
        
        # Get analytics
        analytics = self.tracker.get_analytics(days=days)
        
        # Generate suggestions from different analyzers
        suggestions: List[MetaAnalysisSuggestion] = []
        
        suggestions.extend(self._analyze_error_patterns(analytics, days))
        suggestions.extend(self._analyze_performance(analytics, days))
        suggestions.extend(self._analyze_rag_effectiveness(analytics, days))
        suggestions.extend(self._analyze_framework_usage(analytics))
        suggestions.extend(self._analyze_configuration(analytics, days))
        suggestions.extend(self._analyze_feature_adoption(analytics, days))
        
        # Sort by priority
        priority_order = {
            SuggestionPriority.CRITICAL: 0,
            SuggestionPriority.HIGH: 1,
            SuggestionPriority.MEDIUM: 2,
            SuggestionPriority.LOW: 3,
        }
        suggestions.sort(key=lambda s: priority_order.get(s.priority, 4))
        
        # Calculate health score
        health_score = self._calculate_health_score(analytics, suggestions)
        
        # Determine trends
        trends = self._determine_trends(analytics, days)
        
        # Generate summary
        summary = self._generate_summary(analytics, suggestions, health_score)
        
        report = MetaAnalysisReport(
            id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            analysis_period_days=days,
            analytics=analytics,
            suggestions=suggestions,
            health_score=health_score,
            trends=trends,
            summary=summary,
        )
        
        logger.info(
            f"Meta-analysis complete: {len(suggestions)} suggestions, "
            f"health score: {health_score:.1f}"
        )
        
        return report
    
    def _analyze_error_patterns(
        self,
        analytics: UsageAnalytics,
        days: int,
    ) -> List[MetaAnalysisSuggestion]:
        """Analyze error patterns and generate suggestions."""
        suggestions = []
        
        # Check overall error rate
        if analytics.total_agent_runs > 0:
            for stats in analytics.framework_stats:
                if stats.error_rate > self.ERROR_RATE_THRESHOLD:
                    suggestions.append(MetaAnalysisSuggestion(
                        id=str(uuid.uuid4()),
                        category=SuggestionCategory.RELIABILITY,
                        priority=SuggestionPriority.HIGH if stats.error_rate > 0.2 else SuggestionPriority.MEDIUM,
                        title=f"High error rate in {stats.framework} framework",
                        description=(
                            f"The {stats.framework} framework has a {stats.error_rate*100:.1f}% error rate "
                            f"over the past {days} days. This is above the threshold of "
                            f"{self.ERROR_RATE_THRESHOLD*100:.0f}%."
                        ),
                        evidence=[
                            f"Total runs: {stats.total_runs}",
                            f"Failed runs: {stats.failed_runs}",
                            f"Common errors: {', '.join(stats.common_error_types[:3]) if stats.common_error_types else 'N/A'}",
                        ],
                        recommended_action=(
                            f"Review the error logs for {stats.framework} runs and address the most common "
                            f"error types. Consider adding better error handling or adjusting configurations."
                        ),
                        estimated_impact="Could reduce failed runs by 50-80%",
                        affected_components=[stats.framework, "error_handling"],
                    ))
        
        # Check for recurring specific errors
        errors = self.tracker.get_events(
            event_type=EventType.ERROR.value,
            start_time=datetime.utcnow() - timedelta(days=days),
            limit=1000,
        )
        
        error_counts: Dict[str, int] = {}
        for error in errors:
            error_type = error.get("error_type", "unknown")
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        for error_type, count in error_counts.items():
            if count >= 10:  # Recurring error threshold
                suggestions.append(MetaAnalysisSuggestion(
                    id=str(uuid.uuid4()),
                    category=SuggestionCategory.ERROR_PREVENTION,
                    priority=SuggestionPriority.HIGH if count >= 50 else SuggestionPriority.MEDIUM,
                    title=f"Recurring error: {error_type[:50]}",
                    description=(
                        f"The error '{error_type}' has occurred {count} times in the past {days} days. "
                        f"This indicates a systematic issue that should be addressed."
                    ),
                    evidence=[f"Occurrences: {count}"],
                    recommended_action=(
                        "Investigate the root cause of this error and implement a fix. "
                        "Consider adding validation or guards to prevent this error."
                    ),
                    estimated_impact=f"Could prevent {count} errors per week",
                    affected_components=["error_handling"],
                ))
        
        return suggestions
    
    def _analyze_performance(
        self,
        analytics: UsageAnalytics,
        days: int,
    ) -> List[MetaAnalysisSuggestion]:
        """Analyze performance and generate suggestions."""
        suggestions = []
        
        # Check for slow frameworks
        for stats in analytics.framework_stats:
            if stats.avg_duration_seconds > self.SLOW_DURATION_THRESHOLD:
                suggestions.append(MetaAnalysisSuggestion(
                    id=str(uuid.uuid4()),
                    category=SuggestionCategory.PERFORMANCE,
                    priority=SuggestionPriority.MEDIUM,
                    title=f"Slow average execution time in {stats.framework}",
                    description=(
                        f"The average execution time for {stats.framework} is "
                        f"{stats.avg_duration_seconds:.1f} seconds, which is above the "
                        f"threshold of {self.SLOW_DURATION_THRESHOLD} seconds."
                    ),
                    evidence=[
                        f"Average duration: {stats.avg_duration_seconds:.1f}s",
                        f"Total duration: {stats.total_duration_seconds:.1f}s",
                        f"Total runs: {stats.total_runs}",
                    ],
                    recommended_action=(
                        "Consider optimizing the agent workflows, using smaller models for "
                        "simple tasks, or implementing caching for repeated queries."
                    ),
                    estimated_impact="Could reduce average execution time by 20-40%",
                    affected_components=[stats.framework, "performance"],
                ))
        
        # Check API response times
        if analytics.avg_response_time_ms > 1000:  # Over 1 second
            suggestions.append(MetaAnalysisSuggestion(
                id=str(uuid.uuid4()),
                category=SuggestionCategory.PERFORMANCE,
                priority=SuggestionPriority.MEDIUM,
                title="Slow API response times",
                description=(
                    f"The average API response time is {analytics.avg_response_time_ms:.0f}ms, "
                    f"which may impact user experience."
                ),
                evidence=[f"Average response time: {analytics.avg_response_time_ms:.0f}ms"],
                recommended_action=(
                    "Review the slowest API endpoints and optimize them. Consider "
                    "implementing caching, async processing, or database query optimization."
                ),
                estimated_impact="Could improve response times by 30-50%",
                affected_components=["api", "performance"],
            ))
        
        return suggestions
    
    def _analyze_rag_effectiveness(
        self,
        analytics: UsageAnalytics,
        days: int,
    ) -> List[MetaAnalysisSuggestion]:
        """Analyze RAG query effectiveness."""
        suggestions = []
        
        if analytics.rag_effectiveness_score > 0:
            if analytics.rag_effectiveness_score < self.LOW_RAG_SCORE_THRESHOLD:
                suggestions.append(MetaAnalysisSuggestion(
                    id=str(uuid.uuid4()),
                    category=SuggestionCategory.RELIABILITY,
                    priority=SuggestionPriority.HIGH,
                    title="Low RAG retrieval effectiveness",
                    description=(
                        f"The average RAG relevance score is {analytics.rag_effectiveness_score:.2f}, "
                        f"which is below the threshold of {self.LOW_RAG_SCORE_THRESHOLD}. "
                        f"This means retrieved documents may not be highly relevant to queries."
                    ),
                    evidence=[
                        f"Average relevance score: {analytics.rag_effectiveness_score:.2f}",
                        f"Total RAG queries: {analytics.total_rag_queries}",
                    ],
                    recommended_action=(
                        "Review and improve the knowledge base content. Consider re-indexing "
                        "with better chunking strategies, updating embedding models, or "
                        "adding more relevant documents to the knowledge base."
                    ),
                    estimated_impact="Could improve answer accuracy by 30-50%",
                    affected_components=["rag", "knowledge_base", "embeddings"],
                ))
        
        return suggestions
    
    def _analyze_framework_usage(
        self,
        analytics: UsageAnalytics,
    ) -> List[MetaAnalysisSuggestion]:
        """Analyze framework usage distribution."""
        suggestions = []
        
        if len(analytics.framework_stats) > 1:
            # Find the most reliable framework
            best_framework = min(
                analytics.framework_stats,
                key=lambda s: s.error_rate if s.total_runs > 0 else 1.0,
            )
            
            for stats in analytics.framework_stats:
                if (
                    stats.framework != best_framework.framework
                    and stats.error_rate > best_framework.error_rate + 0.1
                    and stats.total_runs >= 10
                ):
                    suggestions.append(MetaAnalysisSuggestion(
                        id=str(uuid.uuid4()),
                        category=SuggestionCategory.WORKFLOW_IMPROVEMENT,
                        priority=SuggestionPriority.LOW,
                        title=f"Consider using {best_framework.framework} more",
                        description=(
                            f"{best_framework.framework} has a lower error rate "
                            f"({best_framework.error_rate*100:.1f}%) compared to "
                            f"{stats.framework} ({stats.error_rate*100:.1f}%). "
                            f"Consider migrating some workloads."
                        ),
                        evidence=[
                            f"{best_framework.framework} error rate: {best_framework.error_rate*100:.1f}%",
                            f"{stats.framework} error rate: {stats.error_rate*100:.1f}%",
                        ],
                        recommended_action=(
                            f"Evaluate whether tasks currently using {stats.framework} "
                            f"could be migrated to {best_framework.framework} for better reliability."
                        ),
                        estimated_impact="Could improve overall reliability",
                        affected_components=[stats.framework, best_framework.framework],
                    ))
        
        return suggestions
    
    def _analyze_configuration(
        self,
        analytics: UsageAnalytics,
        days: int,
    ) -> List[MetaAnalysisSuggestion]:
        """Analyze configuration and suggest optimizations."""
        suggestions = []
        
        # Check for unused features based on event types
        if analytics.total_rag_queries == 0 and analytics.total_agent_runs > 10:
            suggestions.append(MetaAnalysisSuggestion(
                id=str(uuid.uuid4()),
                category=SuggestionCategory.FEATURE_ADOPTION,
                priority=SuggestionPriority.LOW,
                title="RAG not being used",
                description=(
                    "No RAG queries have been made in the past {days} days, "
                    "but agents are being run. RAG can significantly improve "
                    "agent responses by providing relevant context."
                ),
                evidence=[
                    f"RAG queries: {analytics.total_rag_queries}",
                    f"Agent runs: {analytics.total_agent_runs}",
                ],
                recommended_action=(
                    "Consider enabling RAG for your agents to provide them with "
                    "relevant context from your knowledge bases."
                ),
                estimated_impact="Could improve response quality by 20-40%",
                affected_components=["rag", "agents"],
            ))
        
        return suggestions
    
    def _analyze_feature_adoption(
        self,
        analytics: UsageAnalytics,
        days: int,
    ) -> List[MetaAnalysisSuggestion]:
        """Analyze feature adoption patterns."""
        suggestions = []
        
        # This would be expanded with more feature-specific analysis
        # For now, check basic patterns
        
        if analytics.total_events > 0:
            agent_ratio = analytics.total_agent_runs / analytics.total_events
            
            if agent_ratio < 0.1 and analytics.total_events > 100:
                suggestions.append(MetaAnalysisSuggestion(
                    id=str(uuid.uuid4()),
                    category=SuggestionCategory.FEATURE_ADOPTION,
                    priority=SuggestionPriority.LOW,
                    title="Low agent utilization",
                    description=(
                        f"Only {agent_ratio*100:.1f}% of framework activity involves agent runs. "
                        f"Agents are the core feature of the framework."
                    ),
                    evidence=[
                        f"Agent runs: {analytics.total_agent_runs}",
                        f"Total events: {analytics.total_events}",
                    ],
                    recommended_action=(
                        "Explore creating agents for your common tasks. "
                        "Check the documentation for getting started with agents."
                    ),
                    estimated_impact="Could automate more workflows",
                    affected_components=["agents"],
                ))
        
        return suggestions
    
    def _calculate_health_score(
        self,
        analytics: UsageAnalytics,
        suggestions: List[MetaAnalysisSuggestion],
    ) -> float:
        """
        Calculate an overall health score for the framework.
        
        Score is 0-100, with 100 being perfect health.
        """
        score = 100.0
        
        # Deduct for high error rates
        for stats in analytics.framework_stats:
            if stats.error_rate > 0.1:
                score -= min(20, stats.error_rate * 100)
        
        # Deduct for low RAG effectiveness
        if analytics.rag_effectiveness_score > 0 and analytics.rag_effectiveness_score < 0.5:
            score -= (0.5 - analytics.rag_effectiveness_score) * 20
        
        # Deduct for critical/high priority suggestions
        critical_count = sum(1 for s in suggestions if s.priority == SuggestionPriority.CRITICAL)
        high_count = sum(1 for s in suggestions if s.priority == SuggestionPriority.HIGH)
        
        score -= critical_count * 15
        score -= high_count * 5
        
        # Deduct for high error count
        if analytics.total_errors > analytics.total_agent_runs * 0.2:
            score -= 10
        
        return max(0, min(100, score))
    
    def _determine_trends(
        self,
        analytics: UsageAnalytics,
        days: int,
    ) -> Dict[str, str]:
        """Determine trends in various metrics."""
        # This would ideally compare current period to previous period
        # For now, return basic indicators
        
        trends = {}
        
        # Activity trend
        if analytics.total_events > days * 10:
            trends["activity"] = "active"
        elif analytics.total_events > days * 2:
            trends["activity"] = "moderate"
        else:
            trends["activity"] = "low"
        
        # Error trend
        error_rate = analytics.total_errors / max(1, analytics.total_agent_runs)
        if error_rate < 0.05:
            trends["errors"] = "healthy"
        elif error_rate < 0.15:
            trends["errors"] = "moderate"
        else:
            trends["errors"] = "concerning"
        
        # RAG usage trend
        if analytics.total_rag_queries > analytics.total_agent_runs * 0.5:
            trends["rag_usage"] = "high"
        elif analytics.total_rag_queries > 0:
            trends["rag_usage"] = "moderate"
        else:
            trends["rag_usage"] = "unused"
        
        return trends
    
    def _generate_summary(
        self,
        analytics: UsageAnalytics,
        suggestions: List[MetaAnalysisSuggestion],
        health_score: float,
    ) -> str:
        """Generate a natural language summary of the analysis."""
        critical = sum(1 for s in suggestions if s.priority == SuggestionPriority.CRITICAL)
        high = sum(1 for s in suggestions if s.priority == SuggestionPriority.HIGH)
        
        # Build summary
        parts = []
        
        # Health assessment
        if health_score >= 90:
            parts.append("The framework is in excellent health.")
        elif health_score >= 70:
            parts.append("The framework is in good health with some areas for improvement.")
        elif health_score >= 50:
            parts.append("The framework has several areas that need attention.")
        else:
            parts.append("The framework requires immediate attention to address critical issues.")
        
        # Activity summary
        parts.append(
            f"Over the analysis period, there were {analytics.total_agent_runs} agent runs "
            f"and {analytics.total_api_calls} API calls."
        )
        
        # Issues summary
        if critical > 0 or high > 0:
            issue_parts = []
            if critical > 0:
                issue_parts.append(f"{critical} critical")
            if high > 0:
                issue_parts.append(f"{high} high-priority")
            parts.append(f"There are {' and '.join(issue_parts)} issues to address.")
        else:
            parts.append("No critical issues were found.")
        
        # Framework performance
        if analytics.framework_stats:
            best = min(analytics.framework_stats, key=lambda s: s.error_rate if s.total_runs > 0 else 1)
            if best.total_runs > 0:
                parts.append(
                    f"The most reliable framework is {best.framework} with a "
                    f"{(1-best.error_rate)*100:.0f}% success rate."
                )
        
        return " ".join(parts)
    
    def generate_suggestions(self, days: int = 7) -> List[MetaAnalysisSuggestion]:
        """
        Generate suggestions without a full report.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of suggestions
        """
        report = self.run_analysis(days)
        return report.suggestions
