# Chunk: e7db220cca7b_4

- source: `src/agentic_assistants/kubernetes/deployments.py`
- lines: 302-391
- chunk: 5/7

```
f"Scaled deployment {name} to {replicas} replicas")
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
```
