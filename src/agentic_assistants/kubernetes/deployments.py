"""
Deployment management for Kubernetes.

Provides operations for creating, scaling, and managing deployments
of agents, flows, and other workloads.
"""

import logging
from datetime import datetime
from typing import Any, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.kubernetes.client import KubernetesClient
from agentic_assistants.kubernetes.models import (
    DeploymentConfig,
    DeploymentInfo,
    DeploymentStatus,
    AgentDeploymentConfig,
    FlowDeploymentConfig,
    ResourceRequirements,
)

logger = logging.getLogger(__name__)


class DeploymentManager:
    """
    Manager for Kubernetes deployments.
    
    Handles creation, scaling, and lifecycle management of deployments
    for agents, flows, and custom workloads.
    
    Example:
        >>> client = KubernetesClient()
        >>> manager = DeploymentManager(client)
        >>> 
        >>> config = DeploymentConfig(
        ...     name="my-agent",
        ...     image="agentic/agent:latest",
        ...     replicas=2,
        ... )
        >>> deployment = await manager.create_deployment(config)
    """

    def __init__(
        self,
        client: Optional[KubernetesClient] = None,
        config: Optional[AgenticConfig] = None,
    ):
        """
        Initialize the deployment manager.
        
        Args:
            client: Kubernetes client instance
            config: Agentic configuration
        """
        self.config = config or AgenticConfig()
        self.client = client or KubernetesClient(config=self.config)

    async def create_deployment(self, deploy_config: DeploymentConfig) -> Optional[DeploymentInfo]:
        """
        Create a new Kubernetes deployment.
        
        Args:
            deploy_config: Deployment configuration
            
        Returns:
            DeploymentInfo if successful, None otherwise
        """
        if not self.client.is_available:
            logger.error("Kubernetes client not available")
            return None
        
        try:
            from kubernetes import client
            
            # Ensure namespace exists
            await self.client.create_namespace(deploy_config.namespace)
            
            # Build resource requirements
            resources = None
            if deploy_config.resources:
                resources = client.V1ResourceRequirements(
                    requests={
                        "cpu": deploy_config.resources.cpu_request,
                        "memory": deploy_config.resources.memory_request,
                    },
                    limits={
                        "cpu": deploy_config.resources.cpu_limit,
                        "memory": deploy_config.resources.memory_limit,
                    },
                )
                if deploy_config.resources.gpu_request:
                    resources.limits["nvidia.com/gpu"] = str(deploy_config.resources.gpu_request)
            else:
                # Use defaults from config
                k8s_config = self.config.kubernetes
                resources = client.V1ResourceRequirements(
                    requests={
                        "cpu": k8s_config.default_cpu_request,
                        "memory": k8s_config.default_memory_request,
                    },
                    limits={
                        "cpu": k8s_config.default_cpu_limit,
                        "memory": k8s_config.default_memory_limit,
                    },
                )
            
            # Build container spec
            container = client.V1Container(
                name=deploy_config.name,
                image=deploy_config.image,
                ports=[client.V1ContainerPort(container_port=deploy_config.port)]
                if deploy_config.port
                else None,
                env=[
                    client.V1EnvVar(name=k, value=v)
                    for k, v in deploy_config.env.items()
                ],
                resources=resources,
            )
            
            # Build labels
            labels = {
                "app": deploy_config.name,
                "agentic.io/managed": "true",
                "agentic.io/type": deploy_config.deployment_type,
            }
            if deploy_config.source_id:
                labels["agentic.io/source-id"] = deploy_config.source_id
            labels.update(deploy_config.labels)
            
            # Build pod template
            template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels),
                spec=client.V1PodSpec(
                    containers=[container],
                    node_selector=deploy_config.node_selector,
                ),
            )
            
            # Build deployment spec
            spec = client.V1DeploymentSpec(
                replicas=deploy_config.replicas,
                selector=client.V1LabelSelector(
                    match_labels={"app": deploy_config.name},
                ),
                template=template,
            )
            
            # Build deployment
            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(
                    name=deploy_config.name,
                    namespace=deploy_config.namespace,
                    labels=labels,
                ),
                spec=spec,
            )
            
            # Create deployment
            self.client.apps_api.create_namespaced_deployment(
                namespace=deploy_config.namespace,
                body=deployment,
            )
            logger.info(f"Created deployment {deploy_config.name} in {deploy_config.namespace}")
            
            # Create service if requested
            if deploy_config.create_service and deploy_config.port:
                await self._create_service(deploy_config)
            
            # Create ConfigMap if data provided
            if deploy_config.config_map_data:
                await self._create_configmap(deploy_config)
            
            # Return deployment info
            return await self.get_deployment(deploy_config.name, deploy_config.namespace)
            
        except Exception as e:
            logger.error(f"Failed to create deployment: {e}")
            return None

    async def _create_service(self, deploy_config: DeploymentConfig) -> bool:
        """Create a service for a deployment."""
        try:
            from kubernetes import client
            
            service = client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(
                    name=deploy_config.name,
                    namespace=deploy_config.namespace,
                    labels={
                        "agentic.io/managed": "true",
                    },
                ),
                spec=client.V1ServiceSpec(
                    type=deploy_config.service_type,
                    selector={"app": deploy_config.name},
                    ports=[
                        client.V1ServicePort(
                            port=deploy_config.port,
                            target_port=deploy_config.port,
                        )
                    ],
                ),
            )
            
            self.client.core_api.create_namespaced_service(
                namespace=deploy_config.namespace,
                body=service,
            )
            logger.info(f"Created service {deploy_config.name} in {deploy_config.namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create service: {e}")
            return False

    async def _create_configmap(self, deploy_config: DeploymentConfig) -> bool:
        """Create a ConfigMap for a deployment."""
        try:
            from kubernetes import client
            
            configmap = client.V1ConfigMap(
                api_version="v1",
                kind="ConfigMap",
                metadata=client.V1ObjectMeta(
                    name=f"{deploy_config.name}-config",
                    namespace=deploy_config.namespace,
                ),
                data=deploy_config.config_map_data,
            )
            
            self.client.core_api.create_namespaced_config_map(
                namespace=deploy_config.namespace,
                body=configmap,
            )
            logger.info(f"Created ConfigMap {deploy_config.name}-config")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create ConfigMap: {e}")
            return False

    async def get_deployment(
        self,
        name: str,
        namespace: str,
    ) -> Optional[DeploymentInfo]:
        """Get a specific deployment."""
        deployments = await self.client.list_deployments(namespace=namespace)
        for deploy in deployments:
            if deploy.name == name:
                return deploy
        return None

    async def list_deployments(
        self,
        namespace: Optional[str] = None,
        deployment_type: Optional[str] = None,
    ) -> list[DeploymentInfo]:
        """
        List deployments, optionally filtered.
        
        Args:
            namespace: Filter by namespace
            deployment_type: Filter by agentic deployment type
            
        Returns:
            List of DeploymentInfo objects
        """
        label_selector = "agentic.io/managed=true"
        if deployment_type:
            label_selector += f",agentic.io/type={deployment_type}"
        
        return await self.client.list_deployments(
            namespace=namespace,
            label_selector=label_selector,
        )

    async def scale_deployment(
        self,
        name: str,
        namespace: str,
        replicas: int,
    ) -> Optional[DeploymentInfo]:
        """Scale a deployment to the specified number of replicas."""
        if not self.client.is_available:
            return None
        
        try:
            body = {"spec": {"replicas": replicas}}
            self.client.apps_api.patch_namespaced_deployment_scale(
                name=name,
                namespace=namespace,
                body=body,
            )
            logger.info(f"Scaled deployment {name} to {replicas} replicas")
            return await self.get_deployment(name, namespace)
            
        except Exception as e:
            logger.error(f"Failed to scale deployment: {e}")
            return None

    async def delete_deployment(
        self,
        name: str,
        namespace: str,
        delete_service: bool = True,
    ) -> bool:
        """Delete a deployment and optionally its service."""
        if not self.client.is_available:
            return False
        
        try:
            self.client.apps_api.delete_namespaced_deployment(
                name=name,
                namespace=namespace,
            )
            logger.info(f"Deleted deployment {name}")
            
            if delete_service:
                try:
                    self.client.core_api.delete_namespaced_service(
                        name=name,
                        namespace=namespace,
                    )
                    logger.info(f"Deleted service {name}")
                except Exception as e:
                    # Service might not exist
                    logger.debug(f"Service {name} not found or already deleted: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete deployment: {e}")
            return False

    async def restart_deployment(
        self,
        name: str,
        namespace: str,
    ) -> Optional[DeploymentInfo]:
        """Restart a deployment by triggering a rolling restart."""
        if not self.client.is_available:
            return None
        
        try:
            now = datetime.utcnow().isoformat()
            body = {
                "spec": {
                    "template": {
                        "metadata": {
                            "annotations": {
                                "kubectl.kubernetes.io/restartedAt": now,
                            }
                        }
                    }
                }
            }
            self.client.apps_api.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=body,
            )
            logger.info(f"Restarted deployment {name}")
            return await self.get_deployment(name, namespace)
            
        except Exception as e:
            logger.error(f"Failed to restart deployment: {e}")
            return None

    async def deploy_agent(
        self,
        agent_config: AgentDeploymentConfig,
        base_image: str = "agentic/agent-runner:latest",
    ) -> Optional[DeploymentInfo]:
        """
        Deploy an agent to Kubernetes.
        
        Args:
            agent_config: Agent deployment configuration
            base_image: Base container image for the agent
            
        Returns:
            DeploymentInfo if successful
        """
        # Build environment variables
        env = {
            "AGENT_ID": agent_config.agent_id,
            "AGENT_FRAMEWORK": agent_config.framework,
            "AGENTIC_LOG_LEVEL": "INFO",
        }
        if agent_config.model_endpoint:
            env["OLLAMA_HOST"] = agent_config.model_endpoint
        env.update(agent_config.env_vars)
        
        # Create deployment config
        deploy_config = DeploymentConfig(
            name=agent_config.name,
            namespace=agent_config.namespace,
            image=base_image,
            replicas=agent_config.replicas,
            port=8080,
            env=env,
            resources=agent_config.resources,
            deployment_type="agent",
            source_id=agent_config.agent_id,
            create_service=True,
            service_type="ClusterIP",
        )
        
        return await self.create_deployment(deploy_config)

    async def deploy_flow(
        self,
        flow_config: FlowDeploymentConfig,
        base_image: str = "agentic/flow-runner:latest",
    ) -> Optional[DeploymentInfo]:
        """
        Deploy a flow to Kubernetes.
        
        Args:
            flow_config: Flow deployment configuration
            base_image: Base container image for the flow
            
        Returns:
            DeploymentInfo if successful
        """
        # Build environment variables
        env = {
            "FLOW_ID": flow_config.flow_id,
            "FLOW_FRAMEWORK": flow_config.framework,
            "STATE_BACKEND": flow_config.state_backend,
            "AGENTIC_LOG_LEVEL": "INFO",
        }
        if flow_config.model_endpoint:
            env["OLLAMA_HOST"] = flow_config.model_endpoint
        
        # Add MinIO config if using minio state backend
        if flow_config.state_backend == "minio":
            minio_config = self.config.minio
            env["MINIO_ENDPOINT"] = minio_config.endpoint
            env["MINIO_BUCKET"] = minio_config.default_bucket
        
        env.update(flow_config.env_vars)
        
        # Create deployment config
        deploy_config = DeploymentConfig(
            name=flow_config.name,
            namespace=flow_config.namespace,
            image=base_image,
            replicas=flow_config.replicas,
            port=8080,
            env=env,
            resources=flow_config.resources,
            deployment_type="flow",
            source_id=flow_config.flow_id,
            create_service=True,
            service_type="ClusterIP",
        )
        
        return await self.create_deployment(deploy_config)

    async def get_deployment_logs(
        self,
        name: str,
        namespace: str,
        tail_lines: int = 100,
    ) -> str:
        """Get logs from a deployment's pods."""
        pods = await self.client.list_pods(
            namespace=namespace,
            label_selector=f"app={name}",
        )
        
        if not pods:
            return "No pods found for deployment"
        
        # Get logs from first pod
        pod = pods[0]
        return await self.client.get_pod_logs(
            name=pod.name,
            namespace=namespace,
            tail_lines=tail_lines,
        )

    async def get_deployment_status(
        self,
        name: str,
        namespace: str,
    ) -> dict:
        """Get detailed status of a deployment."""
        deployment = await self.get_deployment(name, namespace)
        if not deployment:
            return {"status": "not_found"}
        
        pods = await self.client.list_pods(
            namespace=namespace,
            label_selector=f"app={name}",
        )
        
        return {
            "status": deployment.status.value,
            "replicas": deployment.replicas,
            "ready_replicas": deployment.ready_replicas,
            "available_replicas": deployment.available_replicas,
            "pods": [
                {
                    "name": p.name,
                    "phase": p.phase.value,
                    "restarts": p.restarts,
                    "node": p.node_name,
                }
                for p in pods
            ],
            "conditions": deployment.conditions,
        }
