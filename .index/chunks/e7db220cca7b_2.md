# Chunk: e7db220cca7b_2

- source: `src/agentic_assistants/kubernetes/deployments.py`
- lines: 153-230
- chunk: 3/7

```
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
```
