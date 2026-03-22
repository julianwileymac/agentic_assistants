"""
Cybersecurity Hub - Local security tooling, learning, and exploration platform.

A comprehensive cybersecurity hub built on the Agentic Assistants framework,
providing red team operations, blue team monitoring, vulnerability assessment,
and AI-powered security analysis.

Example:
    >>> from examples.cybersec_hub import CybersecHub
    >>> hub = CybersecHub()
    >>> red_team = hub.get_agent("red_team")
    >>> results = red_team.scan_target("192.168.1.0/24")
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

import yaml

from agentic_assistants.config import AgenticConfig
from agentic_assistants.engine import AgenticEngine
from agentic_assistants.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)

# Package info
__version__ = "1.0.0"
__author__ = "Cybersecurity Hub Team"

# Default config path
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.yaml"


class OperationMode(str, Enum):
    """Operation modes for the cybersecurity hub."""
    FULL = "full"
    RED_ONLY = "red-only"
    BLUE_ONLY = "blue-only"
    LEARNING = "learning"


class Severity(str, Enum):
    """Severity levels for findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ScanResult:
    """Result from a security scan operation."""
    scan_id: str
    target: str
    tool: str
    timestamp: str
    status: str
    findings: List[Dict[str, Any]]
    raw_output: str
    metadata: Dict[str, Any]


@dataclass
class Vulnerability:
    """Vulnerability finding."""
    vuln_id: str
    title: str
    description: str
    severity: Severity
    cvss_score: Optional[float]
    affected_target: str
    cve_id: Optional[str]
    remediation: Optional[str]
    references: List[str]
    metadata: Dict[str, Any]


