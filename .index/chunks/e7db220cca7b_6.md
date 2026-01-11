# Chunk: e7db220cca7b_6

- source: `src/agentic_assistants/kubernetes/deployments.py`
- lines: 459-523
- chunk: 7/7

```
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
```
