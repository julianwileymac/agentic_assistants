"""
Meta Analyzer Module for the Framework Assistant.

This module analyzes usage patterns and generates improvement suggestions
using both the observability system and LLM-based analysis.

Example:
    >>> module = MetaAnalyzerModule(config, usage_tracker)
    >>> insights = module.analyze_and_suggest()
    >>> suggestions = module.get_suggestions()
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

if TYPE_CHECKING:
    from agentic_assistants.observability import MetaAnalyzer, UsageTracker

logger = get_logger(__name__)


class MetaAnalyzerModule:
    """
    Provides meta-analysis capabilities for framework improvement.
    
    This module:
    - Analyzes usage patterns from the observability system
    - Uses LLM to generate improvement insights
    - Prioritizes suggestions by impact
    - Tracks suggestion implementation
    
    Attributes:
        config: Framework configuration
        usage_tracker: Usage tracker for data
        meta_analyzer: Meta analyzer for pattern analysis
    """
    
    DEFAULT_ANALYSIS_PROMPT = """You are an expert at analyzing software usage patterns and suggesting improvements.
Given the following usage data and metrics, provide actionable suggestions for improving the framework.
Focus on:
- Performance optimizations
- Reliability improvements
- User experience enhancements
- Feature adoption
- Error prevention

