"""
Integrations module for Agentic Assistants.

This module provides integrations with external services:
- JupyterServerManager: Manage JupyterLab instances and kernels
- RemoteDevManager: Manage remote development servers
- SSHConnection: SSH connection wrapper
- HuggingFaceHubIntegration: HuggingFace Hub model/dataset management

Example:
    >>> from agentic_assistants.integrations import JupyterServerManager, RemoteDevManager
    >>> 
    >>> jupyter = JupyterServerManager()
    >>> 
    >>> remote_dev = RemoteDevManager()
    >>> conn = remote_dev.create_ssh_connection("dev-1", {"host": "server.example.com"})
"""

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
from agentic_assistants.integrations.huggingface import (
    HuggingFaceHubIntegration,
    ModelCard,
    DatasetCard,
)
from agentic_assistants.integrations.pytorch_utils import (
    is_torch_available,
    is_cuda_available,
    is_mps_available,
    get_device,
    get_gpu_info,
    get_torch_info,
    estimate_model_memory,
    estimate_training_memory,
    clear_gpu_cache,
    get_dtype_for_device,
    get_optimal_batch_size,
)

__all__ = [
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
    # HuggingFace
    "HuggingFaceHubIntegration",
    "ModelCard",
    "DatasetCard",
    # PyTorch utilities
    "is_torch_available",
    "is_cuda_available",
    "is_mps_available",
    "get_device",
    "get_gpu_info",
    "get_torch_info",
    "estimate_model_memory",
    "estimate_training_memory",
    "clear_gpu_cache",
    "get_dtype_for_device",
    "get_optimal_batch_size",
]



