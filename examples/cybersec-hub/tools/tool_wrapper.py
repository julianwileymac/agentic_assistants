"""
Base class and common wrappers for security tools.

Provides Python interfaces for security tools with standardized methods.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import re
import json

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedOutput:
    """Parsed output from a security tool."""
    raw: str
    findings: List[Dict[str, Any]]
    summary: Dict[str, Any]
    metadata: Dict[str, Any]


class BaseToolWrapper(ABC):
    """
    Base class for security tool wrappers.
    
    Provides a standardized interface for executing and parsing
    security tool output.
    """
    
    def __init__(
        self,
        tool_manager,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize tool wrapper.
        
        Args:
            tool_manager: ToolManager instance
            config: Configuration dictionary
        """
        self.tool_manager = tool_manager
        self.config = config or {}
        self.tool_name = self._get_tool_name()
    
    @abstractmethod
    def _get_tool_name(self) -> str:
        """Get the tool identifier."""
        pass
    
    @abstractmethod
    def parse_output(self, output: str) -> ParsedOutput:
        """
        Parse tool output into structured format.
        
        Args:
            output: Raw tool output
            
        Returns:
            ParsedOutput with structured findings
        """
        pass
    
    def run(
        self,
        target: str,
        options: Optional[List[str]] = None,
        **kwargs
    ) -> ParsedOutput:
        """
        Execute the tool and parse output.
        
        Args:
            target: Target to scan/test
            options: Tool-specific options
            **kwargs: Additional execution parameters
            
        Returns:
            ParsedOutput with results
        """
        # Execute tool
        result = self.tool_manager.execute(
            tool=self.tool_name,
            target=target,
            options=options,
            **kwargs
        )
        
        if not result.success:
            logger.warning(f"{self.tool_name} execution failed: {result.stderr}")
        
        # Parse output
        parsed = self.parse_output(result.stdout)
        
        # Add execution metadata
        parsed.metadata.update({
            "exit_code": result.exit_code,
            "duration": result.duration,
            "timestamp": result.timestamp,
            "command": result.command
        })
        
        return parsed
    
    def validate_target(self, target: str) -> bool:
        """
        Validate target format.
        
        Args:
            target: Target string
            
        Returns:
            True if valid
        """
        # Basic validation - can be overridden
        return bool(target and target.strip())


class NmapWrapper(BaseToolWrapper):
    """Wrapper for Nmap network scanner."""
    
    def _get_tool_name(self) -> str:
        return "nmap"
    
    def parse_output(self, output: str) -> ParsedOutput:
        """Parse Nmap output."""
        findings = []
        hosts = []
        
        # Simple parsing - in production, use python-nmap or parse XML
        current_host = None
        for line in output.split("\n"):
            line = line.strip()
            
            # Parse host line
            if "Nmap scan report for" in line:
                host_match = re.search(r'for (.+)$', line)
                if host_match:
                    current_host = {
                        "host": host_match.group(1).strip(),
                        "ports": []
                    }
                    hosts.append(current_host)
            
            # Parse port line
            elif current_host and re.match(r'\d+/tcp', line):
                parts = line.split()
                if len(parts) >= 3:
                    port_info = {
                        "port": parts[0],
                        "state": parts[1],
                        "service": parts[2] if len(parts) > 2 else "unknown"
                    }
                    current_host["ports"].append(port_info)
                    findings.append({
                        "type": "open_port",
                        "host": current_host["host"],
                        **port_info
                    })
        
        summary = {
            "total_hosts": len(hosts),
            "total_ports": len(findings),
            "hosts": hosts
        }
        
        return ParsedOutput(
            raw=output,
            findings=findings,
            summary=summary,
            metadata={"parser": "nmap"}
        )
    
    def scan_ports(
        self,
        target: str,
        port_range: str = "1-1000",
        service_detection: bool = False
    ) -> ParsedOutput:
        """
        Scan ports on target.
        
        Args:
            target: Target host or network
            port_range: Port range to scan
            service_detection: Enable service version detection
            
        Returns:
            ParsedOutput with port scan results
        """
        options = ["-p", port_range]
        if service_detection:
            options.append("-sV")
        
        return self.run(target, options=options)


class SQLMapWrapper(BaseToolWrapper):
    """Wrapper for SQLMap SQL injection tool."""
    
    def _get_tool_name(self) -> str:
        return "sqlmap"
    
    def parse_output(self, output: str) -> ParsedOutput:
        """Parse SQLMap output."""
        findings = []
        
        # Look for vulnerabilities
        if "sqlmap identified the following injection point" in output:
            findings.append({
                "type": "sql_injection",
                "severity": "high",
                "description": "SQL injection vulnerability detected"
            })
        
        # Extract database information
        db_info = {}
        if "back-end DBMS:" in output:
            match = re.search(r'back-end DBMS: (.+)', output)
            if match:
                db_info["dbms"] = match.group(1).strip()
        
        summary = {
            "vulnerable": len(findings) > 0,
            "injection_points": len(findings),
            "database_info": db_info
        }
        
        return ParsedOutput(
            raw=output,
            findings=findings,
            summary=summary,
            metadata={"parser": "sqlmap"}
        )
    
    def test_url(
        self,
        url: str,
        cookie: Optional[str] = None,
        data: Optional[str] = None
    ) -> ParsedOutput:
        """
        Test URL for SQL injection.
        
        Args:
            url: Target URL
            cookie: Cookie string
            data: POST data
            
        Returns:
            ParsedOutput with injection findings
        """
        options = ["-u"]
        if cookie:
            options.extend(["--cookie", cookie])
        if data:
            options.extend(["--data", data])
        options.append("--batch")  # Non-interactive
        
        return self.run(url, options=options)


