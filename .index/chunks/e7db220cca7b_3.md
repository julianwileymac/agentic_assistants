# Chunk: e7db220cca7b_3

- source: `src/agentic_assistants/kubernetes/deployments.py`
- lines: 221-311
- chunk: 4/7

```
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
```
