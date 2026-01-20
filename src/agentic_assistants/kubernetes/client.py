"""
Kubernetes client wrapper for Agentic Assistants.

Provides a high-level interface for Kubernetes cluster operations,
wrapping the kubernetes-python library with async support.
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any

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


def discover_rpi_kubeconfig() -> Optional[str]:
    """
    Discover the rpi_kubernetes kubeconfig file.
    
    Searches for kubeconfig.yaml in the rpi_kubernetes repository directory.
    Falls back to standard locations if not found.
    
    Returns:
        Path to kubeconfig file if found, None otherwise
    """
    # Get username with fallback
    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    
    # Build search paths
    search_paths = []
    
    # Path.home() based paths (most reliable cross-platform)
    search_paths.append(Path.home() / "Documents" / "GitHub" / "rpi_kubernetes" / "kubeconfig.yaml")
    search_paths.append(Path.home() / "rpi_kubernetes" / "kubeconfig.yaml")
    
    # Windows-specific paths with username
    if username:
        search_paths.append(Path(f"C:/Users/{username}/Documents/GitHub/rpi_kubernetes/kubeconfig.yaml"))
        # WSL path
        search_paths.append(Path(f"/mnt/c/Users/{username}/Documents/GitHub/rpi_kubernetes/kubeconfig.yaml"))
    
    # Try USERPROFILE environment variable (Windows)
    userprofile = os.getenv("USERPROFILE")
    if userprofile:
        search_paths.append(Path(userprofile) / "Documents" / "GitHub" / "rpi_kubernetes" / "kubeconfig.yaml")
    
    # Relative to current working directory (for running from repo)
    search_paths.append(Path.cwd().parent / "rpi_kubernetes" / "kubeconfig.yaml")
    
    logger.debug(f"Searching for rpi_kubernetes kubeconfig in: {[str(p) for p in search_paths]}")
    
    for path in search_paths:
        try:
            if path.exists() and path.is_file():
                logger.info(f"Discovered rpi_kubernetes kubeconfig at: {path}")
                return str(path)
        except Exception as e:
            logger.debug(f"Error checking path {path}: {e}")
    
    logger.debug("rpi_kubernetes kubeconfig not found in standard locations")
    return None


def _is_running_in_cluster() -> bool:
    """Check if we're running inside a Kubernetes cluster."""
    return os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token")