Be specific and practical in your suggestions."""

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        usage_tracker: Optional["UsageTracker"] = None,
        meta_analyzer: Optional["MetaAnalyzer"] = None,
    ):
        """
        Initialize the meta analyzer module.
        
        Args:
            config: Configuration instance
            usage_tracker: Usage tracker for data
            meta_analyzer: Meta analyzer for pattern analysis
        """
        self.config = config or AgenticConfig()
        self._usage_tracker = usage_tracker
        self._meta_analyzer = meta_analyzer
        self._cached_analysis: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration = timedelta(hours=1)
    
    @property
    def usage_tracker(self) -> Optional["UsageTracker"]:
        """Get the usage tracker."""
        if self._usage_tracker is None:
            try:
                from agentic_assistants.observability import UsageTracker
                self._usage_tracker = UsageTracker(self.config)
            except ImportError:
                pass
        return self._usage_tracker
    
    @property
    def meta_analyzer(self) -> Optional["MetaAnalyzer"]:
        """Get the meta analyzer."""
        if self._meta_analyzer is None and self.usage_tracker is not None:
            try:
                from agentic_assistants.observability import MetaAnalyzer
                self._meta_analyzer = MetaAnalyzer(self.usage_tracker, self.config)
            except ImportError:
                pass
        return self._meta_analyzer
    
    def _get_model(self) -> str:
        """Get the model to use."""
        return self.config.assistant.model or self.config.ollama.default_model
    
    def _call_llm(
        self,
        prompt: str,
        system_message: Optional[str] = None,
    ) -> str:
        """Make an LLM call."""
        import httpx
        
        system = system_message or self.DEFAULT_ANALYSIS_PROMPT
        
        response = httpx.post(
            f"{self.config.ollama.host}/api/chat",
            json={
                "model": self._get_model(),
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "options": {"temperature": 0.3},
            },
            timeout=self.config.ollama.timeout,
        )
        response.raise_for_status()
        
        return response.json().get("message", {}).get("content", "")
    
    def analyze_and_suggest(
        self,
        days: int = 7,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Run analysis and generate suggestions.
        
        Args:
            days: Number of days to analyze
            force_refresh: Force refresh of cached analysis
            
        Returns:
            Analysis results with suggestions
        """
        # Check cache
        if (
            not force_refresh
            and self._cached_analysis
            and self._cache_timestamp
            and datetime.utcnow() - self._cache_timestamp < self._cache_duration
        ):
            return self._cached_analysis
        
        results: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_period_days": days,
            "analytics": None,
            "pattern_suggestions": [],
            "llm_insights": None,
            "priority_actions": [],
        }
        
        # Get base analytics from meta analyzer
        if self.meta_analyzer:
            try:
                report = self.meta_analyzer.run_analysis(days)
                results["analytics"] = report.analytics.model_dump() if report.analytics else None
                results["pattern_suggestions"] = [
                    s.model_dump() for s in report.suggestions
                ]
                results["health_score"] = report.health_score
                results["trends"] = report.trends
            except Exception as e:
                logger.error(f"Failed to run meta analysis: {e}")
        
        # Generate LLM-based insights
        if results.get("analytics"):
            try:
                llm_insights = self._generate_llm_insights(results)
                results["llm_insights"] = llm_insights
            except Exception as e:
                logger.warning(f"Failed to generate LLM insights: {e}")
        
        # Combine and prioritize actions
        results["priority_actions"] = self._prioritize_actions(results)
        
        # Cache results
        self._cached_analysis = results
        self._cache_timestamp = datetime.utcnow()
        
        return results
    
    def _generate_llm_insights(self, analysis: Dict[str, Any]) -> str:
        """Generate LLM-based insights from analysis data."""
        analytics = analysis.get("analytics", {})
        suggestions = analysis.get("pattern_suggestions", [])
        
        prompt = f"""Analyze the following framework usage data and provide insights:

## Usage Statistics (Last {analysis.get('analysis_period_days', 7)} Days)
- Total Events: {analytics.get('total_events', 0)}
- Agent Runs: {analytics.get('total_agent_runs', 0)}
- API Calls: {analytics.get('total_api_calls', 0)}
- RAG Queries: {analytics.get('total_rag_queries', 0)}
- Errors: {analytics.get('total_errors', 0)}
- Average API Response Time: {analytics.get('avg_response_time_ms', 0):.0f}ms
- RAG Effectiveness Score: {analytics.get('rag_effectiveness_score', 0):.2f}

## Framework Usage
{self._format_framework_stats(analytics.get('framework_stats', []))}

## Pattern-Based Suggestions
{self._format_suggestions(suggestions)}

## Health Score
{analysis.get('health_score', 'N/A')}

## Trends
{analysis.get('trends', {})}

Based on this data, provide:
1. Key insights about framework usage
2. Areas that need immediate attention
3. Opportunities for improvement
4. Recommendations for the development team
5. Predicted impact if suggestions are implemented"""

        return self._call_llm(prompt)
    
    def _format_framework_stats(self, stats: List[Dict]) -> str:
        """Format framework stats for the prompt."""
        if not stats:
            return "No framework usage data available."
        
        lines = []
        for s in stats:
            framework = s.get("framework", "unknown")
            total = s.get("total_runs", 0)
            success = s.get("successful_runs", 0)
            avg_duration = s.get("avg_duration_seconds", 0)
            error_rate = s.get("error_rate", 0)
            
            lines.append(
                f"- {framework}: {total} runs, {success} successful, "
                f"{error_rate*100:.1f}% error rate, {avg_duration:.1f}s avg duration"
            )
        
        return "\n".join(lines)
    
    def _format_suggestions(self, suggestions: List[Dict]) -> str:
        """Format suggestions for the prompt."""
        if not suggestions:
            return "No pattern-based suggestions generated."
        
        lines = []
        for s in suggestions[:5]:  # Top 5
            priority = s.get("priority", "medium")
            title = s.get("title", "")
            category = s.get("category", "")
            lines.append(f"- [{priority.upper()}] ({category}) {title}")
        
        return "\n".join(lines)
    
    def _prioritize_actions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize actions from analysis."""
        actions = []
        
        # Extract from pattern suggestions
        for s in analysis.get("pattern_suggestions", []):
            actions.append({
                "source": "pattern_analysis",
                "priority": s.get("priority", "medium"),
                "action": s.get("recommended_action", s.get("title", "")),
                "category": s.get("category", ""),
                "impact": s.get("estimated_impact", ""),
            })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        actions.sort(key=lambda a: priority_order.get(a.get("priority", "medium"), 2))
        
        return actions[:10]  # Top 10 actions
    
    def get_suggestions(
        self,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get filtered suggestions.
        
        Args:
            category: Filter by category
            priority: Filter by priority
            limit: Maximum suggestions to return
            
        Returns:
            List of suggestions
        """
        analysis = self.analyze_and_suggest()
        suggestions = analysis.get("pattern_suggestions", [])
        
        # Apply filters
        if category:
            suggestions = [s for s in suggestions if s.get("category") == category]
        
        if priority:
            suggestions = [s for s in suggestions if s.get("priority") == priority]
        
        return suggestions[:limit]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get a health summary of the framework.
        
        Returns:
            Health summary with score and status
        """
        analysis = self.analyze_and_suggest()
        
        health_score = analysis.get("health_score", 50)
        trends = analysis.get("trends", {})
        analytics = analysis.get("analytics", {})
        
        # Determine overall status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 70:
            status = "good"
        elif health_score >= 50:
            status = "fair"
        else:
            status = "needs_attention"
        
        return {
            "health_score": health_score,
            "status": status,
            "trends": trends,
            "total_events": analytics.get("total_events", 0),
            "total_errors": analytics.get("total_errors", 0),
            "error_rate": (
                analytics.get("total_errors", 0) / max(analytics.get("total_agent_runs", 1), 1)
            ),
            "top_issues": [
                s.get("title") for s in analysis.get("pattern_suggestions", [])[:3]
            ],
        }
    
    def explain_suggestion(
        self,
        suggestion_id: str,
    ) -> str:
        """
        Get a detailed explanation of a suggestion.
        
        Args:
            suggestion_id: The suggestion ID
            
        Returns:
            Detailed explanation
        """
        analysis = self.analyze_and_suggest()
        
        # Find the suggestion
        suggestion = None
        for s in analysis.get("pattern_suggestions", []):
            if s.get("id") == suggestion_id:
                suggestion = s
                break
        
        if not suggestion:
            return "Suggestion not found."
        
        prompt = f"""Explain this framework improvement suggestion in detail:

