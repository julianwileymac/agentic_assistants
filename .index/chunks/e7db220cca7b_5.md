# Chunk: e7db220cca7b_5

- source: `src/agentic_assistants/kubernetes/deployments.py`
- lines: 381-469
- chunk: 6/7

```
-> Optional[DeploymentInfo]:
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

```
