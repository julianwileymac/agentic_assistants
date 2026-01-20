"""
Remote Development Server Integration.

This module provides integration with remote development servers:
- SSH connections with key management
- VS Code Server / code-server integration
- JupyterHub connection support
- Resource monitoring and health checks

Example:
    >>> from agentic_assistants.integrations.remote_dev import RemoteDevManager
    >>> 
    >>> manager = RemoteDevManager()
    >>> 
    >>> # Connect to a remote server via SSH
    >>> conn = manager.create_ssh_connection({
    ...     "host": "dev-server.example.com",
    ...     "username": "developer",
    ...     "key_file": "~/.ssh/id_rsa",
    ... })
    >>> 
    >>> # Execute commands
    >>> result = conn.execute("ls -la")
    >>> print(result.stdout)
    >>> 
    >>> # Check server resources
    >>> resources = conn.get_system_info()
"""

import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SSHConnectionConfig:
    """SSH connection configuration."""
    host: str
    port: int = 22
    username: str = ""
    password: Optional[str] = None
    key_file: Optional[str] = None
    key_passphrase: Optional[str] = None
    timeout: int = 30
    keepalive_interval: int = 60
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding sensitive data)."""
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "has_password": self.password is not None,
            "key_file": self.key_file,
            "timeout": self.timeout,
        }


@dataclass
class CommandResult:
    """Result of a remote command execution."""
    command: str
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    
    @property
    def success(self) -> bool:
        return self.exit_code == 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "success": self.success,
            "duration_ms": self.duration_ms,
        }


@dataclass
class SystemInfo:
    """Remote system information."""
    hostname: str = ""
    os_type: str = ""
    os_version: str = ""
    kernel: str = ""
    cpu_count: int = 0
    memory_total_gb: float = 0.0
    memory_available_gb: float = 0.0
    disk_total_gb: float = 0.0
    disk_available_gb: float = 0.0
    load_average: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    uptime_hours: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hostname": self.hostname,
            "os_type": self.os_type,
            "os_version": self.os_version,
            "kernel": self.kernel,
            "cpu_count": self.cpu_count,
            "memory_total_gb": self.memory_total_gb,
            "memory_available_gb": self.memory_available_gb,
            "disk_total_gb": self.disk_total_gb,
            "disk_available_gb": self.disk_available_gb,
            "load_average": self.load_average,
            "uptime_hours": self.uptime_hours,
        }


@dataclass
class SSHTunnelConfig:
    """SSH tunnel configuration."""
    local_port: int
    remote_host: str
    remote_port: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "local_port": self.local_port,
            "remote_host": self.remote_host,
            "remote_port": self.remote_port,
        }


class SSHConnection:
    """
    SSH connection wrapper with command execution and tunneling.
    
    Provides:
    - Command execution with timeout
    - File transfer (SFTP)
    - Port forwarding
    - System monitoring
    """
    
    def __init__(self, config: SSHConnectionConfig):
        """
        Initialize SSH connection.
        
        Args:
            config: SSH connection configuration
        """
        self.config = config
        self._client = None
        self._sftp = None
        self._tunnels: List[Any] = []
    
    def connect(self) -> bool:
        """
        Establish SSH connection.
        
        Returns:
            True if connected successfully
        """
        try:
            import paramiko
        except ImportError:
            raise ImportError("paramiko not installed. Run: pip install paramiko")
        
        try:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                "hostname": self.config.host,
                "port": self.config.port,
                "username": self.config.username,
                "timeout": self.config.timeout,
            }
            
            if self.config.password:
                connect_kwargs["password"] = self.config.password
            elif self.config.key_file:
                key_path = Path(self.config.key_file).expanduser()
                if self.config.key_passphrase:
                    key = paramiko.RSAKey.from_private_key_file(
                        str(key_path),
                        password=self.config.key_passphrase,
                    )
                else:
                    key = paramiko.RSAKey.from_private_key_file(str(key_path))
                connect_kwargs["pkey"] = key
            
            self._client.connect(**connect_kwargs)
            
            # Set keepalive
            transport = self._client.get_transport()
            if transport:
                transport.set_keepalive(self.config.keepalive_interval)
            
            logger.info(f"Connected to {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            logger.error(f"SSH connection failed: {e}")
            self._client = None
            return False
    
    def disconnect(self) -> None:
        """Close SSH connection."""
        # Close tunnels
        for tunnel in self._tunnels:
            try:
                tunnel.close()
            except Exception:
                pass
        self._tunnels.clear()
        
        # Close SFTP
        if self._sftp:
            try:
                self._sftp.close()
            except Exception:
                pass
            self._sftp = None
        
        # Close client
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
        
        logger.info(f"Disconnected from {self.config.host}")
    
    @property
    def is_connected(self) -> bool:
        """Check if connection is active."""
        if not self._client:
            return False
        
        transport = self._client.get_transport()
        return transport is not None and transport.is_active()
    
    def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        get_pty: bool = False,
    ) -> CommandResult:
        """
        Execute a command on the remote server.
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds (uses config default if None)
            get_pty: Whether to request a PTY
            
        Returns:
            CommandResult with output and exit code
        """
        if not self.is_connected:
            raise RuntimeError("Not connected")
        
        timeout = timeout or self.config.timeout
        start_time = time.time()
        
        try:
            stdin, stdout, stderr = self._client.exec_command(
                command,
                timeout=timeout,
                get_pty=get_pty,
            )
            
            exit_code = stdout.channel.recv_exit_status()
            stdout_str = stdout.read().decode("utf-8", errors="replace")
            stderr_str = stderr.read().decode("utf-8", errors="replace")
            
            duration_ms = (time.time() - start_time) * 1000
            
            return CommandResult(
                command=command,
                stdout=stdout_str,
                stderr=stderr_str,
                exit_code=exit_code,
                duration_ms=duration_ms,
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return CommandResult(
                command=command,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                duration_ms=duration_ms,
            )
    
    def get_sftp(self):
        """Get SFTP client for file operations."""
        if not self.is_connected:
            raise RuntimeError("Not connected")
        
        if not self._sftp:
            self._sftp = self._client.open_sftp()
        
        return self._sftp
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
    ) -> bool:
        """
        Upload a file to the remote server.
        
        Args:
            local_path: Local file path
            remote_path: Remote destination path
            
        Returns:
            True if successful
        """
        try:
            sftp = self.get_sftp()
            sftp.put(str(Path(local_path).expanduser()), remote_path)
            logger.debug(f"Uploaded {local_path} to {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False
    
    def download_file(
        self,
        remote_path: str,
        local_path: str,
    ) -> bool:
        """
        Download a file from the remote server.
        
        Args:
            remote_path: Remote file path
            local_path: Local destination path
            
        Returns:
            True if successful
        """
        try:
            sftp = self.get_sftp()
            local = Path(local_path).expanduser()
            local.parent.mkdir(parents=True, exist_ok=True)
            sftp.get(remote_path, str(local))
            logger.debug(f"Downloaded {remote_path} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def get_system_info(self) -> SystemInfo:
        """
        Get system information from the remote server.
        
        Returns:
            SystemInfo with resource details
        """
        info = SystemInfo()
        
        # Hostname
        result = self.execute("hostname")
        if result.success:
            info.hostname = result.stdout.strip()
        
        # OS info
        result = self.execute("cat /etc/os-release 2>/dev/null || uname -s")
        if result.success:
            output = result.stdout
            if "ID=" in output:
                for line in output.split("\n"):
                    if line.startswith("ID="):
                        info.os_type = line.split("=")[1].strip('"')
                    elif line.startswith("VERSION="):
                        info.os_version = line.split("=")[1].strip('"')
            else:
                info.os_type = output.strip()
        
        # Kernel
        result = self.execute("uname -r")
        if result.success:
            info.kernel = result.stdout.strip()
        
        # CPU count
        result = self.execute("nproc")
        if result.success:
            try:
                info.cpu_count = int(result.stdout.strip())
            except ValueError:
                pass
        
        # Memory
        result = self.execute("free -b")
        if result.success:
            for line in result.stdout.split("\n"):
                if line.startswith("Mem:"):
                    parts = line.split()
                    if len(parts) >= 4:
                        info.memory_total_gb = int(parts[1]) / (1024**3)
                        info.memory_available_gb = int(parts[3]) / (1024**3)
        
        # Disk
        result = self.execute("df -B1 / | tail -1")
        if result.success:
            parts = result.stdout.split()
            if len(parts) >= 4:
                info.disk_total_gb = int(parts[1]) / (1024**3)
                info.disk_available_gb = int(parts[3]) / (1024**3)
        
        # Load average
        result = self.execute("cat /proc/loadavg")
        if result.success:
            parts = result.stdout.split()
            if len(parts) >= 3:
                info.load_average = (
                    float(parts[0]),
                    float(parts[1]),
                    float(parts[2]),
                )
        
        # Uptime
        result = self.execute("cat /proc/uptime")
        if result.success:
            try:
                info.uptime_hours = float(result.stdout.split()[0]) / 3600
            except (ValueError, IndexError):
                pass
        
        return info
    
    def create_tunnel(
        self,
        local_port: int,
        remote_host: str,
        remote_port: int,
    ) -> Optional[SSHTunnelConfig]:
        """
        Create an SSH tunnel for port forwarding.
        
        Args:
            local_port: Local port to bind
            remote_host: Remote host to forward to
            remote_port: Remote port to forward to
            
        Returns:
            Tunnel configuration if successful
        """
        if not self.is_connected:
            raise RuntimeError("Not connected")
        
        try:
            from sshtunnel import SSHTunnelForwarder
            
            tunnel = SSHTunnelForwarder(
                (self.config.host, self.config.port),
                ssh_username=self.config.username,
                ssh_password=self.config.password,
                ssh_pkey=self.config.key_file,
                remote_bind_address=(remote_host, remote_port),
                local_bind_address=("127.0.0.1", local_port),
            )
            tunnel.start()
            
            self._tunnels.append(tunnel)
            
            config = SSHTunnelConfig(
                local_port=local_port,
                remote_host=remote_host,
                remote_port=remote_port,
            )
            
            logger.info(f"Created tunnel: localhost:{local_port} -> {remote_host}:{remote_port}")
            return config
            
        except ImportError:
            logger.warning("sshtunnel not installed. Install with: pip install sshtunnel")
            return None
        except Exception as e:
            logger.error(f"Failed to create tunnel: {e}")
            return None


@dataclass
class CodeServerConfig:
    """VS Code Server / code-server configuration."""
    host: str
    port: int = 8080
    password: Optional[str] = None
    use_tls: bool = False
    cert_file: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "has_password": self.password is not None,
            "use_tls": self.use_tls,
            "url": self.url,
        }
    
    @property
    def url(self) -> str:
        scheme = "https" if self.use_tls else "http"
        return f"{scheme}://{self.host}:{self.port}"


class CodeServerClient:
    """
    Client for interacting with VS Code Server / code-server.
    
    Provides:
    - Connection testing
    - Session management
    - Health monitoring
    """
    
    def __init__(self, config: CodeServerConfig):
        """
        Initialize code-server client.
        
        Args:
            config: Code-server configuration
        """
        self.config = config
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check code-server health.
        
        Returns:
            Health status dictionary
        """
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.config.url}/healthz")
                
                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "url": self.config.url,
                }
        except Exception as e:
            return {
                "status": "unreachable",
                "error": str(e),
                "url": self.config.url,
            }
    
    def get_connection_url(self) -> str:
        """Get the URL for connecting to code-server."""
        return self.config.url


