# Chunk: e7db220cca7b_1

- source: `src/agentic_assistants/kubernetes/deployments.py`
- lines: 86-161
- chunk: 2/7

```
est,
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
```
