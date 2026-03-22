"""
Log Analyzer Agent for AI-powered log analysis and correlation.

Ingests logs from multiple sources, detects patterns, and identifies anomalies.
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import Counter
import re
import json

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class LogEntry:
    """Parsed log entry."""
    entry_id: str
    timestamp: str
    source: str
    level: str  # debug, info, warning, error, critical
    message: str
    raw_log: str
    fields: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class LogPattern:
    """Detected log pattern."""
    pattern_id: str
    pattern_type: str
    frequency: int
    first_seen: str
    last_seen: str
    examples: List[str]
    severity: str
    description: str


@dataclass
class CorrelationResult:
    """Correlated log events."""
    correlation_id: str
    events: List[LogEntry]
    correlation_type: str
    confidence: float
    timeline: List[Tuple[str, str]]  # (timestamp, event_summary)
    potential_attack: bool
    description: str


class LogAnalyzerAgent:
    """
    AI-powered log analysis and correlation agent.
    
    Capabilities:
    - Multi-source log ingestion
    - Pattern recognition
    - Anomaly detection
    - Event correlation
    - Attack chain identification
    - Natural language querying
    
    Example:
        >>> agent = LogAnalyzerAgent(config, ml_engine, knowledge_base)
        >>> result = agent.analyze("/var/log/auth.log")
        >>> patterns = agent.find_patterns(result['entries'])
        >>> correlations = agent.correlate_events(result['entries'])
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        ml_engine,
        knowledge_base
    ):
        """
        Initialize Log Analyzer Agent.
        
        Args:
            config: Agent configuration
            ml_engine: ML engine for anomaly detection
            knowledge_base: Knowledge base for storing patterns
        """
        self.config = config
        self.ml_engine = ml_engine
        self.knowledge_base = knowledge_base
        
        # Agent settings
        self.system_prompt = config.get("system_prompt", "")
        self.llm_config = config.get("llm", {})
        
        # Analysis state
        self.known_patterns = []
        self.analysis_history = []
        
        logger.info("LogAnalyzerAgent initialized")
    
    def analyze(
        self,
        source: Union[str, List[str]],
        time_range: Optional[Tuple[str, str]] = None,
        filter_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze logs from source(s).
        
        Args:
            source: Log file path or list of paths
            time_range: (start, end) time range filter
            filter_level: Minimum log level to include
            
        Returns:
            Analysis results
        """
        sources = [source] if isinstance(source, str) else source
        logger.info(f"Analyzing {len(sources)} log source(s)")
        
        all_entries = []
        for src in sources:
            entries = self._ingest_logs(src, time_range, filter_level)
            all_entries.extend(entries)
        
        logger.info(f"Ingested {len(all_entries)} log entries")
        
        # Find patterns
        patterns = self.find_patterns(all_entries)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(all_entries)
        
        # Correlate events
        correlations = self.correlate_events(all_entries)
        
        # Generate insights
        insights = self._generate_insights(all_entries, patterns, anomalies, correlations)
        
        result = {
            "sources": sources,
            "total_entries": len(all_entries),
            "entries": all_entries,
            "patterns": patterns,
            "anomalies": anomalies,
            "correlations": correlations,
            "insights": insights,
            "analyzed_at": datetime.now().isoformat()
        }
        
        self.analysis_history.append(result)
        return result
    
    def _ingest_logs(
        self,
        source: str,
        time_range: Optional[Tuple[str, str]],
        filter_level: Optional[str]
    ) -> List[LogEntry]:
        """Ingest and parse logs from a source."""
        entries = []
        
        try:
            with open(source, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                entry = self._parse_log_line(line, source)
                if entry:
                    # Apply filters
                    if filter_level and not self._meets_level_filter(entry.level, filter_level):
                        continue
                    
                    entries.append(entry)
            
            logger.debug(f"Ingested {len(entries)} entries from {source}")
        
        except FileNotFoundError:
            logger.error(f"Log file not found: {source}")
        except Exception as e:
            logger.error(f"Failed to ingest logs from {source}: {e}")
        
        return entries
    
    def _parse_log_line(self, line: str, source: str) -> Optional[LogEntry]:
        """Parse a log line into structured format."""
        line = line.strip()
        if not line:
            return None
        
        entry_id = f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # Try to parse timestamp (multiple common formats)
        timestamp = None
        timestamp_patterns = [
            (r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', "%Y-%m-%d %H:%M:%S"),
            (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', "%Y-%m-%dT%H:%M:%S"),
            (r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', "%b %d %H:%M:%S"),
        ]
        
        for pattern, fmt in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp = match.group(1)
                break
        
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        # Detect log level
        level = "info"
        level_patterns = {
            "debug": r'\b(DEBUG|debug)\b',
            "info": r'\b(INFO|info)\b',
            "warning": r'\b(WARNING|WARN|warning|warn)\b',
            "error": r'\b(ERROR|error|ERR|err)\b',
            "critical": r'\b(CRITICAL|critical|FATAL|fatal)\b'
        }
        
        for lvl, pattern in level_patterns.items():
            if re.search(pattern, line):
                level = lvl
                break
        
        # Extract fields (key=value pairs)
        fields = {}
        field_pattern = r'(\w+)=(["\']?)([^\s"\']+)\2'
        for match in re.finditer(field_pattern, line):
            key, _, value = match.groups()
            fields[key] = value
        
        return LogEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            source=source,
            level=level,
            message=line,
            raw_log=line,
            fields=fields,
            metadata={}
        )
    
    def _meets_level_filter(self, entry_level: str, filter_level: str) -> bool:
        """Check if entry meets level filter."""
        level_order = ["debug", "info", "warning", "error", "critical"]
        try:
            entry_idx = level_order.index(entry_level)
            filter_idx = level_order.index(filter_level)
            return entry_idx >= filter_idx
        except ValueError:
            return True
    
    def find_patterns(
        self,
        entries: List[LogEntry],
        min_frequency: int = 3
    ) -> List[LogPattern]:
        """
        Find recurring patterns in log entries.
        
        Args:
            entries: Log entries to analyze
            min_frequency: Minimum occurrences to be considered a pattern
            
        Returns:
            List of detected patterns
        """
        logger.info(f"Finding patterns in {len(entries)} entries")
        
        patterns = []
        
        # Pattern 1: Repeated error messages
        error_messages = [e.message for e in entries if e.level in ["error", "critical"]]
        error_counts = Counter(error_messages)
        
        for message, count in error_counts.items():
            if count >= min_frequency:
                matching_entries = [e for e in entries if e.message == message]
                patterns.append(LogPattern(
                    pattern_id=f"pattern_{len(patterns)}",
                    pattern_type="repeated_error",
                    frequency=count,
                    first_seen=matching_entries[0].timestamp if matching_entries else "",
                    last_seen=matching_entries[-1].timestamp if matching_entries else "",
                    examples=[message[:200]],
                    severity="high" if count > 10 else "medium",
                    description=f"Error repeated {count} times"
                ))
        
        # Pattern 2: Burst of logs (many logs in short time)
        # Simplified - would need time-series analysis in production
        if len(entries) > 100:
            patterns.append(LogPattern(
                pattern_id=f"pattern_{len(patterns)}",
                pattern_type="log_burst",
                frequency=len(entries),
                first_seen=entries[0].timestamp if entries else "",
                last_seen=entries[-1].timestamp if entries else "",
                examples=[],
                severity="medium",
                description=f"High volume of logs: {len(entries)} entries"
            ))
        
        # Pattern 3: Sequential failures
        consecutive_errors = 0
        max_consecutive = 0
        
        for entry in entries:
            if entry.level in ["error", "critical"]:
                consecutive_errors += 1
                max_consecutive = max(max_consecutive, consecutive_errors)
            else:
                consecutive_errors = 0
        
        if max_consecutive >= min_frequency:
            patterns.append(LogPattern(
                pattern_id=f"pattern_{len(patterns)}",
                pattern_type="sequential_failures",
                frequency=max_consecutive,
                first_seen="",
                last_seen="",
                examples=[],
                severity="high",
                description=f"Up to {max_consecutive} consecutive errors detected"
            ))
        
        logger.info(f"Found {len(patterns)} patterns")
        return patterns
    
    def _detect_anomalies(self, entries: List[LogEntry]) -> List[Dict[str, Any]]:
        """Detect anomalous log entries using ML."""
        if not self.ml_engine or "anomaly_detector" not in self.ml_engine:
            logger.warning("ML engine not available for anomaly detection")
            return []
        
        logger.info(f"Detecting anomalies in {len(entries)} entries")
        
        # Extract text for ML analysis
        log_texts = [e.raw_log for e in entries]
        
        try:
            # Get anomaly scores
            scores = self.ml_engine["anomaly_detector"].detect(log_texts)
            
            # Filter anomalies
            threshold = 0.8
            anomalies = []
            
            for entry, score in zip(entries, scores):
                if score > threshold:
                    anomalies.append({
                        "entry_id": entry.entry_id,
                        "timestamp": entry.timestamp,
                        "source": entry.source,
                        "level": entry.level,
                        "message": entry.message[:200],
                        "anomaly_score": score,
                        "reason": "Statistical anomaly detected by ML model"
                    })
            
            logger.info(f"Detected {len(anomalies)} anomalies")
            return anomalies
        
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def correlate_events(
        self,
        entries: List[LogEntry],
        time_window: int = 300,
        min_correlation_size: int = 3
    ) -> List[CorrelationResult]:
        """
        Correlate log events to identify attack chains.
        
        Args:
            entries: Log entries to correlate
            time_window: Time window in seconds for correlation
            min_correlation_size: Minimum events in a correlation
            
        Returns:
            List of correlated event groups
        """
        logger.info(f"Correlating {len(entries)} events")
        
        correlations = []
        
        # Correlation 1: Same source authentication failures
        auth_entries = [e for e in entries if "auth" in e.source.lower() or "login" in e.message.lower()]
        failed_auth = [e for e in auth_entries if "failed" in e.message.lower() or "failure" in e.message.lower()]
        
        if len(failed_auth) >= min_correlation_size:
            correlations.append(CorrelationResult(
                correlation_id=f"corr_{len(correlations)}",
                events=failed_auth,
                correlation_type="authentication_failures",
                confidence=0.9,
                timeline=[(e.timestamp, "Auth failure") for e in failed_auth[:10]],
                potential_attack=len(failed_auth) > 5,
                description=f"Multiple authentication failures detected ({len(failed_auth)} events)"
            ))
        
        # Correlation 2: Error cascade
        errors = [e for e in entries if e.level in ["error", "critical"]]
        if len(errors) >= min_correlation_size:
            # Check if errors are close in time (simplified)
            correlations.append(CorrelationResult(
                correlation_id=f"corr_{len(correlations)}",
                events=errors,
                correlation_type="error_cascade",
                confidence=0.75,
                timeline=[(e.timestamp, e.level) for e in errors[:10]],
                potential_attack=False,
                description=f"Error cascade detected ({len(errors)} errors)"
            ))
        
        logger.info(f"Found {len(correlations)} correlations")
        return correlations
    
    def _generate_insights(
        self,
        entries: List[LogEntry],
        patterns: List[LogPattern],
        anomalies: List[Dict[str, Any]],
        correlations: List[CorrelationResult]
    ) -> List[str]:
        """Generate human-readable insights from analysis."""
        insights = []
        
        # Insight 1: Overall health
        error_count = len([e for e in entries if e.level in ["error", "critical"]])
        error_ratio = error_count / len(entries) if entries else 0
        
        if error_ratio > 0.1:
            insights.append(f"High error rate detected: {error_ratio:.1%} of logs are errors")
        elif error_ratio < 0.01:
            insights.append("Low error rate - system appears healthy")
        
        # Insight 2: Patterns
        if patterns:
            high_severity_patterns = [p for p in patterns if p.severity == "high"]
            if high_severity_patterns:
                insights.append(f"Found {len(high_severity_patterns)} high-severity patterns requiring attention")
        
        # Insight 3: Anomalies
        if anomalies:
            insights.append(f"Detected {len(anomalies)} anomalous events for investigation")
        
        # Insight 4: Correlations
        attack_correlations = [c for c in correlations if c.potential_attack]
        if attack_correlations:
            insights.append(f"WARNING: {len(attack_correlations)} potential attack patterns detected")
        
        # Insight 5: Most common issues
        error_messages = [e.message for e in entries if e.level == "error"]
        if error_messages:
            most_common = Counter(error_messages).most_common(1)[0]
            insights.append(f"Most common error: '{most_common[0][:100]}' ({most_common[1]} occurrences)")
        
        return insights
    
    def query_logs(
        self,
        entries: List[LogEntry],
        query: str
    ) -> List[LogEntry]:
        """
        Query logs using natural language or keywords.
        
        Args:
            entries: Log entries to search
            query: Search query
            
        Returns:
            Matching log entries
        """
        logger.info(f"Querying logs: {query}")
        
        query_lower = query.lower()
        
        # Simple keyword matching - in production, use semantic search
        matching = []
        for entry in entries:
            if (query_lower in entry.message.lower() or
                query_lower in entry.source.lower() or
                any(query_lower in str(v).lower() for v in entry.fields.values())):
                matching.append(entry)
        
        logger.info(f"Found {len(matching)} matching entries")
        return matching
    
    def export_analysis(
        self,
        analysis: Dict[str, Any],
        format: str = "json"
    ) -> str:
        """
        Export analysis results.
        
        Args:
            analysis: Analysis results
            format: Export format (json, markdown, csv)
            
        Returns:
            Exported content
        """
        if format == "json":
            # Convert dataclasses to dicts for JSON serialization
            serializable = {
                "sources": analysis["sources"],
                "total_entries": analysis["total_entries"],
                "patterns": [
                    {
                        "pattern_id": p.pattern_id,
                        "pattern_type": p.pattern_type,
                        "frequency": p.frequency,
                        "severity": p.severity,
                        "description": p.description
                    }
                    for p in analysis["patterns"]
                ],
                "anomalies": analysis["anomalies"],
                "insights": analysis["insights"],
                "analyzed_at": analysis["analyzed_at"]
            }
            return json.dumps(serializable, indent=2)
        
        elif format == "markdown":
            return self._export_markdown(analysis)
        
        return "Unsupported format"
    
    def _export_markdown(self, analysis: Dict[str, Any]) -> str:
        """Export analysis as markdown."""
        md = f"""# Log Analysis Report

## Summary
- **Sources**: {', '.join(analysis['sources'])}
- **Total Entries**: {analysis['total_entries']}
- **Analyzed**: {analysis['analyzed_at']}

## Insights
"""
        for insight in analysis["insights"]:
            md += f"- {insight}\n"
        
        md += f"\n## Patterns ({len(analysis['patterns'])})\n"
        for pattern in analysis["patterns"]:
            md += f"\n### {pattern.pattern_type}\n"
            md += f"- **Frequency**: {pattern.frequency}\n"
            md += f"- **Severity**: {pattern.severity}\n"
            md += f"- **Description**: {pattern.description}\n"
        
        md += f"\n## Anomalies ({len(analysis['anomalies'])})\n"
        for anomaly in analysis["anomalies"][:10]:  # Limit to first 10
            md += f"- **{anomaly['timestamp']}**: {anomaly['message'][:100]}... (score: {anomaly['anomaly_score']:.2f})\n"
        
        return md


__all__ = ["LogAnalyzerAgent", "LogEntry", "LogPattern", "CorrelationResult"]
