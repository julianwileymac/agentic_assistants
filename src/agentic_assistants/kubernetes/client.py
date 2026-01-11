"""
Kubernetes client wrapper for Agentic Assistants.

Provides a high-level interface for Kubernetes cluster operations,
wrapping the kubernetes-python library with async support.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from agentic_assistants.config import AgenticConfig
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
    ClusterConnectionConfig,
)

logger = logging.getLogger(__name__)


class KubernetesClient:
    """
    High-level Kubernetes client for cluster operations.
    
    This client wraps the kubernetes-python library and provides
    async methods for common cluster operations.
    
    Example:
        >>> client = KubernetesClient()
        >>> cluster_info = await client.get_cluster_info()
        >>> nodes = await client.list_nodes()
    """

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        connection_config: Optional[ClusterConnectionConfig] = None,
    ):
        """
        Initialize the Kubernetes client.
        
        Args:
            config: Agentic configuration instance
            connection_config: Direct connection configuration (overrides config)
        """
        self.config = config or AgenticConfig()
        self.connection_config = connection_config
        self._core_api = None
        self._apps_api = None
        self._version_api = None
        self._custom_api = None
        self._initialized = False
        self._k8s_available = False
        
        # Check if kubernetes library is available
        try:
            from kubernetes import client, config as k8s_config
            self._k8s_available = True
        except ImportError:
            logger.warning("kubernetes library not installed. K8s features disabled.")

    def _initialize(self) -> bool:
        """Initialize Kubernetes client connection."""
        if self._initialized:
            return self._k8s_available
        
        if not self._k8s_available:
            self._initialized = True
            return False
        
        try:
            from kubernetes import client, config as k8s_config
            
            # Determine connection method
            conn = self.connection_config
            k8s_settings = self.config.kubernetes
            
            kubeconfig_path = conn.kubeconfig_path if conn else k8s_settings.kubeconfig_path
            context = conn.context if conn else k8s_settings.context
            cluster_endpoint = conn.cluster_endpoint if conn else k8s_settings.cluster_endpoint
            token = conn.token if conn else k8s_settings.cluster_token
            
            if cluster_endpoint and token:
                # Direct connection with endpoint and token
                configuration = client.Configuration()
                configuration.host = cluster_endpoint
                configuration.api_key = {"authorization": f"Bearer {token}"}
                if conn and not conn.verify_ssl:
                    configuration.verify_ssl = False
                elif not k8s_settings.verify_ssl:
                    configuration.verify_ssl = False
                client.Configuration.set_default(configuration)
            elif kubeconfig_path:
                # Load from specific kubeconfig file
                k8s_config.load_kube_config(
                    config_file=kubeconfig_path,
                    context=context,
                )
            else:
                # Try in-cluster config first, fall back to default kubeconfig
                try:
                    k8s_config.load_incluster_config()
                except k8s_config.ConfigException:
                    k8s_config.load_kube_config(context=context)
            
            self._core_api = client.CoreV1Api()
            self._apps_api = client.AppsV1Api()
            self._version_api = client.VersionApi()
            self._custom_api = client.CustomObjectsApi()
            self._initialized = True
            logger.info("Kubernetes client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            self._initialized = True
            return False

    @property
    def is_available(self) -> bool:
        """Check if Kubernetes client is available and connected."""
        self._initialize()
        return self._k8s_available and self._core_api is not None

    @property
    def core_api(self):
        """Get CoreV1Api instance."""
        self._initialize()
        return self._core_api

    @property
    def apps_api(self):
        """Get AppsV1Api instance."""
        self._initialize()
        return self._apps_api

    async def get_cluster_info(self) -> ClusterInfo:
        """
        Get overall cluster information.
        
        Returns:
            ClusterInfo with cluster details and node information
        """
        if not self._initialize():
            return ClusterInfo(
                name="disconnected",
                version="unknown",
                node_count=0,
                ready_nodes=0,
                total_pods=0,
                running_pods=0,
                total_cpu="0",
                total_memory="0",
                is_connected=False,
            )
        
        try:
            # Get Kubernetes version
            version_info = self._version_api.get_code()
            k8s_version = version_info.git_version
            
            # Get nodes
            nodes = await self.list_nodes()
            ready_nodes = sum(1 for n in nodes if n.status == NodeStatus.READY)
            
            # Calculate total resources
            total_cpu = 0.0
            total_memory = 0.0
            for node in nodes:
                if node.metrics:
                    # Parse CPU (e.g., "4" or "4000m")
                    cpu_str = node.metrics.cpu_capacity
                    if cpu_str.endswith("m"):
                        total_cpu += int(cpu_str[:-1]) / 1000
                    else:
                        try:
                            total_cpu += int(cpu_str)
                        except ValueError:
                            pass
                    
                    # Parse memory (e.g., "8Gi" or "8192Mi")
                    mem_str = node.metrics.memory_capacity
                    if mem_str.endswith("Gi"):
                        total_memory += float(mem_str[:-2])
                    elif mem_str.endswith("Mi"):
                        total_memory += float(mem_str[:-2]) / 1024
                    elif mem_str.endswith("Ki"):
                        total_memory += float(mem_str[:-2]) / (1024 * 1024)
            
            # Get pods
            pods = self._core_api.list_pod_for_all_namespaces()
            total_pods = len(pods.items)
            running_pods = sum(1 for p in pods.items if p.status.phase == "Running")
            
            # Get namespaces
            namespaces = self._core_api.list_namespace()
            namespace_names = [ns.metadata.name for ns in namespaces.items]
            
            # Get cluster name from context
            cluster_name = self.config.kubernetes.context or "kubernetes"
            
            return ClusterInfo(
                name=cluster_name,
                version=k8s_version,
                node_count=len(nodes),
                ready_nodes=ready_nodes,
                total_pods=total_pods,
                running_pods=running_pods,
                total_cpu=f"{total_cpu:.0f}",
                total_memory=f"{total_memory:.1f}Gi",
                namespaces=namespace_names,
                nodes=nodes,
                is_connected=True,
                context=self.config.kubernetes.context,
            )
            
        except Exception as e:
            logger.error(f"Failed to get cluster info: {e}")
            return ClusterInfo(
                name="error",
                version="unknown",
                node_count=0,
                ready_nodes=0,
                total_pods=0,
                running_pods=0,
                total_cpu="0",
                total_memory="0",
                is_connected=False,
            )

    async def list_nodes(self) -> list[NodeInfo]:
        """
        List all cluster nodes with details.
        
        Returns:
            List of NodeInfo objects
        """
        if not self._initialize():
            return []
        
        try:
            nodes = self._core_api.list_node()
            result = []
            
            for node in nodes.items:
                # Determine status
                status = NodeStatus.UNKNOWN
                conditions = {}
                for condition in node.status.conditions or []:
                    conditions[condition.type] = condition.status
                    if condition.type == "Ready":
                        status = (
                            NodeStatus.READY
                            if condition.status == "True"
                            else NodeStatus.NOT_READY
                        )
                
                # Get roles from labels
                roles = []
                for label, value in (node.metadata.labels or {}).items():
                    if label.startswith("node-role.kubernetes.io/"):
                        roles.append(label.split("/")[1])
                if not roles:
                    roles = ["worker"]
                
                # Get taints
                taints = []
                for taint in node.spec.taints or []:
                    taints.append(f"{taint.key}={taint.value}:{taint.effect}")
                
                # Get IP address
                ip_address = ""
                for addr in node.status.addresses or []:
                    if addr.type == "InternalIP":
                        ip_address = addr.address
                        break
                
                # Get metrics
                capacity = node.status.capacity or {}
                allocatable = node.status.allocatable or {}
                
                # Count pods on this node
                pods = self._core_api.list_pod_for_all_namespaces(
                    field_selector=f"spec.nodeName={node.metadata.name}"
                )
                pods_running = len([p for p in pods.items if p.status.phase == "Running"])
                
                metrics = NodeMetrics(
                    cpu_capacity=capacity.get("cpu", "0"),
                    cpu_allocatable=allocatable.get("cpu", "0"),
                    memory_capacity=capacity.get("memory", "0"),
                    memory_allocatable=allocatable.get("memory", "0"),
                    pods_capacity=int(capacity.get("pods", "110")),
                    pods_running=pods_running,
                )
                
                node_info = NodeInfo(
                    name=node.metadata.name,
                    status=status,
                    roles=roles,
                    ip_address=ip_address,
                    architecture=node.status.node_info.architecture,
                    os_image=node.status.node_info.os_image,
                    kernel_version=node.status.node_info.kernel_version,
                    container_runtime=node.status.node_info.container_runtime_version,
                    kubelet_version=node.status.node_info.kubelet_version,
                    created_at=node.metadata.creation_timestamp,
                    labels=node.metadata.labels or {},
                    taints=taints,
                    conditions=conditions,
                    metrics=metrics,
                )
                result.append(node_info)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list nodes: {e}")
            return []

    async def get_node(self, name: str) -> Optional[NodeInfo]:
        """Get a specific node by name."""
        nodes = await self.list_nodes()
        for node in nodes:
            if node.name == name:
                return node
        return None

    async def list_pods(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None,
    ) -> list[PodInfo]:
        """
        List pods in the cluster.
        
        Args:
            namespace: Filter by namespace (all namespaces if None)
            label_selector: Filter by labels
            
        Returns:
            List of PodInfo objects
        """
        if not self._initialize():
            return []
        
        try:
            if namespace:
                pods = self._core_api.list_namespaced_pod(
                    namespace=namespace,
                    label_selector=label_selector,
                )
            else:
                pods = self._core_api.list_pod_for_all_namespaces(
                    label_selector=label_selector,
                )
            
            result = []
            for pod in pods.items:
                # Calculate total restarts
                restarts = 0
                containers = []
                for cs in pod.status.container_statuses or []:
                    restarts += cs.restart_count
                    containers.append(cs.name)
                
                # Map phase
                phase_map = {
                    "Pending": PodPhase.PENDING,
                    "Running": PodPhase.RUNNING,
                    "Succeeded": PodPhase.SUCCEEDED,
                    "Failed": PodPhase.FAILED,
                }
                phase = phase_map.get(pod.status.phase, PodPhase.UNKNOWN)
                
                pod_info = PodInfo(
                    name=pod.metadata.name,
                    namespace=pod.metadata.namespace,
                    phase=phase,
                    node_name=pod.spec.node_name,
                    ip_address=pod.status.pod_ip,
                    containers=containers,
                    restarts=restarts,
                    created_at=pod.metadata.creation_timestamp,
                    labels=pod.metadata.labels or {},
                )
                result.append(pod_info)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list pods: {e}")
            return []

    async def get_pod_logs(
        self,
        name: str,
        namespace: str,
        container: Optional[str] = None,
        tail_lines: int = 100,
    ) -> str:
        """Get logs from a pod."""
        if not self._initialize():
            return "Kubernetes not available"
        
        try:
            logs = self._core_api.read_namespaced_pod_log(
                name=name,
                namespace=namespace,
                container=container,
                tail_lines=tail_lines,
            )
            return logs
        except Exception as e:
            logger.error(f"Failed to get logs for pod {name}: {e}")
            return f"Error: {e}"

    async def list_services(
        self,
        namespace: Optional[str] = None,
    ) -> list[ServiceInfo]:
        """List services in the cluster."""
        if not self._initialize():
            return []
        
        try:
            if namespace:
                services = self._core_api.list_namespaced_service(namespace=namespace)
            else:
                services = self._core_api.list_service_for_all_namespaces()
            
            result = []
            for svc in services.items:
                # Get external IP if LoadBalancer
                external_ip = None
                if svc.status.load_balancer and svc.status.load_balancer.ingress:
                    ingress = svc.status.load_balancer.ingress[0]
                    external_ip = ingress.ip or ingress.hostname
                
                # Parse ports
                ports = []
                for port in svc.spec.ports or []:
                    ports.append({
                        "name": port.name,
                        "port": port.port,
                        "target_port": str(port.target_port),
                        "protocol": port.protocol,
                        "node_port": port.node_port,
                    })
                
                service_info = ServiceInfo(
                    name=svc.metadata.name,
                    namespace=svc.metadata.namespace,
                    type=svc.spec.type,
                    cluster_ip=svc.spec.cluster_ip,
                    external_ip=external_ip,
                    ports=ports,
                    selector=svc.spec.selector or {},
                    created_at=svc.metadata.creation_timestamp,
                )
                result.append(service_info)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list services: {e}")
            return []

    async def list_deployments(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None,
    ) -> list[DeploymentInfo]:
        """List deployments in the cluster."""
        if not self._initialize():
            return []
        
        try:
            if namespace:
                deployments = self._apps_api.list_namespaced_deployment(
                    namespace=namespace,
                    label_selector=label_selector,
                )
            else:
                deployments = self._apps_api.list_deployment_for_all_namespaces(
                    label_selector=label_selector,
                )
            
            result = []
            for deploy in deployments.items:
                # Determine status
                status = DeploymentStatus.PENDING
                ready = deploy.status.ready_replicas or 0
                desired = deploy.spec.replicas or 0
                
                if ready == desired and ready > 0:
                    status = DeploymentStatus.RUNNING
                elif ready < desired and ready > 0:
                    status = DeploymentStatus.SCALING
                elif deploy.status.conditions:
                    for condition in deploy.status.conditions:
                        if condition.type == "Progressing" and condition.status == "True":
                            status = DeploymentStatus.UPDATING
                        elif condition.type == "Available" and condition.status == "False":
                            status = DeploymentStatus.FAILED
                
                # Get image from first container
                image = ""
                if deploy.spec.template.spec.containers:
                    image = deploy.spec.template.spec.containers[0].image
                
                # Parse conditions
                conditions = []
                for cond in deploy.status.conditions or []:
                    conditions.append({
                        "type": cond.type,
                        "status": cond.status,
                        "reason": cond.reason,
                        "message": cond.message,
                        "last_update": cond.last_update_time.isoformat() if cond.last_update_time else None,
                    })
                
                # Get agentic-specific labels
                labels = deploy.metadata.labels or {}
                deployment_type = labels.get("agentic.io/type")
                source_id = labels.get("agentic.io/source-id")
                
                info = DeploymentInfo(
                    name=deploy.metadata.name,
                    namespace=deploy.metadata.namespace,
                    status=status,
                    replicas=desired,
                    ready_replicas=ready,
                    available_replicas=deploy.status.available_replicas or 0,
                    image=image,
                    created_at=deploy.metadata.creation_timestamp,
                    labels=labels,
                    conditions=conditions,
                    deployment_type=deployment_type,
                    source_id=source_id,
                )
                result.append(info)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list deployments: {e}")
            return []

    async def get_namespaces(self) -> list[str]:
        """Get list of namespace names."""
        if not self._initialize():
            return []
        
        try:
            namespaces = self._core_api.list_namespace()
            return [ns.metadata.name for ns in namespaces.items]
        except Exception as e:
            logger.error(f"Failed to get namespaces: {e}")
            return []

    async def create_namespace(self, name: str) -> bool:
        """Create a namespace if it doesn't exist."""
        if not self._initialize():
            return False
        
        try:
            from kubernetes import client
            
            # Check if exists
            namespaces = await self.get_namespaces()
            if name in namespaces:
                return True
            
            # Create namespace
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=name)
            )
            self._core_api.create_namespace(body=namespace)
            logger.info(f"Created namespace: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create namespace {name}: {e}")
            return False

    async def test_connection(self) -> dict:
        """
        Test the Kubernetes cluster connection.
        
        Returns:
            Dict with connection status and details
        """
        if not self._k8s_available:
            return {
                "connected": False,
                "error": "kubernetes library not installed",
            }
        
        try:
            self._initialize()
            if not self._core_api:
                return {
                    "connected": False,
                    "error": "Failed to initialize client",
                }
            
            # Try to get version
            version = self._version_api.get_code()
            
            return {
                "connected": True,
                "version": version.git_version,
                "platform": version.platform,
            }
            
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
            }
