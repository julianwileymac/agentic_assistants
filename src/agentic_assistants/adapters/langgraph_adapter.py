"""
LangGraph framework adapter with integrated observability.

This adapter wraps LangGraph workflows to provide:
- MLFlow experiment tracking for graph execution
- OpenTelemetry tracing for node transitions
- Standardized metrics and logging

Example:
    >>> from langgraph.graph import StateGraph
    >>> from agentic_assistants.adapters import LangGraphAdapter
    >>> 
    >>> adapter = LangGraphAdapter()
    >>> 
    >>> # Create your graph
    >>> graph = StateGraph(MyState)
    >>> graph.add_node("process", process_fn)
    >>> ...
    >>> 
    >>> # Run with tracking
    >>> result = adapter.run_graph(
    ...     graph.compile(),
    ...     inputs={"query": "Hello"},
    ...     experiment_name="workflow-experiment"
    ... )
"""

import time
from typing import Any, Callable, Optional, TypeVar

from agentic_assistants.adapters.base import BaseAdapter
from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

StateType = TypeVar("StateType")


class LangGraphAdapter(BaseAdapter):
    """
    Adapter for LangGraph framework integration.
    
    This adapter provides observability wrappers for LangGraph workflows,
    tracking node execution, state transitions, and graph performance.
    
    Attributes:
        config: Agentic configuration instance
        default_model: Default LLM model for nodes
    """

    framework_name = "langgraph"

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        default_model: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the LangGraph adapter.
        
        Args:
            config: Configuration instance
            default_model: Default model for LLM nodes (uses config default if None)
            **kwargs: Additional arguments passed to BaseAdapter
        """
        super().__init__(config, name="LangGraph", **kwargs)
        self.default_model = default_model or self.config.ollama.default_model

    def run(self, graph: Any, inputs: dict, **kwargs) -> Any:
        """
        Run a LangGraph workflow with tracking.
        
        This is a convenience method that calls run_graph.
        
        Args:
            graph: The compiled LangGraph
            inputs: Input state dictionary
            **kwargs: Additional arguments passed to run_graph
        
        Returns:
            Graph execution result
        """
        return self.run_graph(graph, inputs, **kwargs)

    def run_graph(
        self,
        graph: Any,
        inputs: dict,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
        config: Optional[dict] = None,
    ) -> Any:
        """
        Run a LangGraph workflow with full observability.
        
        Args:
            graph: The compiled LangGraph to run
            inputs: Input state dictionary
            experiment_name: MLFlow experiment name (optional)
            run_name: Name for this run
            tags: Additional tags for the run
            config: LangGraph config (e.g., for recursion limit)
        
        Returns:
            The final state after graph execution
        
        Example:
            >>> graph = workflow.compile()
            >>> result = adapter.run_graph(
            ...     graph,
            ...     inputs={"messages": [HumanMessage("Hello")]},
            ...     experiment_name="chat-workflow"
            ... )
        """
        # Set experiment if specified
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        # Build run name
        actual_run_name = run_name or f"graph-{time.strftime('%Y%m%d-%H%M%S')}"

        # Build parameters
        params = {
            "framework": "langgraph",
            "model": self.default_model,
            "input_keys": list(inputs.keys()),
        }

        # Build tags
        all_tags = {"framework": "langgraph"}
        if tags:
            all_tags.update(tags)

        with self.track_run(actual_run_name, tags=all_tags, params=params):
            start_time = time.time()

            try:
                logger.info(f"Starting LangGraph workflow: {actual_run_name}")

                # Run the graph
                result = graph.invoke(inputs, config=config)

                duration = time.time() - start_time

                # Log success metrics
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)

                # Log final state summary
                if isinstance(result, dict):
                    self.tracker.log_dict(
                        {k: str(v)[:1000] for k, v in result.items()},
                        "output/final_state.json",
                    )

                logger.info(f"Graph completed in {duration:.2f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                logger.error(f"Graph failed after {duration:.2f}s: {e}")
                raise

    def stream_graph(
        self,
        graph: Any,
        inputs: dict,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        config: Optional[dict] = None,
    ):
        """
        Stream a LangGraph workflow with tracking.
        
        This method yields intermediate states as the graph executes,
        while still tracking the full execution.
        
        Args:
            graph: The compiled LangGraph to run
            inputs: Input state dictionary
            experiment_name: MLFlow experiment name (optional)
            run_name: Name for this run
            config: LangGraph config
        
        Yields:
            Intermediate states during execution
        """
        # Set experiment if specified
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        actual_run_name = run_name or f"graph-stream-{time.strftime('%Y%m%d-%H%M%S')}"

        params = {
            "framework": "langgraph",
            "mode": "streaming",
            "model": self.default_model,
        }

        with self.track_run(actual_run_name, params=params):
            start_time = time.time()
            step_count = 0

            try:
                for state in graph.stream(inputs, config=config):
                    step_count += 1
                    self.tracker.log_metric("steps", step_count)

                    with self.track_step(f"step-{step_count}", step_number=step_count):
                        yield state

                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)
                self.tracker.log_metric("total_steps", step_count)

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                raise

    def wrap_node(
        self,
        node_fn: Callable[[StateType], StateType],
        node_name: str,
    ) -> Callable[[StateType], StateType]:
        """
        Wrap a node function with observability.
        
        This creates a wrapper that traces node execution and logs metrics.
        
        Args:
            node_fn: The node function to wrap
            node_name: Name for the node (used in traces)
        
        Returns:
            Wrapped function with tracing
        
        Example:
            >>> def process_node(state):
            ...     return {"result": process(state["input"])}
            >>> 
            >>> wrapped = adapter.wrap_node(process_node, "process")
            >>> graph.add_node("process", wrapped)
        """

        def wrapped(state: StateType) -> StateType:
            with self.telemetry.span(
                f"node.{node_name}",
                attributes={"node.name": node_name},
            ) as span:
                start_time = time.time()
                try:
                    result = node_fn(state)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.record_exception(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    span.set_attribute("duration_seconds", duration)

        wrapped.__name__ = node_fn.__name__
        wrapped.__doc__ = node_fn.__doc__
        return wrapped

    def create_ollama_llm(self, model: Optional[str] = None) -> Any:
        """
        Create a LangChain ChatOllama instance.
        
        Args:
            model: Model name (uses default if None)
        
        Returns:
            Configured ChatOllama instance
        """
        try:
            from langchain_ollama import ChatOllama
        except ImportError as e:
            raise ImportError(
                "langchain-ollama is required. Install with: pip install langchain-ollama"
            ) from e

        return ChatOllama(
            model=model or self.default_model,
            base_url=self.config.ollama.host,
        )

    def create_state_graph(self, state_class: type) -> Any:
        """
        Create a new StateGraph.
        
        Args:
            state_class: The state class (TypedDict or Pydantic model)
        
        Returns:
            New StateGraph instance
        """
        try:
            from langgraph.graph import StateGraph
        except ImportError as e:
            raise ImportError(
                "langgraph is required. Install with: pip install langgraph"
            ) from e

        return StateGraph(state_class)

    async def deploy_graph(
        self,
        flow_id: str,
        name: str,
        namespace: Optional[str] = None,
        replicas: int = 1,
        model_endpoint: Optional[str] = None,
        state_backend: str = "minio",
        env_vars: Optional[dict[str, str]] = None,
        cpu_request: str = "100m",
        cpu_limit: str = "1000m",
        memory_request: str = "256Mi",
        memory_limit: str = "1Gi",
    ) -> Any:
        """
        Deploy a LangGraph workflow to Kubernetes.
        
        This method creates a Kubernetes deployment for running the graph
        as a persistent service with distributed state management.
        
        Args:
            flow_id: Unique identifier for the flow
            name: Deployment name
            namespace: Kubernetes namespace (uses default if None)
            replicas: Number of replicas
            model_endpoint: LLM endpoint URL
            state_backend: State backend (minio, redis)
            env_vars: Additional environment variables
            cpu_request: CPU request
            cpu_limit: CPU limit
            memory_request: Memory request
            memory_limit: Memory limit
        
        Returns:
            DeploymentInfo if successful
        
        Example:
            >>> deployment = await adapter.deploy_graph(
            ...     flow_id="chat-flow-001",
            ...     name="chat-flow",
            ...     model_endpoint="http://ollama.model-serving:11434",
            ...     state_backend="minio"
            ... )
        """
        from agentic_assistants.kubernetes import (
            DeploymentManager,
            FlowDeploymentConfig,
            ResourceRequirements,
        )
        
        deployer = DeploymentManager(config=self.config)
        
        resources = ResourceRequirements(
            cpu_request=cpu_request,
            cpu_limit=cpu_limit,
            memory_request=memory_request,
            memory_limit=memory_limit,
        )
        
        config = FlowDeploymentConfig(
            flow_id=flow_id,
            name=name,
            namespace=namespace or self.config.kubernetes.default_deploy_namespace,
            replicas=replicas,
            framework="langgraph",
            model_endpoint=model_endpoint,
            state_backend=state_backend,
            env_vars=env_vars or {},
            resources=resources,
        )
        
        deployment = await deployer.deploy_flow(config)
        
        if deployment:
            logger.info(f"Deployed graph {name} to Kubernetes")
        else:
            logger.error(f"Failed to deploy graph {name}")
        
        return deployment

    async def undeploy_graph(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Remove a graph deployment from Kubernetes.
        
        Args:
            name: Deployment name
            namespace: Kubernetes namespace
        
        Returns:
            True if successfully deleted
        """
        from agentic_assistants.kubernetes import DeploymentManager
        
        deployer = DeploymentManager(config=self.config)
        ns = namespace or self.config.kubernetes.default_deploy_namespace
        
        success = await deployer.delete_deployment(name, ns)
        
        if success:
            logger.info(f"Undeployed graph {name} from Kubernetes")
        else:
            logger.error(f"Failed to undeploy graph {name}")
        
        return success

    async def get_graph_deployment_status(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> dict:
        """
        Get the status of a graph deployment.
        
        Args:
            name: Deployment name
            namespace: Kubernetes namespace
        
        Returns:
            Deployment status dict
        """
        from agentic_assistants.kubernetes import DeploymentManager
        
        deployer = DeploymentManager(config=self.config)
        ns = namespace or self.config.kubernetes.default_deploy_namespace
        
        return await deployer.get_deployment_status(name, ns)