class CybersecHub:
    """
    Main Cybersecurity Hub interface.
    
    Provides a comprehensive platform for security operations, including:
    - Red team operations (offensive security)
    - Blue team monitoring (defensive security)
    - Vulnerability assessment and management
    - AI-powered log analysis and anomaly detection
    - Tool management and automation
    - Knowledge base for security intelligence
    
    Example:
        >>> hub = CybersecHub()
        >>> 
        >>> # Red team operations
        >>> red_team = hub.get_agent("red_team")
        >>> scan_results = hub.scan_target("192.168.1.100", tool="nmap")
        >>> 
        >>> # Blue team monitoring
        >>> blue_team = hub.get_agent("blue_team")
        >>> anomalies = hub.analyze_logs(source="/var/log/auth.log")
        >>> 
        >>> # Vulnerability management
        >>> vulns = hub.get_vulnerabilities(severity="critical")
        >>> 
        >>> # AI assistant
        >>> assistant = hub.get_assistant()
        >>> advice = assistant.chat("How should I secure SSH?")
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        mode: Optional[OperationMode] = None,
        project_id: Optional[str] = None,
    ):
        """
        Initialize the Cybersecurity Hub.
        
        Args:
            config_path: Path to configuration file
            mode: Operation mode (full, red-only, blue-only, learning)
            project_id: Project identifier for scoping
        """
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.project_id = project_id or "cybersec-hub"
        
        # Load configuration
        self._config = self._load_config()
        
        # Set operation mode
        self.mode = mode or OperationMode(self._config.get("cybersec", {}).get("mode", "full"))
        
        # Initialize paths
        self.data_dir = Path(self._config.get("paths", {}).get("data_dir", "./data"))
        self.tools_dir = Path(self._config.get("paths", {}).get("tools_dir", "./data/tools"))
        self.logs_dir = Path(self._config.get("paths", {}).get("logs_dir", "./data/logs"))
        self.reports_dir = Path(self._config.get("paths", {}).get("reports_dir", "./data/reports"))
        
        # Ensure directories exist
        for dir_path in [self.data_dir, self.tools_dir, self.logs_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components (lazy loaded)
        self._engine = None
        self._agents = {}
        self._tool_manager = None
        self._ml_engine = None
        self._network_manager = None
        self._knowledge_base = None
        self._assistant = None
        
        # Setup logging
        setup_logging(
            level=self._config.get("logging", {}).get("level", "INFO"),
            output_file=str(self.logs_dir / "cybersec-hub.log")
        )
        
        logger.info(f"CybersecHub initialized in {self.mode} mode")
        logger.info(f"Configuration: {self.config_path}")
        logger.info(f"Data directory: {self.data_dir}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
                logger.debug(f"Loaded configuration from {self.config_path}")
                return config
        logger.warning(f"Configuration file not found: {self.config_path}")
        return {}
    
    @property
    def engine(self) -> AgenticEngine:
        """Get the Agentic Engine instance."""
        if self._engine is None:
            self._engine = AgenticEngine()
            logger.debug("AgenticEngine initialized")
        return self._engine
    
    @property
    def tool_manager(self):
        """Get the tool manager."""
        if self._tool_manager is None:
            from .tools.tool_manager import ToolManager
            self._tool_manager = ToolManager(
                config=self._config.get("cybersec", {}).get("tools", {}),
                tools_dir=self.tools_dir
            )
            logger.debug("ToolManager initialized")
        return self._tool_manager
    
    @property
    def ml_engine(self):
        """Get the ML engine for anomaly detection and prediction."""
        if self._ml_engine is None:
            from .ml.anomaly_detection import AnomalyDetector
            from .ml.vuln_predictor import VulnerabilityPredictor
            
            self._ml_engine = {
                "anomaly_detector": AnomalyDetector(
                    config=self._config.get("cybersec", {}).get("ml", {}).get("anomaly_detection", {})
                ),
                "vuln_predictor": VulnerabilityPredictor(
                    config=self._config.get("cybersec", {}).get("ml", {}).get("vulnerability_prediction", {})
                )
            }
            logger.debug("ML Engine initialized")
        return self._ml_engine
    
    @property
    def network_manager(self):
        """Get the network manager for VPN and target management."""
        if self._network_manager is None:
            from .network.vpn_manager import VPNManager
            from .network.target_manager import TargetManager
            
            self._network_manager = {
                "vpn": VPNManager(
                    config=self._config.get("cybersec", {}).get("network", {})
                ),
                "targets": TargetManager(
                    config=self._config.get("cybersec", {}).get("red_team", {})
                )
            }
            logger.debug("Network Manager initialized")
        return self._network_manager
    
    @property
    def knowledge_base(self):
        """Get the knowledge base (vector store)."""
        if self._knowledge_base is None:
            from agentic_assistants.vectordb import get_vector_store
            
            vector_config = self._config.get("vector_db", {})
            self._knowledge_base = get_vector_store(
                backend=vector_config.get("backend", "lancedb"),
                path=vector_config.get("path", str(self.data_dir / "knowledge" / "vectordb"))
            )
            logger.debug("Knowledge Base initialized")
        return self._knowledge_base
    
    def get_agent(self, agent_type: str):
        """
        Get a specialized security agent.
        
        Args:
            agent_type: Type of agent (red_team, blue_team, vulnerability_scanner, log_analyzer)
            
        Returns:
            Initialized agent instance
        """
        if agent_type not in self._agents:
            agent_config = self._config.get("agents", {}).get(agent_type, {})
            
            if agent_type == "red_team":
                from .agents.red_team_agent import RedTeamAgent
                self._agents[agent_type] = RedTeamAgent(
                    config=agent_config,
                    tool_manager=self.tool_manager,
                    knowledge_base=self.knowledge_base
                )
            elif agent_type == "blue_team":
                from .agents.blue_team_agent import BlueTeamAgent
                self._agents[agent_type] = BlueTeamAgent(
                    config=agent_config,
                    ml_engine=self.ml_engine,
                    knowledge_base=self.knowledge_base
                )
            elif agent_type == "vulnerability_scanner":
                from .agents.vulnerability_scanner_agent import VulnerabilityScannerAgent
                self._agents[agent_type] = VulnerabilityScannerAgent(
                    config=agent_config,
                    tool_manager=self.tool_manager,
                    ml_engine=self.ml_engine
                )
            elif agent_type == "log_analyzer":
                from .agents.log_analyzer_agent import LogAnalyzerAgent
                self._agents[agent_type] = LogAnalyzerAgent(
                    config=agent_config,
                    ml_engine=self.ml_engine,
                    knowledge_base=self.knowledge_base
                )
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            logger.info(f"Agent '{agent_type}' initialized")
        
        return self._agents[agent_type]
    
    def get_assistant(self):
        """
        Get the AI security assistant for interactive guidance.
        
        Returns:
            Security assistant instance
        """
        if self._assistant is None:
            from .ml.assistant import SecurityAssistant
            self._assistant = SecurityAssistant(
                config=self._config.get("cybersec", {}).get("ml", {}).get("assistant", {}),
                knowledge_base=self.knowledge_base,
                tool_manager=self.tool_manager
            )
            logger.debug("Security Assistant initialized")
        return self._assistant
    
    def scan_target(
        self,
        target: str,
        tool: str = "nmap",
        options: Optional[List[str]] = None,
        stealth: bool = False
    ) -> ScanResult:
        """
        Scan a target with specified tool.
        
        Args:
            target: Target IP, hostname, or network (CIDR)
            tool: Security tool to use
            options: Tool-specific options
            stealth: Use stealth mode if available
            
        Returns:
            ScanResult with findings
        """
        logger.info(f"Scanning target {target} with {tool}")
        
        # Validate target authorization
        if not self.network_manager["targets"].is_authorized(target):
            raise PermissionError(f"Target {target} is not authorized for scanning")
        
        # Execute scan
        result = self.tool_manager.execute(
            tool=tool,
            target=target,
            options=options or [],
            stealth=stealth
        )
        
        # Store results in knowledge base
        self.knowledge_base.add(
            collection="cybersec-logs",
            text=result.raw_output,
            metadata={
                "tool": tool,
                "target": target,
                "timestamp": result.timestamp
            }
        )
        
        logger.info(f"Scan completed: {result.scan_id}")
        return result
    
    def analyze_logs(
        self,
        source: str,
        detect_anomalies: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze security logs for threats and anomalies.
        
        Args:
            source: Log file path or identifier
            detect_anomalies: Run anomaly detection
            
        Returns:
            Analysis results with anomalies and insights
        """
        logger.info(f"Analyzing logs from {source}")
        
        log_analyzer = self.get_agent("log_analyzer")
        results = log_analyzer.analyze(source=source)
        
        if detect_anomalies:
            anomalies = self.ml_engine["anomaly_detector"].detect(results["events"])
            results["anomalies"] = anomalies
        
        return results
    
    def get_vulnerabilities(
        self,
        severity: Optional[str] = None,
        target: Optional[str] = None,
        limit: int = 100
    ) -> List[Vulnerability]:
        """
        Get vulnerabilities from knowledge base.
        
        Args:
            severity: Filter by severity level
            target: Filter by target
            limit: Maximum results to return
            
        Returns:
            List of vulnerabilities
        """
        # Query knowledge base
        filters = {}
        if severity:
            filters["severity"] = severity
        if target:
            filters["target"] = target
        
        results = self.knowledge_base.search(
            collection="cybersec-vulnerabilities",
            query="",
            limit=limit,
            filters=filters
        )
        
        # Convert to Vulnerability objects
        vulnerabilities = []
        for result in results:
            vuln = Vulnerability(
                vuln_id=result.get("vuln_id", ""),
                title=result.get("title", ""),
                description=result.get("description", ""),
                severity=Severity(result.get("severity", "info")),
                cvss_score=result.get("cvss_score"),
                affected_target=result.get("target", ""),
                cve_id=result.get("cve_id"),
                remediation=result.get("remediation"),
                references=result.get("references", []),
                metadata=result.get("metadata", {})
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def generate_report(
        self,
        scan_ids: Optional[List[str]] = None,
        format: str = "html",
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate security assessment report.
        
        Args:
            scan_ids: Specific scan IDs to include
            format: Report format (html, pdf, json, markdown)
            output_path: Output file path
            
        Returns:
            Path to generated report
        """
        logger.info(f"Generating {format} report")
        
        # Import reporting module
        from .automation.reporting import ReportGenerator
        
        generator = ReportGenerator(
            config=self._config.get("cybersec", {}).get("reporting", {}),
            knowledge_base=self.knowledge_base
        )
        
        report_path = generator.generate(
            scan_ids=scan_ids,
            format=format,
            output_path=output_path or str(self.reports_dir)
        )
        
        logger.info(f"Report generated: {report_path}")
        return report_path
    
    def install_tool(self, tool_name: str) -> bool:
        """
        Install a security tool.
        
        Args:
            tool_name: Name of tool to install
            
        Returns:
            True if installation succeeded
        """
        logger.info(f"Installing tool: {tool_name}")
        return self.tool_manager.install(tool_name)
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available security tools.
        
        Args:
            category: Filter by category (network, web, exploit, etc.)
            
        Returns:
            List of tool information
        """
        return self.tool_manager.list_tools(category=category)
    
    def connect_vpn(self, profile: Optional[str] = None) -> bool:
        """
        Connect to VPN for international testing.
        
        Args:
            profile: VPN profile name (uses default if None)
            
        Returns:
            True if connection succeeded
        """
        logger.info(f"Connecting to VPN: {profile or 'default'}")
        return self.network_manager["vpn"].connect(profile)
    
    def disconnect_vpn(self) -> bool:
        """Disconnect from VPN."""
        logger.info("Disconnecting from VPN")
        return self.network_manager["vpn"].disconnect()


# Convenience function
def create_hub(config_path: Optional[str] = None, mode: Optional[str] = None) -> CybersecHub:
    """
    Create a CybersecHub instance.
    
    Args:
        config_path: Path to configuration file
        mode: Operation mode
        
    Returns:
        Initialized CybersecHub instance
    """
    return CybersecHub(
        config_path=config_path,
        mode=OperationMode(mode) if mode else None
    )


__all__ = [
    "CybersecHub",
    "create_hub",
    "OperationMode",
    "Severity",
    "ScanResult",
    "Vulnerability",
]
