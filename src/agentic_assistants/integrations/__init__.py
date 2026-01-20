"""
Integrations module for Agentic Assistants.

This module provides integrations with external services:
- JupyterManager: Manage JupyterLab instances and kernels
- RemoteDevManager: Manage remote development servers
- SSHConnection: SSH connection wrapper

Example:
    >>> from agentic_assistants.integrations import JupyterManager, RemoteDevManager
    >>> 
    >>> jupyter = JupyterManager()
    >>> jupyter.ensure_running()
    >>> 
    >>> remote_dev = RemoteDevManager()
    >>> conn = remote_dev.create_ssh_connection("dev-1", {"host": "server.example.com"})
"""

from agentic_assistants.integrations.jupyter import JupyterManager
from agentic_assistants.integrations.jupyter_wrapper import (
    NotebookExecutor,
    NotebookResult,
    CellOutput,
    JupyterServerManager,
    NotebookManager,
)
from agentic_assistants.integrations.remote_dev import (
    RemoteDevManager,
    SSHConnection,
    SSHConnectionConfig,
    CodeServerClient,
    CodeServerConfig,
    CommandResult,
    SystemInfo,
)
from agentic_assistants.integrations.git_ops import (
    GitOperations,
    GitCredentials,
    RepoStatus,
    BranchInfo,
    CommitInfo,
    GitOperationResult,
    SSHKeyManager,
)

__all__ = [
    "JupyterManager",
    "NotebookExecutor",
    "NotebookResult",
    "CellOutput",
    "JupyterServerManager",
    "NotebookManager",
    "RemoteDevManager",
    "SSHConnection",
    "SSHConnectionConfig",
    "CodeServerClient",
    "CodeServerConfig",
    "CommandResult",
    "SystemInfo",
    "GitOperations",
    "GitCredentials",
    "RepoStatus",
    "BranchInfo",
    "CommitInfo",
    "GitOperationResult",
    "SSHKeyManager",
]