class MetasploitWrapper(BaseToolWrapper):
    """Wrapper for Metasploit Framework."""
    
    def _get_tool_name(self) -> str:
        return "metasploit"
    
    def parse_output(self, output: str) -> ParsedOutput:
        """Parse Metasploit output."""
        findings = []
        
        # Parse module execution results
        if "[+]" in output:
            for line in output.split("\n"):
                if "[+]" in line:
                    findings.append({
                        "type": "success",
                        "message": line.split("[+]", 1)[1].strip()
                    })
        
        if "[-]" in output:
            for line in output.split("\n"):
                if "[-]" in line:
                    findings.append({
                        "type": "error",
                        "message": line.split("[-]", 1)[1].strip()
                    })
        
        summary = {
            "success_count": sum(1 for f in findings if f["type"] == "success"),
            "error_count": sum(1 for f in findings if f["type"] == "error")
        }
        
        return ParsedOutput(
            raw=output,
            findings=findings,
            summary=summary,
            metadata={"parser": "metasploit"}
        )


class NiktoWrapper(BaseToolWrapper):
    """Wrapper for Nikto web scanner."""
    
    def _get_tool_name(self) -> str:
        return "nikto"
    
    def parse_output(self, output: str) -> ParsedOutput:
        """Parse Nikto output."""
        findings = []
        
        # Parse vulnerability lines
        for line in output.split("\n"):
            if line.startswith("+"):
                # Extract OSVDB references and descriptions
                parts = line.split(":", 1)
                if len(parts) > 1:
                    finding = {
                        "type": "web_vulnerability",
                        "description": parts[1].strip(),
                        "severity": "medium"  # Default
                    }
                    
                    # Try to extract OSVDB ID
                    osvdb_match = re.search(r'OSVDB-(\d+)', line)
                    if osvdb_match:
                        finding["osvdb_id"] = osvdb_match.group(1)
                    
                    findings.append(finding)
        
        summary = {
            "total_findings": len(findings),
            "vulnerabilities": len([f for f in findings if f["type"] == "web_vulnerability"])
        }
        
        return ParsedOutput(
            raw=output,
            findings=findings,
            summary=summary,
            metadata={"parser": "nikto"}
        )
    
    def scan_web(
        self,
        target: str,
        ssl: bool = False,
        port: int = 80
    ) -> ParsedOutput:
        """
        Scan web server.
        
        Args:
            target: Target host
            ssl: Use HTTPS
            port: Target port
            
        Returns:
            ParsedOutput with web vulnerabilities
        """
        options = ["-h", target]
        if ssl:
            options.append("-ssl")
        if port != 80:
            options.extend(["-p", str(port)])
        
        # Remove target from end since we already added it with -h
        return self.tool_manager.execute(
            tool=self.tool_name,
            target="",
            options=options
        )


class WiresharkWrapper(BaseToolWrapper):
    """Wrapper for Wireshark/tshark packet analyzer."""
    
    def _get_tool_name(self) -> str:
        return "wireshark"
    
    def parse_output(self, output: str) -> ParsedOutput:
        """Parse tshark output."""
        findings = []
        packets = []
        
        # Parse packet lines
        for line in output.split("\n"):
            if line.strip():
                packets.append({"raw": line})
        
        summary = {
            "total_packets": len(packets),
            "protocols": []  # Would extract from actual parsing
        }
        
        return ParsedOutput(
            raw=output,
            findings=findings,
            summary=summary,
            metadata={"parser": "tshark"}
        )
    
    def capture(
        self,
        interface: str = "eth0",
        duration: int = 10,
        filter: Optional[str] = None
    ) -> ParsedOutput:
        """
        Capture network traffic.
        
        Args:
            interface: Network interface
            duration: Capture duration in seconds
            filter: BPF filter
            
        Returns:
            ParsedOutput with packet data
        """
        options = ["-i", interface, "-a", f"duration:{duration}"]
        if filter:
            options.extend(["-f", filter])
        
        return self.run(interface, options=options)


# Tool wrapper registry
WRAPPER_REGISTRY = {
    "nmap": NmapWrapper,
    "sqlmap": SQLMapWrapper,
    "metasploit": MetasploitWrapper,
    "nikto": NiktoWrapper,
    "wireshark": WiresharkWrapper,
}


def get_wrapper(tool_name: str, tool_manager, config: Optional[Dict] = None):
    """
    Get wrapper instance for a tool.
    
    Args:
        tool_name: Tool identifier
        tool_manager: ToolManager instance
        config: Configuration dict
        
    Returns:
        Tool wrapper instance
    """
    wrapper_class = WRAPPER_REGISTRY.get(tool_name)
    if not wrapper_class:
        raise ValueError(f"No wrapper available for {tool_name}")
    
    return wrapper_class(tool_manager=tool_manager, config=config)


__all__ = [
    "BaseToolWrapper",
    "ParsedOutput",
    "NmapWrapper",
    "SQLMapWrapper",
    "MetasploitWrapper",
    "NiktoWrapper",
    "WiresharkWrapper",
    "get_wrapper",
]
