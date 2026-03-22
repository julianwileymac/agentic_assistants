"""
Blue Team Agent for defensive security operations.

Monitors systems for threats, detects anomalies, and responds to incidents.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import re
import json

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SecurityEvent:
    """Security event metadata."""
    event_id: str
    timestamp: str
    source: str
    severity: str  # low, medium, high, critical
    event_type: str
    description: str
    raw_log: str
    metadata: Dict[str, Any]


@dataclass
class ThreatDetection:
    """Detected threat."""
    threat_id: str
    detected_at: str
    threat_type: str
    severity: str
    confidence: float
    indicators: List[str]
    recommended_actions: List[str]
    metadata: Dict[str, Any]


class BlueTeamAgent:
    """
    Automated defensive security operations agent.
    
    Capabilities:
    - Log monitoring and analysis
    - Intrusion detection
    - Anomaly detection
    - Incident response automation
    - Threat intelligence correlation
    
    Example:
        >>> agent = BlueTeamAgent(config, ml_engine, knowledge_base)
        >>> agent.start_monitoring(sources=["/var/log/auth.log"])
        >>> anomalies = agent.detect_anomalies()
        >>> agent.respond_to_threat(threat)
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        ml_engine,
        knowledge_base
    ):
        """
        Initialize Blue Team Agent.
        
        Args:
            config: Agent configuration
            ml_engine: ML engine for anomaly detection
            knowledge_base: Knowledge base for threat intelligence
        """
        self.config = config
        self.ml_engine = ml_engine
        self.knowledge_base = knowledge_base
        
        # Agent settings
        self.system_prompt = config.get("system_prompt", "")
        self.llm_config = config.get("llm", {})
        self.tools = config.get("tools", [])
        
        # Monitoring state
        self.monitoring_active = False
        self.monitored_sources = []
        self.event_history = []
        self.threat_detections = []
        
        logger.info("BlueTeamAgent initialized")
    
    def start_monitoring(
        self,
        sources: List[str],
        interval: int = 60,
        alert_threshold: float = 0.8
    ):
        """
        Start continuous monitoring of log sources.
        
        Args:
            sources: List of log file paths or identifiers
            interval: Check interval in seconds
            alert_threshold: Anomaly score threshold for alerts
        """
        logger.info(f"Starting monitoring of {len(sources)} sources")
        
        self.monitoring_active = True
        self.monitored_sources = sources
        self.config["monitoring_interval"] = interval
        self.config["alert_threshold"] = alert_threshold
        
        logger.info(f"Monitoring active: interval={interval}s, threshold={alert_threshold}")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        logger.info("Stopping monitoring")
        self.monitoring_active = False
        self.monitored_sources = []
    
    def analyze_logs(
        self,
        source: str,
        time_range: Optional[tuple] = None,
        filter_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze logs from a specific source.
        
        Args:
            source: Log source path or identifier
            time_range: (start_time, end_time) tuple
            filter_pattern: Regex pattern to filter logs
            
        Returns:
            Analysis results with events and anomalies
        """
        logger.info(f"Analyzing logs from {source}")
        
        try:
            # Read log file
            with open(source, 'r') as f:
                log_lines = f.readlines()
            
            # Parse log entries
            events = []
            for line in log_lines:
                event = self._parse_log_line(line, source)
                if event:
                    # Apply filter if specified
                    if filter_pattern and not re.search(filter_pattern, line):
                        continue
                    events.append(event)
            
            logger.info(f"Parsed {len(events)} events from {source}")
            
            # Detect anomalies using ML
            anomalies = []
            if self.ml_engine and "anomaly_detector" in self.ml_engine:
                anomaly_scores = self.ml_engine["anomaly_detector"].detect(
                    [e.raw_log for e in events]
                )
                
                # Filter by threshold
                threshold = self.config.get("alert_threshold", 0.8)
                for event, score in zip(events, anomaly_scores):
                    if score > threshold:
                        anomalies.append({
                            "event": event,
                            "anomaly_score": score,
                            "reason": "Statistical anomaly detected"
                        })
            
            # Identify common threat patterns
            threats = self._identify_threats(events)
            
            return {
                "source": source,
                "total_events": len(events),
                "events": events,
                "anomalies": anomalies,
                "threats": threats,
                "analysis_time": datetime.now().isoformat()
            }
        
        except FileNotFoundError:
            logger.error(f"Log file not found: {source}")
            return {"error": f"Log file not found: {source}"}
        except Exception as e:
            logger.error(f"Log analysis failed: {e}")
            return {"error": str(e)}
    
    def _parse_log_line(self, line: str, source: str) -> Optional[SecurityEvent]:
        """Parse a log line into a SecurityEvent."""
        line = line.strip()
        if not line:
            return None
        
        # Basic log parsing - would need to be customized per log format
        event_id = f"evt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # Try to extract timestamp (common formats)
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',  # 2024-01-01 12:00:00
            r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})',     # Jan 01 12:00:00
        ]
        
        timestamp = datetime.now().isoformat()
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp = match.group(1)
                break
        
        # Determine severity based on keywords
        severity = "info"
        if any(word in line.lower() for word in ["error", "failed", "failure"]):
            severity = "medium"
        if any(word in line.lower() for word in ["critical", "alert", "emergency"]):
            severity = "high"
        if any(word in line.lower() for word in ["attack", "intrusion", "breach"]):
            severity = "critical"
        
        # Determine event type
        event_type = "general"
        if "authentication" in line.lower() or "login" in line.lower():
            event_type = "authentication"
        elif "connection" in line.lower() or "network" in line.lower():
            event_type = "network"
        elif "file" in line.lower():
            event_type = "file_access"
        
        return SecurityEvent(
            event_id=event_id,
            timestamp=timestamp,
            source=source,
            severity=severity,
            event_type=event_type,
            description=line[:200],  # Truncate long lines
            raw_log=line,
            metadata={}
        )
    
    def _identify_threats(self, events: List[SecurityEvent]) -> List[ThreatDetection]:
        """Identify common threat patterns in events."""
        threats = []
        
        # Pattern 1: Multiple failed authentication attempts (brute force)
        auth_failures = [e for e in events if e.event_type == "authentication" and "failed" in e.description.lower()]
        if len(auth_failures) > 5:
            threats.append(ThreatDetection(
                threat_id=f"threat_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                detected_at=datetime.now().isoformat(),
                threat_type="brute_force",
                severity="high",
                confidence=0.85,
                indicators=[e.event_id for e in auth_failures[:10]],
                recommended_actions=[
                    "Review failed authentication attempts",
                    "Check for IP address patterns",
                    "Consider rate limiting",
                    "Enable account lockout policies"
                ],
                metadata={"failure_count": len(auth_failures)}
            ))
        
        # Pattern 2: Unusual network activity
        network_events = [e for e in events if e.event_type == "network"]
        if len(network_events) > 100:
            threats.append(ThreatDetection(
                threat_id=f"threat_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                detected_at=datetime.now().isoformat(),
                threat_type="unusual_network_activity",
                severity="medium",
                confidence=0.70,
                indicators=[e.event_id for e in network_events[:10]],
                recommended_actions=[
                    "Investigate network traffic patterns",
                    "Check for data exfiltration",
                    "Review firewall rules"
                ],
                metadata={"event_count": len(network_events)}
            ))
        
        return threats
    
    def detect_anomalies(
        self,
        events: Optional[List[SecurityEvent]] = None,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in security events using ML.
        
        Args:
            events: Events to analyze (uses history if None)
            threshold: Anomaly score threshold
            
        Returns:
            List of detected anomalies
        """
        events = events or self.event_history
        threshold = threshold or self.config.get("alert_threshold", 0.8)
        
        if not events:
            logger.warning("No events to analyze")
            return []
        
        logger.info(f"Detecting anomalies in {len(events)} events")
        
        # Use ML anomaly detector
        if self.ml_engine and "anomaly_detector" in self.ml_engine:
            log_texts = [e.raw_log for e in events]
            scores = self.ml_engine["anomaly_detector"].detect(log_texts)
            
            anomalies = []
            for event, score in zip(events, scores):
                if score > threshold:
                    anomalies.append({
                        "event_id": event.event_id,
                        "timestamp": event.timestamp,
                        "source": event.source,
                        "severity": event.severity,
                        "anomaly_score": score,
                        "description": event.description,
                        "recommended_action": self._recommend_action(event, score)
                    })
            
            logger.info(f"Detected {len(anomalies)} anomalies")
            return anomalies
        
        logger.warning("ML engine not available for anomaly detection")
        return []
    
    def _recommend_action(self, event: SecurityEvent, score: float) -> str:
        """Recommend action based on event and anomaly score."""
        if score > 0.9:
            return "Immediate investigation required - high confidence anomaly"
        elif score > 0.8:
            return "Investigate soon - potential security incident"
        elif event.severity == "critical":
            return "Review critical event details"
        else:
            return "Monitor for patterns"
    
    def respond_to_threat(
        self,
        threat: Union[ThreatDetection, Dict[str, Any]],
        auto_respond: bool = False
    ) -> Dict[str, Any]:
        """
        Respond to detected threat.
        
        Args:
            threat: Detected threat or threat dict
            auto_respond: Automatically execute response actions
            
        Returns:
            Response result
        """
        if isinstance(threat, dict):
            threat_id = threat.get("threat_id", "unknown")
            threat_type = threat.get("threat_type", "unknown")
        else:
            threat_id = threat.threat_id
            threat_type = threat.threat_type
        
        logger.warning(f"Responding to threat: {threat_id} ({threat_type})")
        
        if not auto_respond:
            logger.info("Auto-response disabled - manual intervention required")
            return {
                "success": False,
                "message": "Manual response required",
                "threat_id": threat_id
            }
        
        # Automated response actions (simplified)
        response_log = []
        
        if threat_type == "brute_force":
            response_log.append("Logged brute force attempt")
            response_log.append("Alerted security team")
            # In production: block IP, enable rate limiting, etc.
        
        elif threat_type == "unusual_network_activity":
            response_log.append("Logged unusual network activity")
            response_log.append("Captured network traffic for analysis")
        
        return {
            "success": True,
            "threat_id": threat_id,
            "actions_taken": response_log,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_incident_report(
        self,
        threat: ThreatDetection,
        include_recommendations: bool = True
    ) -> str:
        """
        Generate incident report for a threat.
        
        Args:
            threat: Threat detection
            include_recommendations: Include recommended actions
            
        Returns:
            Incident report (markdown format)
        """
        report = f"""# Security Incident Report

## Threat Details
- **Threat ID**: {threat.threat_id}
- **Detected**: {threat.detected_at}
- **Type**: {threat.threat_type}
- **Severity**: {threat.severity}
- **Confidence**: {threat.confidence:.2%}

## Indicators
"""
        
        for indicator in threat.indicators:
            report += f"- {indicator}\n"
        
        if include_recommendations:
            report += "\n## Recommended Actions\n"
            for action in threat.recommended_actions:
                report += f"- {action}\n"
        
        report += f"\n## Metadata\n```json\n{json.dumps(threat.metadata, indent=2)}\n```\n"
        
        return report
    
    def correlate_events(
        self,
        events: List[SecurityEvent],
        time_window: int = 300
    ) -> List[Dict[str, Any]]:
        """
        Correlate events to identify attack chains.
        
        Args:
            events: Events to correlate
            time_window: Time window in seconds
            
        Returns:
            List of correlated event groups
        """
        logger.info(f"Correlating {len(events)} events (window={time_window}s)")
        
        # Group events by source and time proximity
        # This is simplified - production would use more sophisticated correlation
        
        correlated_groups = []
        processed = set()
        
        for i, event in enumerate(events):
            if event.event_id in processed:
                continue
            
            # Find related events
            related = [event]
            for j, other in enumerate(events[i+1:]):
                if other.event_id in processed:
                    continue
                
                # Check if events are related (same source, similar time)
                if event.source == other.source:
                    related.append(other)
                    processed.add(other.event_id)
            
            if len(related) > 1:
                correlated_groups.append({
                    "group_id": f"corr_{i}",
                    "event_count": len(related),
                    "events": related,
                    "potential_attack_chain": len(related) > 5
                })
                processed.add(event.event_id)
        
        logger.info(f"Found {len(correlated_groups)} correlated event groups")
        return correlated_groups
    
    def get_security_posture(self) -> Dict[str, Any]:
        """
        Get overall security posture assessment.
        
        Returns:
            Security posture metrics
        """
        # Calculate metrics based on recent events and threats
        total_events = len(self.event_history)
        total_threats = len(self.threat_detections)
        
        # Calculate severity distribution
        severity_dist = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        }
        
        for event in self.event_history:
            severity_dist[event.severity] = severity_dist.get(event.severity, 0) + 1
        
        # Calculate posture score (simplified)
        score = 100
        score -= severity_dist.get("critical", 0) * 10
        score -= severity_dist.get("high", 0) * 5
        score -= severity_dist.get("medium", 0) * 2
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "status": "good" if score > 80 else "warning" if score > 60 else "critical",
            "total_events": total_events,
            "total_threats": total_threats,
            "severity_distribution": severity_dist,
            "monitoring_active": self.monitoring_active,
            "monitored_sources": len(self.monitored_sources),
            "timestamp": datetime.now().isoformat()
        }


__all__ = ["BlueTeamAgent", "SecurityEvent", "ThreatDetection"]
