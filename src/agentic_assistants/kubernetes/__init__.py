"""
Kubernetes integration for Agentic Assistants.

This module provides comprehensive Kubernetes cluster management including:
- Cluster connection and health monitoring
- Deployment management for agents, flows, and models
- MinIO/S3 storage integration
- LLM model serving deployment

Example:
    >>> from agentic_assistants.kubernetes import KubernetesClient, DeploymentManager
    >>> 
    >>> client = KubernetesClient()
    >>> cluster_info = await client.get_cluster_info()
    >>> print(f"Cluster: {cluster_info.name}, Nodes: {cluster_info.node_count}")
    >>> 
    >>> deployer = DeploymentManager(client)
    >>> await deployer.deploy_agent(agent_config)
"""

from agentic_assistants.kubernetes.client import KubernetesClient, discover_rpi_kubeconfig
from agentic_assistants.kubernetes.deployments import DeploymentManager
from agentic_assistants.kubernetes.models import (
    ClusterInfo,
    NodeInfo,
    NodeMetrics,
    NodeStatus,
    PodInfo,
    PodPhase,
    ServiceInfo,
    DeploymentInfo,
    DeploymentStatus,
    DeploymentConfig,
    ModelDeploymentConfig,
    ModelServingType,
    AgentDeploymentConfig,
    FlowDeploymentConfig,
    ResourceRequirements,
    ClusterConnectionConfig,
)
from agentic_assistants.kubernetes.storage import MinIOStorage
from agentic_assistants.kubernetes.model_serving import ModelServingManager

__all__ = [
    # Client
    "KubernetesClient",
    "discover_rpi_kubeconfig",
    # Deployment
    "DeploymentManager",
    # Model Serving
    "ModelServingManager",
    # Models
    "ClusterInfo",
    "NodeInfo",
    "NodeMetrics",
    "NodeStatus",
    "PodInfo",
    "PodPhase",
    "ServiceInfo",
    "DeploymentInfo",
    "DeploymentStatus",
    "DeploymentConfig",
    "ModelDeploymentConfig",
    "ModelServingType",
    "AgentDeploymentConfig",
    "FlowDeploymentConfig",
    "ResourceRequirements",
    "ClusterConnectionConfig",
    # Storage
    "MinIOStorage",
]