def _candidate_kubeconfigs(config: AgenticConfig) -> List[Dict[str, Any]]:
    """
    Collect candidate kubeconfig files in priority order.
    
    Returns:
        List of dicts with 'path' and 'source' keys, ordered by priority
    """
    candidates = []
    k8s_settings = config.kubernetes
    
    # 1. Explicit K8S_KUBECONFIG_PATH if set
    if k8s_settings.kubeconfig_path:
        candidates.append({
            "path": k8s_settings.kubeconfig_path,
            "source": "K8S_KUBECONFIG_PATH"
        })
    
    # 2. KUBECONFIG environment variable (can be multiple paths separated by os.pathsep)
    kubeconfig_env = os.getenv("KUBECONFIG")
    if kubeconfig_env:
        for path_str in kubeconfig_env.split(os.pathsep):
            path = Path(path_str).expanduser().resolve()
            if path.exists():
                candidates.append({
                    "path": str(path),
                    "source": "KUBECONFIG"
                })
    
    # 3. rpi_kubernetes discovery (if autodetect enabled)
    if k8s_settings.autodetect_enabled:
        rpi_path = discover_rpi_kubeconfig()
        if rpi_path:
            candidates.append({
                "path": rpi_path,
                "source": "rpi_kubernetes_discovery"
            })
    
    # 4. Standard kubeconfig locations
    standard_paths = [
        (Path.home() / ".kube" / "config", "standard_home"),
    ]
    
    # Windows-specific standard path
    if os.name == "nt":
        userprofile = os.getenv("USERPROFILE")
        if userprofile:
            standard_paths.append((Path(userprofile) / ".kube" / "config", "standard_userprofile"))
    
    for path, source in standard_paths:
        path_expanded = path.expanduser().resolve()
        if path_expanded.exists():
            candidates.append({
                "path": str(path_expanded),
                "source": source
            })
    
    # 5. Extra paths from config
    if k8s_settings.autodetect_enabled and k8s_settings.autodetect_extra_paths:
        for path_str in k8s_settings.autodetect_extra_paths.split(","):
            path_str = path_str.strip()
            if path_str:
                path = Path(path_str).expanduser().resolve()
                if path.exists():
                    candidates.append({
                        "path": str(path),
                        "source": "autodetect_extra_paths"
                    })
    
    return candidates


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
        
        # Diagnostics tracking
        self._last_init: Dict[str, Any] = {}
        self._last_init_error: Optional[str] = None
        self._candidates_tried: List[Dict[str, Any]] = []
        self._connection_method: Optional[str] = None
        self._selected_kubeconfig: Optional[str] = None
        self._selected_context: Optional[str] = None
        self._capabilities: Dict[str, bool] = {}
        self._warnings: List[str] = []
        
        # Check if kubernetes library is available
        try:
            from kubernetes import client, config as k8s_config
            self._k8s_available = True
        except ImportError:
            logger.warning("kubernetes library not installed. K8s features disabled.")
            self._last_init_error = "kubernetes library not installed"
            self._initialized = True

    def _initialize(self) -> bool:
        """Initialize Kubernetes client connection with enhanced diagnostics."""
        if self._initialized:
            return self._k8s_available
        
        if not self._k8s_available:
            self._initialized = True
            return False
        
        # Reset diagnostics
        self._last_init = {}
        self._last_init_error = None
        self._candidates_tried = []
        self._connection_method = None
        self._selected_kubeconfig = None
        self._selected_context = None
        self._capabilities = {}
        self._warnings = []
        
        try:
            from kubernetes import client, config as k8s_config
            
            conn = self.connection_config
            k8s_settings = self.config.kubernetes
            timeout = k8s_settings.request_timeout_seconds
            
            # Determine preferred incluster setting
            prefer_incluster = k8s_settings.prefer_incluster
            if prefer_incluster is None:
                prefer_incluster = _is_running_in_cluster()
            
            # Try direct connection first if configured
            cluster_endpoint = conn.cluster_endpoint if conn else k8s_settings.cluster_endpoint
            token = conn.token if conn else k8s_settings.cluster_token
            
            if cluster_endpoint and token:
                try:
                    self._connection_method = "direct_endpoint"
                    configuration = client.Configuration()
                    configuration.host = cluster_endpoint
                    configuration.api_key = {"authorization": f"Bearer {token}"}
                    verify_ssl = not (k8s_settings.insecure_skip_tls_verify or 
                                    (conn and not conn.verify_ssl) or 
                                    not k8s_settings.verify_ssl)
                    configuration.verify_ssl = verify_ssl
                    configuration.ssl_ca_cert = None if not verify_ssl else None
                    client.Configuration.set_default(configuration)
                    
                    # Test connectivity
                    test_api = client.VersionApi()
                    version_info = test_api.get_code(_request_timeout=timeout)
                    self._last_init = {
                        "method": "direct_endpoint",
                        "endpoint": cluster_endpoint,
                        "verify_ssl": verify_ssl,
                        "version": version_info.git_version,
                    }
                    logger.info(f"Connected via direct endpoint: {cluster_endpoint}")
                except Exception as e:
                    self._last_init_error = f"Direct endpoint connection failed: {str(e)}"
                    logger.error(f"{self._last_init_error}")
                    raise
            
            # Try in-cluster config if preferred and available
            elif prefer_incluster:
                try:
                    self._connection_method = "incluster"
                    k8s_config.load_incluster_config()
                    
                    # Test connectivity
                    test_api = client.VersionApi()
                    version_info = test_api.get_code(_request_timeout=timeout)
                    self._last_init = {
                        "method": "incluster",
                        "version": version_info.git_version,
                    }
                    logger.info("Connected via in-cluster config")
                except Exception as e:
                    self._connection_method = None
                    self._last_init_error = f"In-cluster config failed: {str(e)}"
                    logger.debug(f"{self._last_init_error}")
                    # Continue to try kubeconfig
            
            # Try kubeconfig-based connection
            if not self._connection_method:
                context = conn.context if conn else k8s_settings.context
                explicit_path = conn.kubeconfig_path if conn else k8s_settings.kubeconfig_path
                
                candidates = []
                if explicit_path:
                    # Explicit path gets highest priority
                    candidates.insert(0, {
                        "path": explicit_path,
                        "source": "explicit_config"
                    })
                elif k8s_settings.autodetect_enabled:
                    # Get auto-discovered candidates
                    candidates = _candidate_kubeconfigs(self.config)
                
                # If no candidates and we haven't tried incluster, try standard load
                if not candidates and not prefer_incluster:
                    candidates.append({
                        "path": None,  # Will use default kubeconfig
                        "source": "default_kubeconfig"
                    })
                
                # Try each candidate
                for candidate in candidates:
                    kubeconfig_path = candidate.get("path")
                    source = candidate.get("source", "unknown")
                    
                    try:
                        if kubeconfig_path:
                            # Verify file exists
                            if not Path(kubeconfig_path).exists():
                                self._candidates_tried.append({
                                    "path": kubeconfig_path,
                                    "source": source,
                                    "error": "File does not exist"
                                })
                                continue
                            
                            k8s_config.load_kube_config(
                                config_file=kubeconfig_path,
                                context=context,
                            )
                            self._selected_kubeconfig = kubeconfig_path
                        else:
                            # Use default kubeconfig location
                            k8s_config.load_kube_config(context=context)
                            default_path = str(Path.home() / ".kube" / "config")
                            self._selected_kubeconfig = default_path if Path(default_path).exists() else None
                        
                        # Override SSL verification if requested
                        if k8s_settings.insecure_skip_tls_verify:
                            current_config = client.Configuration()
                            current_config.verify_ssl = False
                            client.Configuration.set_default(current_config)
                        
                        # Test connectivity
                        test_api = client.VersionApi()
                        version_info = test_api.get_code(_request_timeout=timeout)
                        
                        # Success!
                        self._connection_method = "kubeconfig"
                        self._selected_context = context
                        self._last_init = {
                            "method": "kubeconfig",
                            "kubeconfig": self._selected_kubeconfig,
                            "context": context,
                            "source": source,
                            "verify_ssl": not k8s_settings.insecure_skip_tls_verify,
                            "version": version_info.git_version,
                        }
                        
                        logger.info(
                            f"Connected via kubeconfig: {self._selected_kubeconfig} "
                            f"(context: {context or 'current'}, source: {source})"
                        )
                        break
                        
                    except Exception as e:
                        error_msg = str(e)
                        self._candidates_tried.append({
                            "path": kubeconfig_path or "default",
                            "source": source,
                            "error": error_msg
                        })
                        logger.debug(f"Failed to load kubeconfig from {kubeconfig_path or 'default'}: {error_msg}")
                        continue
                
                if not self._connection_method:
                    # All candidates failed
                    all_errors = [f"{c['source']}: {c.get('error', 'unknown')}" for c in self._candidates_tried]
                    self._last_init_error = f"All kubeconfig candidates failed. Tried: {', '.join(all_errors)}"
                    raise Exception(self._last_init_error)
            
            # Initialize API clients
            self._core_api = client.CoreV1Api()
            self._apps_api = client.AppsV1Api()
            self._version_api = client.VersionApi()
            self._custom_api = client.CustomObjectsApi()
            
            # Probe capabilities (best-effort, don't fail on errors)
            self._probe_capabilities(timeout)
            
            self._initialized = True
            logger.info("Kubernetes client initialized successfully")
            return True
            
        except Exception as e:
            error_str = str(e)
            if not self._last_init_error:
                self._last_init_error = error_str
            logger.error(f"Failed to initialize Kubernetes client: {error_str}")
            self._initialized = True
            return False
    
    def _probe_capabilities(self, timeout: int) -> None:
        """Probe cluster capabilities (best-effort, doesn't fail on errors)."""
        if not self._core_api or not self._apps_api:
            return
        
        try:
            # Test: can list namespaces
            try:
                self._core_api.list_namespace(_request_timeout=timeout)
                self._capabilities["list_namespaces"] = True
            except Exception as e:
                self._capabilities["list_namespaces"] = False
                self._warnings.append(f"Cannot list namespaces: {str(e)}")
            
            # Test: can list deployments in default namespace
            try:
                self._apps_api.list_namespaced_deployment(
                    namespace="default",
                    _request_timeout=timeout
                )
                self._capabilities["list_deployments"] = True
            except Exception as e:
                self._capabilities["list_deployments"] = False
                self._warnings.append(f"Cannot list deployments: {str(e)}")
            
            # Test: can list pods
            try:
                self._core_api.list_pod_for_all_namespaces(_request_timeout=timeout)
                self._capabilities["list_pods"] = True
            except Exception as e:
                self._capabilities["list_pods"] = False
                self._warnings.append(f"Cannot list pods: {str(e)}")
                
        except Exception as e:
            logger.debug(f"Capability probe encountered error: {e}")

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
            
            cluster_info = ClusterInfo(
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
                context=self.config.kubernetes.context or self._selected_context,
            )
            
            # Add capabilities and warnings if available (for partial connections)
            if self._warnings:
                # Store warnings in a way that can be accessed if needed
                # Note: ClusterInfo model may not have warnings field, but we can log them
                for warning in self._warnings:
                    logger.warning(f"Cluster connection warning: {warning}")
            
            return cluster_info
            
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

    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Get detailed diagnostics about connection attempts and current status.
        
        Returns:
            Dict with comprehensive diagnostics information
        """
        diagnostics = {
            "kubernetes_library_available": self._k8s_available,
            "initialized": self._initialized,
            "connected": self._initialized and self._core_api is not None,
            "connection_method": self._connection_method,
            "last_init": self._last_init.copy() if self._last_init else {},
            "error": self._last_init_error,
            "candidates_tried": self._candidates_tried.copy(),
            "selected_kubeconfig": self._selected_kubeconfig,
            "selected_context": self._selected_context,
            "capabilities": self._capabilities.copy(),
            "warnings": self._warnings.copy(),
        }
        
        # Add actionable suggestions
        suggestions = []
        if not self._k8s_available:
            suggestions.append("Install the kubernetes library: pip install kubernetes")
        elif not diagnostics["connected"]:
            if self._last_init_error:
                error_lower = self._last_init_error.lower()
                if "ssl" in error_lower or "certificate" in error_lower:
                    suggestions.append("Try setting K8S_INSECURE_SKIP_TLS_VERIFY=true (insecure, for testing only)")
                if "connection" in error_lower or "timeout" in error_lower:
                    suggestions.append("Verify the cluster API server is reachable from this machine")
                    suggestions.append("Check network connectivity and firewall rules")
                if "kubeconfig" in error_lower or "config" in error_lower:
                    suggestions.append("Set K8S_KUBECONFIG_PATH to the correct kubeconfig file path")
                    suggestions.append("Verify the kubeconfig file is valid: kubectl --kubeconfig=<path> get nodes")
                if not self._candidates_tried:
                    suggestions.append("Set K8S_AUTODETECT_ENABLED=true to enable auto-discovery")
                    suggestions.append("Set K8S_KUBECONFIG_PATH explicitly if auto-discovery doesn't work")
        
        diagnostics["suggestions"] = suggestions
        
        # If connected, try to get version info
        if diagnostics["connected"] and self._version_api:
            try:
                version_info = self._version_api.get_code(_request_timeout=5)
                diagnostics["version"] = version_info.git_version
                diagnostics["platform"] = version_info.platform
            except Exception as e:
                diagnostics["warnings"].append(f"Could not retrieve version info: {str(e)}")
        
        return diagnostics
    
    async def test_connection(self) -> dict:
        """
        Test the Kubernetes cluster connection with diagnostics.
        
        Returns:
            Dict with connection status, diagnostics, and suggestions
        """
        if not self._k8s_available:
            return {
                "connected": False,
                "error": "kubernetes library not installed",
                "suggestions": ["Install the kubernetes library: pip install kubernetes"],
            }
        
        try:
            self._initialize()
            diagnostics = self.get_diagnostics()
            
            if diagnostics["connected"]:
                return {
                    "connected": True,
                    "version": diagnostics.get("version"),
                    "platform": diagnostics.get("platform"),
                    "connection_method": diagnostics["connection_method"],
                    "capabilities": diagnostics["capabilities"],
                    "warnings": diagnostics["warnings"] if diagnostics["warnings"] else None,
                }
            else:
                return {
                    "connected": False,
                    "error": diagnostics["error"] or "Failed to initialize client",
                    "connection_method": diagnostics["connection_method"],
                    "candidates_tried": diagnostics["candidates_tried"],
                    "suggestions": diagnostics["suggestions"],
                }
            
        except Exception as e:
            diagnostics = self.get_diagnostics()
            return {
                "connected": False,
                "error": str(e),
                "connection_method": diagnostics.get("connection_method"),
                "candidates_tried": diagnostics.get("candidates_tried", []),
                "suggestions": diagnostics.get("suggestions", []),
            }