class RemoteDevManager:
    """
    Manager for remote development server connections.
    
    Handles:
    - SSH connection lifecycle
    - Code-server integration
    - JupyterHub connections
    - Health monitoring
    """
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """
        Initialize the remote dev manager.
        
        Args:
            config: Configuration instance
        """
        self.config = config or AgenticConfig()
        self._connections: Dict[str, SSHConnection] = {}
        self._code_servers: Dict[str, CodeServerClient] = {}
    
    def create_ssh_connection(
        self,
        connection_id: str,
        config: Dict[str, Any],
    ) -> SSHConnection:
        """
        Create and store an SSH connection.
        
        Args:
            connection_id: Unique identifier for the connection
            config: Connection configuration
            
        Returns:
            SSHConnection instance
        """
        ssh_config = SSHConnectionConfig(
            host=config.get("host", ""),
            port=config.get("port", 22),
            username=config.get("username", ""),
            password=config.get("password"),
            key_file=config.get("key_file"),
            key_passphrase=config.get("key_passphrase"),
            timeout=config.get("timeout", 30),
            keepalive_interval=config.get("keepalive_interval", 60),
        )
        
        connection = SSHConnection(ssh_config)
        self._connections[connection_id] = connection
        
        return connection
    
    def get_connection(self, connection_id: str) -> Optional[SSHConnection]:
        """Get an existing SSH connection."""
        return self._connections.get(connection_id)
    
    def remove_connection(self, connection_id: str) -> bool:
        """
        Remove and disconnect an SSH connection.
        
        Args:
            connection_id: Connection identifier
            
        Returns:
            True if removed
        """
        connection = self._connections.pop(connection_id, None)
        if connection:
            connection.disconnect()
            return True
        return False
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """List all connections with their status."""
        return [
            {
                "id": conn_id,
                "host": conn.config.host,
                "port": conn.config.port,
                "username": conn.config.username,
                "is_connected": conn.is_connected,
            }
            for conn_id, conn in self._connections.items()
        ]
    
    def register_code_server(
        self,
        server_id: str,
        config: Dict[str, Any],
    ) -> CodeServerClient:
        """
        Register a code-server instance.
        
        Args:
            server_id: Unique identifier for the server
            config: Server configuration
            
        Returns:
            CodeServerClient instance
        """
        server_config = CodeServerConfig(
            host=config.get("host", "localhost"),
            port=config.get("port", 8080),
            password=config.get("password"),
            use_tls=config.get("use_tls", False),
            cert_file=config.get("cert_file"),
        )
        
        client = CodeServerClient(server_config)
        self._code_servers[server_id] = client
        
        return client
    
    def get_code_server(self, server_id: str) -> Optional[CodeServerClient]:
        """Get a registered code-server client."""
        return self._code_servers.get(server_id)
    
    async def check_all_health(self) -> Dict[str, Any]:
        """
        Check health of all remote dev resources.
        
        Returns:
            Health status for all connections and servers
        """
        health = {
            "ssh_connections": {},
            "code_servers": {},
            "checked_at": datetime.utcnow().isoformat(),
        }
        
        # Check SSH connections
        for conn_id, conn in self._connections.items():
            health["ssh_connections"][conn_id] = {
                "host": conn.config.host,
                "is_connected": conn.is_connected,
            }
            
            if conn.is_connected:
                try:
                    result = conn.execute("echo 'ping'", timeout=5)
                    health["ssh_connections"][conn_id]["responsive"] = result.success
                except Exception:
                    health["ssh_connections"][conn_id]["responsive"] = False
        
        # Check code-servers
        for server_id, client in self._code_servers.items():
            health["code_servers"][server_id] = await client.check_health()
        
        return health
