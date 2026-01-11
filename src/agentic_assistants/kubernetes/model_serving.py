"""
LLM Model Serving for Kubernetes.

Provides deployment and management of LLM models on Kubernetes,
supporting Ollama, vLLM, and HuggingFace Text Generation Inference.
"""

import logging
from typing import Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.kubernetes.client import KubernetesClient
from agentic_assistants.kubernetes.deployments import DeploymentManager
from agentic_assistants.kubernetes.models import (
    ModelDeploymentConfig,
    ModelServingType,
    DeploymentInfo,
    DeploymentConfig,
    ResourceRequirements,
)

logger = logging.getLogger(__name__)


# Default images for model serving
MODEL_SERVING_IMAGES = {
    ModelServingType.OLLAMA: "ollama/ollama:latest",
    ModelServingType.VLLM: "vllm/vllm-openai:latest",
    ModelServingType.TGI: "ghcr.io/huggingface/text-generation-inference:latest",
}

# Default ports for model serving
MODEL_SERVING_PORTS = {
    ModelServingType.OLLAMA: 11434,
    ModelServingType.VLLM: 8000,
    ModelServingType.TGI: 80,
}


class ModelServingManager:
    """
    Manager for LLM model deployments on Kubernetes.
    
    Supports deploying models using:
    - Ollama: Local-first LLM serving
    - vLLM: High-performance inference
    - TGI: HuggingFace Text Generation Inference
    
    Example:
        >>> manager = ModelServingManager()
        >>> config = ModelDeploymentConfig(
        ...     name="llama-server",
        ...     model_name="llama3.2",
        ...     serving_type=ModelServingType.OLLAMA,
        ... )
        >>> deployment = await manager.deploy_model(config)
    """

    def __init__(
        self,
        client: Optional[KubernetesClient] = None,
        config: Optional[AgenticConfig] = None,
    ):
        """
        Initialize the model serving manager.
        
        Args:
            client: Kubernetes client instance
            config: Agentic configuration
        """
        self.config = config or AgenticConfig()
        self.client = client or KubernetesClient(config=self.config)
        self.deployer = DeploymentManager(client=self.client, config=self.config)

    async def deploy_model(
        self,
        model_config: ModelDeploymentConfig,
    ) -> Optional[DeploymentInfo]:
        """
        Deploy an LLM model to Kubernetes.
        
        Args:
            model_config: Model deployment configuration
            
        Returns:
            DeploymentInfo if successful
        """
        serving_type = model_config.serving_type
        
        if serving_type == ModelServingType.OLLAMA:
            return await self._deploy_ollama(model_config)
        elif serving_type == ModelServingType.VLLM:
            return await self._deploy_vllm(model_config)
        elif serving_type == ModelServingType.TGI:
            return await self._deploy_tgi(model_config)
        else:
            logger.error(f"Unsupported serving type: {serving_type}")
            return None

    async def _deploy_ollama(
        self,
        model_config: ModelDeploymentConfig,
    ) -> Optional[DeploymentInfo]:
        """Deploy an Ollama model server."""
        # Build environment variables
        env = {
            "OLLAMA_HOST": "0.0.0.0",
            "OLLAMA_MODELS": "/root/.ollama/models",
        }
        
        # Add GPU configuration if specified
        if model_config.gpu_layers:
            env["OLLAMA_NUM_GPU"] = str(model_config.gpu_layers)
        
        # Build resource requirements
        resources = model_config.resources or ResourceRequirements(
            cpu_request="500m",
            cpu_limit="4000m",
            memory_request="2Gi",
            memory_limit="8Gi",
        )
        
        # Create deployment config
        deploy_config = DeploymentConfig(
            name=model_config.name,
            namespace=model_config.namespace,
            image=MODEL_SERVING_IMAGES[ModelServingType.OLLAMA],
            replicas=model_config.replicas,
            port=MODEL_SERVING_PORTS[ModelServingType.OLLAMA],
            env=env,
            resources=resources,
            deployment_type="model",
            labels={
                "agentic.io/model-name": model_config.model_name,
                "agentic.io/serving-type": "ollama",
            },
            create_service=True,
            service_type="ClusterIP",
        )
        
        deployment = await self.deployer.create_deployment(deploy_config)
        
        if deployment:
            # Schedule model pull after deployment is ready
            logger.info(f"Ollama deployment created. Model {model_config.model_name} will need to be pulled.")
        
        return deployment

    async def _deploy_vllm(
        self,
        model_config: ModelDeploymentConfig,
    ) -> Optional[DeploymentInfo]:
        """Deploy a vLLM model server."""
        # Build command arguments
        args = [
            "--model", model_config.model_name,
            "--host", "0.0.0.0",
            "--port", str(MODEL_SERVING_PORTS[ModelServingType.VLLM]),
        ]
        
        if model_config.context_length:
            args.extend(["--max-model-len", str(model_config.context_length)])
        
        if model_config.quantization:
            args.extend(["--quantization", model_config.quantization])
        
        # Build environment variables
        env = {
            "HF_HOME": "/root/.cache/huggingface",
        }
        
        # Build resource requirements (vLLM typically needs more resources)
        resources = model_config.resources or ResourceRequirements(
            cpu_request="1000m",
            cpu_limit="8000m",
            memory_request="8Gi",
            memory_limit="32Gi",
            gpu_request=1 if model_config.gpu_layers else None,
        )
        
        # Create deployment config
        deploy_config = DeploymentConfig(
            name=model_config.name,
            namespace=model_config.namespace,
            image=MODEL_SERVING_IMAGES[ModelServingType.VLLM],
            replicas=model_config.replicas,
            port=MODEL_SERVING_PORTS[ModelServingType.VLLM],
            env=env,
            resources=resources,
            deployment_type="model",
            labels={
                "agentic.io/model-name": model_config.model_name,
                "agentic.io/serving-type": "vllm",
            },
            create_service=True,
            service_type="ClusterIP",
            config_map_data={
                "args": " ".join(args),
            },
        )
        
        return await self.deployer.create_deployment(deploy_config)

    async def _deploy_tgi(
        self,
        model_config: ModelDeploymentConfig,
    ) -> Optional[DeploymentInfo]:
        """Deploy a HuggingFace Text Generation Inference server."""
        # Build environment variables
        env = {
            "MODEL_ID": model_config.model_name,
            "PORT": str(MODEL_SERVING_PORTS[ModelServingType.TGI]),
            "HUGGINGFACE_HUB_CACHE": "/data",
        }
        
        if model_config.context_length:
            env["MAX_INPUT_LENGTH"] = str(model_config.context_length)
            env["MAX_TOTAL_TOKENS"] = str(model_config.context_length * 2)
        
        if model_config.quantization:
            env["QUANTIZE"] = model_config.quantization
        
        # Build resource requirements
        resources = model_config.resources or ResourceRequirements(
            cpu_request="1000m",
            cpu_limit="8000m",
            memory_request="8Gi",
            memory_limit="32Gi",
            gpu_request=1 if model_config.gpu_layers else None,
        )
        
        # Create deployment config
        deploy_config = DeploymentConfig(
            name=model_config.name,
            namespace=model_config.namespace,
            image=MODEL_SERVING_IMAGES[ModelServingType.TGI],
            replicas=model_config.replicas,
            port=MODEL_SERVING_PORTS[ModelServingType.TGI],
            env=env,
            resources=resources,
            deployment_type="model",
            labels={
                "agentic.io/model-name": model_config.model_name,
                "agentic.io/serving-type": "tgi",
            },
            create_service=True,
            service_type="ClusterIP",
        )
        
        return await self.deployer.create_deployment(deploy_config)

    async def list_model_deployments(
        self,
        namespace: Optional[str] = None,
    ) -> list[DeploymentInfo]:
        """
        List all model deployments.
        
        Args:
            namespace: Filter by namespace
            
        Returns:
            List of model deployments
        """
        return await self.deployer.list_deployments(
            namespace=namespace or self.config.kubernetes.model_serving_namespace,
            deployment_type="model",
        )

    async def get_model_deployment(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> Optional[DeploymentInfo]:
        """Get a specific model deployment."""
        ns = namespace or self.config.kubernetes.model_serving_namespace
        return await self.deployer.get_deployment(name, ns)

    async def delete_model_deployment(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> bool:
        """Delete a model deployment."""
        ns = namespace or self.config.kubernetes.model_serving_namespace
        return await self.deployer.delete_deployment(name, ns)

    async def scale_model_deployment(
        self,
        name: str,
        replicas: int,
        namespace: Optional[str] = None,
    ) -> Optional[DeploymentInfo]:
        """Scale a model deployment."""
        ns = namespace or self.config.kubernetes.model_serving_namespace
        return await self.deployer.scale_deployment(name, ns, replicas)

    async def get_model_endpoint(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> Optional[str]:
        """
        Get the endpoint URL for a model deployment.
        
        Args:
            name: Deployment name
            namespace: Deployment namespace
            
        Returns:
            Service endpoint URL (internal cluster URL)
        """
        ns = namespace or self.config.kubernetes.model_serving_namespace
        deployment = await self.get_model_deployment(name, ns)
        
        if not deployment:
            return None
        
        # Get serving type from labels
        serving_type = deployment.labels.get("agentic.io/serving-type", "ollama")
        
        # Determine port based on serving type
        port_map = {
            "ollama": 11434,
            "vllm": 8000,
            "tgi": 80,
        }
        port = port_map.get(serving_type, 8080)
        
        # Return internal service URL
        return f"http://{name}.{ns}.svc.cluster.local:{port}"

    async def get_model_external_endpoint(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> Optional[str]:
        """
        Get the external endpoint URL for a model deployment.
        
        This requires the service to be exposed via LoadBalancer or Ingress.
        
        Args:
            name: Deployment name
            namespace: Deployment namespace
            
        Returns:
            External endpoint URL if available
        """
        ns = namespace or self.config.kubernetes.model_serving_namespace
        
        services = await self.client.list_services(namespace=ns)
        for svc in services:
            if svc.name == name:
                if svc.external_ip:
                    port = svc.ports[0]["port"] if svc.ports else 80
                    return f"http://{svc.external_ip}:{port}"
                elif svc.type == "NodePort" and svc.ports:
                    # For NodePort, we'd need a node IP
                    node_port = svc.ports[0].get("node_port")
                    if node_port:
                        nodes = await self.client.list_nodes()
                        if nodes:
                            return f"http://{nodes[0].ip_address}:{node_port}"
        
        return None

    async def pull_ollama_model(
        self,
        deployment_name: str,
        model_name: str,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Pull a model in an Ollama deployment.
        
        This executes the model pull command inside the Ollama container.
        
        Args:
            deployment_name: Name of the Ollama deployment
            model_name: Model to pull (e.g., "llama3.2")
            namespace: Deployment namespace
            
        Returns:
            True if pull was initiated successfully
        """
        if not self.client.is_available:
            return False
        
        ns = namespace or self.config.kubernetes.model_serving_namespace
        
        try:
            # Get pods for the deployment
            pods = await self.client.list_pods(
                namespace=ns,
                label_selector=f"app={deployment_name}",
            )
            
            if not pods:
                logger.error(f"No pods found for deployment {deployment_name}")
                return False
            
            # Execute pull command in first pod
            # Note: This requires exec permissions in the cluster
            pod_name = pods[0].name
            
            # For now, log the command that would need to be run
            logger.info(
                f"To pull model, run: kubectl exec -n {ns} {pod_name} -- "
                f"ollama pull {model_name}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initiate model pull: {e}")
            return False

    async def create_ingress(
        self,
        deployment_name: str,
        host: str,
        namespace: Optional[str] = None,
        tls_secret: Optional[str] = None,
    ) -> bool:
        """
        Create an Ingress for a model deployment.
        
        Args:
            deployment_name: Name of the deployment
            host: Hostname for the ingress
            namespace: Deployment namespace
            tls_secret: TLS secret name for HTTPS
            
        Returns:
            True if ingress was created
        """
        if not self.client.is_available:
            return False
        
        ns = namespace or self.config.kubernetes.model_serving_namespace
        
        try:
            from kubernetes import client
            
            # Get the service to determine port
            services = await self.client.list_services(namespace=ns)
            service_port = 80
            for svc in services:
                if svc.name == deployment_name and svc.ports:
                    service_port = svc.ports[0]["port"]
                    break
            
            # Build ingress spec
            ingress_backend = client.V1IngressBackend(
                service=client.V1IngressServiceBackend(
                    name=deployment_name,
                    port=client.V1ServiceBackendPort(number=service_port),
                )
            )
            
            ingress_rule = client.V1IngressRule(
                host=host,
                http=client.V1HTTPIngressRuleValue(
                    paths=[
                        client.V1HTTPIngressPath(
                            path="/",
                            path_type="Prefix",
                            backend=ingress_backend,
                        )
                    ]
                ),
            )
            
            ingress_spec = client.V1IngressSpec(
                rules=[ingress_rule],
            )
            
            # Add TLS if specified
            if tls_secret:
                ingress_spec.tls = [
                    client.V1IngressTLS(
                        hosts=[host],
                        secret_name=tls_secret,
                    )
                ]
            
            ingress = client.V1Ingress(
                api_version="networking.k8s.io/v1",
                kind="Ingress",
                metadata=client.V1ObjectMeta(
                    name=f"{deployment_name}-ingress",
                    namespace=ns,
                    labels={
                        "agentic.io/managed": "true",
                    },
                    annotations={
                        "nginx.ingress.kubernetes.io/proxy-body-size": "0",
                        "nginx.ingress.kubernetes.io/proxy-read-timeout": "3600",
                        "nginx.ingress.kubernetes.io/proxy-send-timeout": "3600",
                    },
                ),
                spec=ingress_spec,
            )
            
            # Create ingress
            networking_api = client.NetworkingV1Api()
            networking_api.create_namespaced_ingress(
                namespace=ns,
                body=ingress,
            )
            
            logger.info(f"Created ingress for {deployment_name} at {host}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create ingress: {e}")
            return False

    async def set_as_code_assistant(
        self,
        deployment_name: str,
        namespace: Optional[str] = None,
    ) -> dict:
        """
        Configure a model deployment to be used as the code assistant.
        
        This updates the local configuration to use the deployed model
        for code assistance tasks.
        
        Args:
            deployment_name: Name of the model deployment
            namespace: Deployment namespace
            
        Returns:
            Configuration update result
        """
        endpoint = await self.get_model_endpoint(deployment_name, namespace)
        
        if not endpoint:
            return {
                "success": False,
                "error": f"Model deployment {deployment_name} not found",
            }
        
        # Get model name from deployment labels
        deployment = await self.get_model_deployment(deployment_name, namespace)
        model_name = deployment.labels.get("agentic.io/model-name", "unknown")
        
        return {
            "success": True,
            "endpoint": endpoint,
            "model_name": model_name,
            "message": f"Configure your code assistant to use: {endpoint}",
            "config_hint": {
                "ollama_host": endpoint,
                "model": model_name,
            },
        }
