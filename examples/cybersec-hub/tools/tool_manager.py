"""
Tool Manager for cybersecurity tools.

Handles installation, execution, and management of security tools.
"""

import subprocess
import platform
import shutil
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import yaml

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class ToolStatus(str, Enum):
    """Status of a tool."""
    INSTALLED = "installed"
    NOT_INSTALLED = "not_installed"
    INSTALLING = "installing"
    ERROR = "error"
    UNKNOWN = "unknown"


class ExecutionMode(str, Enum):
    """Execution mode for tools."""
    DIRECT = "direct"
    DOCKER = "docker"
    CONTAINER = "container"


@dataclass
class ToolInfo:
    """Information about a security tool."""
    name: str
    description: str
    category: str
    os_support: List[str]
    capabilities: List[str]
    status: ToolStatus = ToolStatus.UNKNOWN
    version: Optional[str] = None
    path: Optional[str] = None
    wrapper: Optional[str] = None
    docker_image: Optional[str] = None
    docs_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result from tool execution."""
    tool: str
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    timestamp: str
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolManager:
    """
    Manages security tools lifecycle and execution.
    
    Handles:
    - Tool installation from registry
    - Tool execution (direct or containerized)
    - Version management
    - Wrapper access for programmatic use
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        tools_dir: Optional[Path] = None,
        registry_path: Optional[Path] = None
    ):
        """
        Initialize Tool Manager.
        
        Args:
            config: Configuration dictionary
            tools_dir: Directory for tool installations
            registry_path: Path to tool registry YAML
        """
        self.config = config or {}
        self.tools_dir = Path(tools_dir) if tools_dir else Path("./data/tools")
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        
        # Load tool registry
        self.registry_path = registry_path or Path(__file__).parent / "tool_registry.yaml"
        self.registry = self._load_registry()
        
        # Detect OS
        self.os_type = self._detect_os()
        
        # Execution mode
        self.default_execution_mode = ExecutionMode(
            self.config.get("containerized_execution", True) and "docker" or "direct"
        )
        
        # Cache for tool wrappers
        self._wrappers = {}
        
        logger.info(f"ToolManager initialized for {self.os_type}")
        logger.info(f"Default execution mode: {self.default_execution_mode}")
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load tool registry from YAML file."""
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                registry = yaml.safe_load(f)
                logger.debug(f"Loaded {len(registry.get('tools', {}))} tools from registry")
                return registry
        logger.warning(f"Registry not found: {self.registry_path}")
        return {"tools": {}, "categories": {}}
    
    def _detect_os(self) -> str:
        """Detect operating system."""
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        elif system in ["linux", "windows"]:
            return system
        return "unknown"
    
    def list_tools(
        self,
        category: Optional[str] = None,
        os_filter: Optional[str] = None,
        installed_only: bool = False
    ) -> List[ToolInfo]:
        """
        List available tools.
        
        Args:
            category: Filter by category
            os_filter: Filter by OS support
            installed_only: Only show installed tools
            
        Returns:
            List of ToolInfo objects
        """
        tools = []
        os_filter = os_filter or self.os_type
        
        for tool_id, tool_data in self.registry.get("tools", {}).items():
            # Filter by category
            if category and tool_data.get("category") != category:
                continue
            
            # Filter by OS
            if os_filter not in tool_data.get("os_support", []):
                continue
            
            # Check installation status
            status = self._check_tool_status(tool_id, tool_data)
            
            # Filter by installed
            if installed_only and status != ToolStatus.INSTALLED:
                continue
            
            tool_info = ToolInfo(
                name=tool_data.get("name", tool_id),
                description=tool_data.get("description", ""),
                category=tool_data.get("category", "unknown"),
                os_support=tool_data.get("os_support", []),
                capabilities=tool_data.get("capabilities", []),
                status=status,
                wrapper=tool_data.get("wrapper"),
                docker_image=tool_data.get("docker_image"),
                docs_url=tool_data.get("docs_url"),
                metadata={"tool_id": tool_id}
            )
            tools.append(tool_info)
        
        return tools
    
    def _check_tool_status(self, tool_id: str, tool_data: Dict[str, Any]) -> ToolStatus:
        """
        Check if a tool is installed.
        
        Args:
            tool_id: Tool identifier
            tool_data: Tool registry data
            
        Returns:
            ToolStatus
        """
        # Check if binary exists in PATH
        tool_binary = tool_id
        if shutil.which(tool_binary):
            return ToolStatus.INSTALLED
        
        # Check if Docker image is available
        if self.default_execution_mode == ExecutionMode.DOCKER:
            docker_image = tool_data.get("docker_image")
            if docker_image and self._check_docker_image(docker_image):
                return ToolStatus.INSTALLED
        
        return ToolStatus.NOT_INSTALLED
    
    def _check_docker_image(self, image: str) -> bool:
        """Check if Docker image exists locally."""
        try:
            result = subprocess.run(
                ["docker", "images", "-q", image],
                capture_output=True,
                text=True,
                timeout=5
            )
            return bool(result.stdout.strip())
        except Exception as e:
            logger.debug(f"Docker check failed: {e}")
            return False
    
    def install(self, tool_id: str) -> bool:
        """
        Install a tool.
        
        Args:
            tool_id: Tool identifier from registry
            
        Returns:
            True if installation succeeded
        """
        tool_data = self.registry.get("tools", {}).get(tool_id)
        if not tool_data:
            logger.error(f"Tool not found in registry: {tool_id}")
            return False
        
        # Check OS support
        if self.os_type not in tool_data.get("os_support", []):
            logger.error(f"Tool {tool_id} not supported on {self.os_type}")
            return False
        
        logger.info(f"Installing tool: {tool_id}")
        
        # Get installation command
        install_data = tool_data.get("install", {}).get(self.os_type)
        if not install_data:
            logger.error(f"No installation method for {tool_id} on {self.os_type}")
            return False
        
        # Determine installation method
        if isinstance(install_data, str):
            install_cmd = install_data
        elif isinstance(install_data, dict):
            # Try package managers in order of preference
            for pm in ["apt", "yum", "pacman", "snap"]:
                if pm in install_data:
                    install_cmd = install_data[pm]
                    break
            else:
                logger.error(f"No supported package manager for {tool_id}")
                return False
        else:
            logger.error(f"Invalid install data for {tool_id}")
            return False
        
        # Execute installation
        try:
            logger.info(f"Running: {install_cmd}")
            result = subprocess.run(
                install_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Tool {tool_id} installed successfully")
                return True
            else:
                logger.error(f"Installation failed: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            logger.error(f"Installation timeout for {tool_id}")
            return False
        except Exception as e:
            logger.error(f"Installation error for {tool_id}: {e}")
            return False
    
    def execute(
        self,
        tool: str,
        target: str,
        options: Optional[List[str]] = None,
        stealth: bool = False,
        mode: Optional[ExecutionMode] = None,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Execute a security tool.
        
        Args:
            tool: Tool identifier
            target: Target to scan/test
            options: Additional tool options
            stealth: Use stealth mode if available
            mode: Execution mode (direct or docker)
            timeout: Execution timeout in seconds
            
        Returns:
            ExecutionResult with output and metadata
        """
        mode = mode or self.default_execution_mode
        options = options or []
        timeout = timeout or self.config.get("execution_timeout", 1800)
        
        tool_data = self.registry.get("tools", {}).get(tool)
        if not tool_data:
            raise ValueError(f"Tool not found: {tool}")
        
        # Check tool status
        status = self._check_tool_status(tool, tool_data)
        if status != ToolStatus.INSTALLED:
            raise RuntimeError(f"Tool {tool} is not installed")
        
        # Build command
        if mode == ExecutionMode.DOCKER:
            command = self._build_docker_command(tool, tool_data, target, options)
        else:
            command = self._build_direct_command(tool, tool_data, target, options, stealth)
        
        # Execute command
        logger.info(f"Executing: {command}")
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            execution_result = ExecutionResult(
                tool=tool,
                command=command,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration=duration,
                timestamp=start_time.isoformat(),
                success=result.returncode == 0,
                metadata={
                    "target": target,
                    "options": options,
                    "mode": mode.value
                }
            )
            
            logger.info(f"Execution completed in {duration:.2f}s")
            return execution_result
        
        except subprocess.TimeoutExpired as e:
            logger.error(f"Execution timeout after {timeout}s")
            return ExecutionResult(
                tool=tool,
                command=command,
                exit_code=-1,
                stdout=e.stdout.decode() if e.stdout else "",
                stderr=f"Timeout after {timeout}s",
                duration=timeout,
                timestamp=start_time.isoformat(),
                success=False,
                metadata={"error": "timeout"}
            )
        
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return ExecutionResult(
                tool=tool,
                command=command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration=0,
                timestamp=start_time.isoformat(),
                success=False,
                metadata={"error": str(e)}
            )
    
    def _build_direct_command(
        self,
        tool: str,
        tool_data: Dict[str, Any],
        target: str,
        options: List[str],
        stealth: bool
    ) -> str:
        """Build command for direct execution."""
        cmd_parts = [tool]
        cmd_parts.extend(options)
        cmd_parts.append(target)
        return " ".join(cmd_parts)
    
    def _build_docker_command(
        self,
        tool: str,
        tool_data: Dict[str, Any],
        target: str,
        options: List[str]
    ) -> str:
        """Build command for Docker execution."""
        docker_image = tool_data.get("docker_image")
        if not docker_image:
            raise ValueError(f"No Docker image available for {tool}")
        
        # Build Docker command
        cmd_parts = [
            "docker", "run", "--rm",
            "--network", "host",
            docker_image
        ]
        cmd_parts.extend(options)
        cmd_parts.append(target)
        
        return " ".join(cmd_parts)
    
    def get_wrapper(self, tool: str):
        """
        Get Python wrapper for a tool.
        
        Args:
            tool: Tool identifier
            
        Returns:
            Tool wrapper instance
        """
        if tool in self._wrappers:
            return self._wrappers[tool]
        
        tool_data = self.registry.get("tools", {}).get(tool)
        if not tool_data:
            raise ValueError(f"Tool not found: {tool}")
        
        wrapper_path = tool_data.get("wrapper")
        if not wrapper_path:
            raise ValueError(f"No wrapper available for {tool}")
        
        # Dynamically import wrapper
        try:
            module_path, class_name = wrapper_path.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            wrapper_class = getattr(module, class_name)
            
            wrapper = wrapper_class(
                tool_manager=self,
                config=self.config
            )
            
            self._wrappers[tool] = wrapper
            return wrapper
        
        except Exception as e:
            logger.error(f"Failed to load wrapper for {tool}: {e}")
            raise
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get available tool categories."""
        categories = []
        for cat_id, cat_data in self.registry.get("categories", {}).items():
            categories.append({
                "id": cat_id,
                "name": cat_data.get("name", cat_id),
                "description": cat_data.get("description", ""),
                "icon": cat_data.get("icon", "tool")
            })
        return categories
    
    def verify_installation(self, tool: str) -> Dict[str, Any]:
        """
        Verify tool installation and get version info.
        
        Args:
            tool: Tool identifier
            
        Returns:
            Dict with verification results
        """
        tool_data = self.registry.get("tools", {}).get(tool)
        if not tool_data:
            return {"success": False, "error": "Tool not found"}
        
        # Check if binary exists
        if shutil.which(tool):
            # Try to get version
            try:
                result = subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version = result.stdout.strip() or result.stderr.strip()
                
                return {
                    "success": True,
                    "installed": True,
                    "version": version,
                    "path": shutil.which(tool)
                }
            except Exception as e:
                return {
                    "success": True,
                    "installed": True,
                    "version": "unknown",
                    "path": shutil.which(tool),
                    "error": str(e)
                }
        
        return {"success": False, "installed": False}
    
    def uninstall(self, tool: str) -> bool:
        """
        Uninstall a tool.
        
        Args:
            tool: Tool identifier
            
        Returns:
            True if uninstallation succeeded
        """
        logger.warning(f"Uninstall not fully implemented for {tool}")
        # Note: Uninstallation is complex and OS-specific
        # Would need to track installation method and reverse it
        return False


__all__ = ["ToolManager", "ToolInfo", "ExecutionResult", "ToolStatus", "ExecutionMode"]