Title: {suggestion.get('title')}
Category: {suggestion.get('category')}
Priority: {suggestion.get('priority')}
Description: {suggestion.get('description')}
Evidence: {suggestion.get('evidence', [])}
Recommended Action: {suggestion.get('recommended_action')}
Estimated Impact: {suggestion.get('estimated_impact')}

Provide:
1. Why this is important
2. How to implement the suggested change
3. Expected benefits
4. Potential risks or trade-offs
5. Step-by-step implementation guide"""

        return self._call_llm(prompt)
    
    def generate_improvement_plan(
        self,
        focus_areas: Optional[List[str]] = None,
    ) -> str:
        """
        Generate a comprehensive improvement plan.
        
        Args:
            focus_areas: Specific areas to focus on
            
        Returns:
            Improvement plan
        """
        analysis = self.analyze_and_suggest()
        
        focus = focus_areas or ["performance", "reliability", "feature_adoption"]
        
        prompt = f"""Based on the following framework analysis, create a comprehensive improvement plan:

## Current Health Score: {analysis.get('health_score', 'N/A')}

## Current Trends
{analysis.get('trends', {})}

## Top Suggestions
{self._format_suggestions(analysis.get('pattern_suggestions', [])[:10])}

## Focus Areas
{', '.join(focus)}

Create an improvement plan that includes:
1. Executive Summary
2. Priority Items (next 2 weeks)
3. Short-term Goals (next month)
4. Medium-term Goals (next quarter)
5. Key Metrics to Track
6. Resource Requirements
7. Risk Mitigation Strategies"""

        return self._call_llm(prompt)
    
    def track_suggestion_implementation(
        self,
        suggestion_id: str,
        implemented: bool,
        notes: Optional[str] = None,
    ) -> bool:
        """
        Track the implementation of a suggestion.
        
        Args:
            suggestion_id: The suggestion ID
            implemented: Whether it was implemented
            notes: Implementation notes
            
        Returns:
            True if tracked successfully
        """
        # Track configuration change
        if self.usage_tracker:
            self.usage_tracker.track_config_change(
                config_section="meta_analysis",
                setting_name=f"suggestion_{suggestion_id}",
                new_value="implemented" if implemented else "dismissed",
                old_value="pending",
                changed_by="meta_analyzer_module",
                metadata={"notes": notes} if notes else {},
            )
            return True
        return False
    
    def invalidate_cache(self) -> None:
        """Invalidate the analysis cache."""
        self._cached_analysis = None
        self._cache_timestamp = None
