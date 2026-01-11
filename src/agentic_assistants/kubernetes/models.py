"""
Pydantic models for Kubernetes resources.

This module defines data models for Kubernetes cluster resources,
deployments, and model serving configurations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class NodeStatus(str, Enum):
    """Status of a Kubernetes node."""
    READY = "Ready"
    NOT_READY = "NotReady"
    UNKNOWN = "Unknown"


class PodPhase(str, Enum):
    """Phase of a Kubernetes pod."""
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class DeploymentStatus(str, Enum):
    """Status of a Kubernetes deployment."""
    PENDING = "Pending"
    RUNNING = "Running"
    SCALING = "Scaling"
    UPDATING = "Updating"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class ModelServingType(str, Enum):
    """Type of model serving deployment."""
    OLLAMA = "ollama"
    VLLM = "vllm"
    TGI = "tgi"  # Text Generation Inference
    CUSTOM = "custom"


class NodeMetrics(BaseModel):
    """Resource metrics for a Kubernetes node."""
    cpu_capacity: str = Field(description="Total CPU capacity")
    cpu_allocatable: str = Field(description="Allocatable CPU")
    cpu_usage: Optional[str] = Field(default=None, description="Current CPU usage")
    memory_capacity: str = Field(description="Total memory capacity")
    memory_allocatable: str = Field(description="Allocatable memory")
    memory_usage: Optional[str] = Field(default=None, description="Current memory usage")
    pods_capacity: int = Field(description="Maximum pods")
    pods_running: int = Field(description="Currently running pods")


class NodeInfo(BaseModel):
    """Information about a Kubernetes node."""
    name: str = Field(description="Node name")
    status: NodeStatus = Field(description="Node status")
    roles: list[str] = Field(default_factory=list, description="Node roles")
    ip_address: str = Field(description="Internal IP address")
    architecture: str = Field(description="CPU architecture")
    os_image: str = Field(description="Operating system image")
    kernel_version: str = Field(description="Kernel version")
    container_runtime: str = Field(description="Container runtime version")
    kubelet_version: str = Field(description="Kubelet version")
    created_at: datetime = Field(description="Creation timestamp")
    labels: dict[str, str] = Field(default_factory=dict, description="Node labels")
    taints: list[str] = Field(default_factory=list, description="Node taints")
    conditions: dict[str, str] = Field(default_factory=dict, description="Node conditions")
    metrics: Optional[NodeMetrics] = Field(default=None, description="Resource metrics")


class ClusterInfo(BaseModel):
    """Information about the Kubernetes cluster."""
    name: str = Field(description="Cluster name")
    version: str = Field(description="Kubernetes version")
    node_count: int = Field(description="Total number of nodes")
    ready_nodes: int = Field(description="Number of ready nodes")
    total_pods: int = Field(description="Total pods in cluster")
    running_pods: int = Field(description="Running pods")
    total_cpu: str = Field(description="Total CPU capacity")
    total_memory: str = Field(description="Total memory capacity")
    namespaces: list[str] = Field(default_factory=list, description="Available namespaces")
    nodes: list[NodeInfo] = Field(default_factory=list, description="Node information")
    is_connected: bool = Field(default=True, description="Connection status")
    context: Optional[str] = Field(default=None, description="Current context")


class PodInfo(BaseModel):
    """Information about a Kubernetes pod."""
    name: str = Field(description="Pod name")
    namespace: str = Field(description="Pod namespace")
    phase: PodPhase = Field(description="Pod phase")
    node_name: Optional[str] = Field(default=None, description="Node running the pod")
    ip_address: Optional[str] = Field(default=None, description="Pod IP address")
    containers: list[str] = Field(default_factory=list, description="Container names")
    restarts: int = Field(default=0, description="Total restart count")
    created_at: datetime = Field(description="Creation timestamp")
    labels: dict[str, str] = Field(default_factory=dict, description="Pod labels")


class ServiceInfo(BaseModel):
    """Information about a Kubernetes service."""
    name: str = Field(description="Service name")
    namespace: str = Field(description="Service namespace")
    type: str = Field(description="Service type (ClusterIP, NodePort, LoadBalancer)")
    cluster_ip: Optional[str] = Field(default=None, description="Cluster IP")
    external_ip: Optional[str] = Field(default=None, description="External IP")
    ports: list[dict[str, Any]] = Field(default_factory=list, description="Service ports")
    selector: dict[str, str] = Field(default_factory=dict, description="Pod selector")
    created_at: datetime = Field(description="Creation timestamp")


class DeploymentInfo(BaseModel):
    """Information about a Kubernetes deployment."""
    name: str = Field(description="Deployment name")
    namespace: str = Field(description="Deployment namespace")
    status: DeploymentStatus = Field(description="Deployment status")
    replicas: int = Field(description="Desired replicas")
    ready_replicas: int = Field(default=0, description="Ready replicas")
    available_replicas: int = Field(default=0, description="Available replicas")
    image: str = Field(description="Container image")
    created_at: datetime = Field(description="Creation timestamp")
    labels: dict[str, str] = Field(default_factory=dict, description="Deployment labels")
    conditions: list[dict[str, Any]] = Field(default_factory=list, description="Deployment conditions")
    # Agentic-specific fields
    deployment_type: Optional[str] = Field(default=None, description="Type: agent, flow, model, etc.")
    source_id: Optional[str] = Field(default=None, description="Source agent/flow ID")


class ResourceRequirements(BaseModel):
    """Resource requirements for a deployment."""
    cpu_request: str = Field(default="100m", description="CPU request")
    cpu_limit: str = Field(default="1000m", description="CPU limit")
    memory_request: str = Field(default="256Mi", description="Memory request")
    memory_limit: str = Field(default="1Gi", description="Memory limit")
    gpu_request: Optional[int] = Field(default=None, description="GPU request")


class DeploymentConfig(BaseModel):
    """Configuration for creating a deployment."""
    name: str = Field(description="Deployment name")
    namespace: str = Field(default="agentic-workloads", description="Target namespace")
    image: str = Field(description="Container image")
    replicas: int = Field(default=1, description="Number of replicas")
    port: Optional[int] = Field(default=None, description="Container port")
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    labels: dict[str, str] = Field(default_factory=dict, description="Additional labels")
    resources: Optional[ResourceRequirements] = Field(default=None, description="Resource requirements")
    node_selector: Optional[dict[str, str]] = Field(default=None, description="Node selector")
    create_service: bool = Field(default=True, description="Create associated service")
    service_type: str = Field(default="ClusterIP", description="Service type")
    # Agentic-specific
    deployment_type: str = Field(default="custom", description="Type: agent, flow, model, custom")
    source_id: Optional[str] = Field(default=None, description="Source agent/flow ID")
    config_map_data: Optional[dict[str, str]] = Field(default=None, description="ConfigMap data")
    secrets: Optional[dict[str, str]] = Field(default=None, description="Secret data")


class ModelDeploymentConfig(BaseModel):
    """Configuration for deploying an LLM model."""
    name: str = Field(description="Deployment name")
    model_name: str = Field(description="Model name/identifier")
    serving_type: ModelServingType = Field(default=ModelServingType.OLLAMA, description="Serving type")
    namespace: str = Field(default="model-serving", description="Target namespace")
    replicas: int = Field(default=1, description="Number of replicas")
    resources: Optional[ResourceRequirements] = Field(default=None, description="Resource requirements")
    # Model-specific settings
    model_path: Optional[str] = Field(default=None, description="Path to model files in storage")
    quantization: Optional[str] = Field(default=None, description="Quantization type (e.g., q4_0, q8_0)")
    context_length: int = Field(default=4096, description="Context window size")
    gpu_layers: Optional[int] = Field(default=None, description="Number of GPU layers")
    # Service settings
    create_ingress: bool = Field(default=False, description="Create ingress for external access")
    ingress_host: Optional[str] = Field(default=None, description="Ingress hostname")


class AgentDeploymentConfig(BaseModel):
    """Configuration for deploying an agent to Kubernetes."""
    agent_id: str = Field(description="Agent ID from control panel")
    name: str = Field(description="Deployment name")
    namespace: str = Field(default="agentic-workloads", description="Target namespace")
    replicas: int = Field(default=1, description="Number of replicas")
    resources: Optional[ResourceRequirements] = Field(default=None, description="Resource requirements")
    # Agent configuration
    framework: str = Field(default="crewai", description="Agent framework (crewai, langgraph)")
    model_endpoint: Optional[str] = Field(default=None, description="LLM endpoint to use")
    tools: list[str] = Field(default_factory=list, description="Tools to include")
    env_vars: dict[str, str] = Field(default_factory=dict, description="Environment variables")


class FlowDeploymentConfig(BaseModel):
    """Configuration for deploying a flow to Kubernetes."""
    flow_id: str = Field(description="Flow ID from control panel")
    name: str = Field(description="Deployment name")
    namespace: str = Field(default="agentic-workloads", description="Target namespace")
    replicas: int = Field(default=1, description="Number of replicas")
    resources: Optional[ResourceRequirements] = Field(default=None, description="Resource requirements")
    # Flow configuration
    framework: str = Field(default="langgraph", description="Flow framework")
    model_endpoint: Optional[str] = Field(default=None, description="LLM endpoint to use")
    state_backend: str = Field(default="minio", description="State backend (minio, redis)")
    env_vars: dict[str, str] = Field(default_factory=dict, description="Environment variables")


class ClusterConnectionConfig(BaseModel):
    """Configuration for connecting to a Kubernetes cluster."""
    kubeconfig_path: Optional[str] = Field(default=None, description="Path to kubeconfig")
    context: Optional[str] = Field(default=None, description="Kubernetes context")
    cluster_endpoint: Optional[str] = Field(default=None, description="Direct API endpoint")
    token: Optional[str] = Field(default=None, description="Bearer token")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
