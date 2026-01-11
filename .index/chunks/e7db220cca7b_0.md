# Chunk: e7db220cca7b_0

- source: `src/agentic_assistants/kubernetes/deployments.py`
- lines: 1-94
- chunk: 1/7

```
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
```
