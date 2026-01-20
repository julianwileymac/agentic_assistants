"""
LangFlow adapter with integrated observability.

This adapter wraps LangFlow workflows to provide:
- MLFlow experiment tracking for flow executions
- OpenTelemetry tracing for component interactions
- Standardized metrics and logging
- Visual workflow support

LangFlow is a visual workflow builder for LangChain components that
allows you to build and deploy AI workflows through a drag-and-drop
interface. This adapter allows running LangFlow flows programmatically
with full observability.

Example:
    >>> from agentic_assistants.adapters import LangFlowAdapter
    >>> 
    >>> adapter = LangFlowAdapter()
    >>> 
    >>> # Run a flow from a JSON definition
    >>> result = adapter.run_flow(
    ...     flow_definition=flow_json,
    ...     inputs={"query": "Hello!"},
    ...     experiment_name="chat-flow"
    ... )
    >>> 
    >>> # Or run from a saved flow file
    >>> result = adapter.run_flow_file(
    ...     "path/to/flow.json",
    ...     inputs={"query": "Hello!"}
    ... )
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from agentic_assistants.adapters.base import BaseAdapter
from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class LangFlowAdapter(BaseAdapter):
    """
    Adapter for LangFlow visual workflow integration.
    
    This adapter provides observability wrappers for LangFlow flows,
    tracking component execution, data flow, and overall performance.
    
    LangFlow features:
    - Visual workflow builder
    - LangChain component integration
    - Flow import/export (JSON)
    - API endpoint deployment
    
    Attributes:
        config: Agentic configuration instance
        default_model: Default LLM model for components
        langflow_api_url: URL of LangFlow API server (if running)
    """

    framework_name = "langflow"

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        default_model: Optional[str] = None,
        langflow_api_url: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the LangFlow adapter.
        
        Args:
            config: Configuration instance
            default_model: Default model for LLM components
            langflow_api_url: URL of LangFlow API server
            **kwargs: Additional arguments passed to BaseAdapter
        """
        super().__init__(config, name="LangFlow", **kwargs)
        self.default_model = default_model or self.config.ollama.default_model
        self.langflow_api_url = langflow_api_url or "http://localhost:7860"
        self._langflow_available = self._check_langflow()
        self._flow_cache: Dict[str, Any] = {}

    def _check_langflow(self) -> bool:
        """Check if LangFlow is available."""
        try:
            from langflow import load_flow_from_json
            return True
        except ImportError:
            logger.warning(
                "LangFlow is not installed. Install with: pip install langflow"
            )
            return False

    def run(
        self,
        flow: Any,
        inputs: Dict[str, Any],
        **kwargs,
    ) -> Any:
        """
        Run a flow with inputs.
        
        Args:
            flow: The flow to run (definition or loaded flow)
            inputs: Input values for the flow
            **kwargs: Additional arguments
            
        Returns:
            Flow output
        """
        if isinstance(flow, dict):
            return self.run_flow(flow, inputs, **kwargs)
        else:
            return self.run_loaded_flow(flow, inputs, **kwargs)

    def run_flow(
        self,
        flow_definition: Union[Dict[str, Any], str],
        inputs: Dict[str, Any],
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        tweaks: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Run a LangFlow flow with full observability.
        
        Args:
            flow_definition: Flow JSON definition (dict or string)
            inputs: Input values for the flow
            experiment_name: MLFlow experiment name
            run_name: Name for this run
            tags: Additional tags
            tweaks: Component tweaks/overrides
            
        Returns:
            Flow output
        """
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        actual_run_name = run_name or f"langflow-{time.strftime('%Y%m%d-%H%M%S')}"

        # Parse flow definition if string
        if isinstance(flow_definition, str):
            flow_definition = json.loads(flow_definition)

        params = {
            "framework": "langflow",
            "model": self.default_model,
            "num_components": len(flow_definition.get("nodes", [])),
        }

        all_tags = {"framework": "langflow"}
        if tags:
            all_tags.update(tags)

        with self.track_run(
            actual_run_name,
            tags=all_tags,
            params=params,
            agent_name="langflow_flow",
            model=self.default_model,
        ):
            start_time = time.time()

            try:
                logger.info(f"Starting LangFlow flow: {actual_run_name}")

                # Inject RAG context if available
                if self._knowledge_base and "query" in inputs:
                    results = self.get_rag_context(inputs["query"])
                    if results:
                        inputs["_rag_context"] = "\n".join(
                            r["content"][:500] for r in results[:3]
                        )

                # Run the flow
                if self._langflow_available:
                    result = self._run_langflow(flow_definition, inputs, tweaks)
                else:
                    result = self._run_via_api(flow_definition, inputs, tweaks)

                duration = time.time() - start_time

                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)

                logger.info(f"LangFlow flow completed in {duration:.2f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                self.log_error(e, "langflow_flow")
                raise

    def _run_langflow(
        self,
        flow_definition: Dict[str, Any],
        inputs: Dict[str, Any],
        tweaks: Optional[Dict[str, Any]],
    ) -> Any:
        """Run using the LangFlow library directly."""
        from langflow import load_flow_from_json

        # Apply tweaks if provided
        if tweaks:
            flow_definition = self._apply_tweaks(flow_definition, tweaks)

        # Override Ollama settings
        flow_definition = self._inject_ollama_settings(flow_definition)

        # Load and run the flow
        flow = load_flow_from_json(flow_definition)
        
        # Get the input component
        input_key = list(inputs.keys())[0] if inputs else "input"
        
        return flow(inputs.get(input_key, ""))

    def _run_via_api(
        self,
        flow_definition: Dict[str, Any],
        inputs: Dict[str, Any],
        tweaks: Optional[Dict[str, Any]],
    ) -> Any:
        """Run via LangFlow API server."""
        import httpx

        # Try to use the API server
        try:
            response = httpx.post(
                f"{self.langflow_api_url}/api/v1/run",
                json={
                    "flow": flow_definition,
                    "inputs": inputs,
                    "tweaks": tweaks or {},
                },
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"LangFlow API not available: {e}")
            # Fall back to simple execution
            return self._run_simple(flow_definition, inputs)

    def _run_simple(
        self,
        flow_definition: Dict[str, Any],
        inputs: Dict[str, Any],
    ) -> str:
        """Simple execution without full LangFlow runtime."""
        import httpx

        # Extract the prompt from inputs
        query = inputs.get("query", inputs.get("input", ""))

        # Look for chat/LLM components in the flow
        nodes = flow_definition.get("nodes", [])
        
        # Find the system message from any chat component
        system_message = "You are a helpful assistant."
        for node in nodes:
            data = node.get("data", {})
            if "system_message" in data:
                system_message = data["system_message"]
                break

        # Make a simple chat request
        response = httpx.post(
            f"{self.config.ollama.host}/api/chat",
            json={
                "model": self.default_model,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": query},
                ],
                "stream": False,
            },
            timeout=self.config.ollama.timeout,
        )
        response.raise_for_status()

        return response.json().get("message", {}).get("content", "")

    def _apply_tweaks(
        self,
        flow_definition: Dict[str, Any],
        tweaks: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply tweaks to flow component parameters."""
        flow = flow_definition.copy()
        nodes = flow.get("nodes", [])

        for node in nodes:
            node_id = node.get("id")
            if node_id in tweaks:
                node_tweaks = tweaks[node_id]
                if "data" in node:
                    node["data"].update(node_tweaks)

        return flow

    def _inject_ollama_settings(
        self,
        flow_definition: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Inject Ollama settings into LLM components."""
        flow = flow_definition.copy()
        nodes = flow.get("nodes", [])

        for node in nodes:
            data = node.get("data", {})
            node_type = data.get("type", "")

            # Check if it's an LLM component
            if any(llm in node_type.lower() for llm in ["llm", "chat", "ollama"]):
                data["base_url"] = self.config.ollama.host
                data["model"] = data.get("model", self.default_model)

        return flow

    def run_flow_file(
        self,
        flow_path: Union[str, Path],
        inputs: Dict[str, Any],
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        tweaks: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Run a LangFlow flow from a JSON file.
        
        Args:
            flow_path: Path to the flow JSON file
            inputs: Input values for the flow
            experiment_name: MLFlow experiment name
            run_name: Name for this run
            tags: Additional tags
            tweaks: Component tweaks/overrides
            
        Returns:
            Flow output
        """
        flow_path = Path(flow_path)

        if not flow_path.exists():
            raise FileNotFoundError(f"Flow file not found: {flow_path}")

        with open(flow_path, "r") as f:
            flow_definition = json.load(f)

        return self.run_flow(
            flow_definition,
            inputs,
            experiment_name=experiment_name,
            run_name=run_name or flow_path.stem,
            tags=tags,
            tweaks=tweaks,
        )

    def run_loaded_flow(
        self,
        flow: Any,
        inputs: Dict[str, Any],
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Run an already-loaded LangFlow flow.
        
        Args:
            flow: The loaded flow object
            inputs: Input values
            experiment_name: MLFlow experiment name
            run_name: Name for this run
            tags: Additional tags
            
        Returns:
            Flow output
        """
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        actual_run_name = run_name or f"langflow-{time.strftime('%Y%m%d-%H%M%S')}"

        params = {
            "framework": "langflow",
            "model": self.default_model,
        }

        all_tags = {"framework": "langflow"}
        if tags:
            all_tags.update(tags)

        with self.track_run(
            actual_run_name,
            tags=all_tags,
            params=params,
            agent_name="langflow_flow",
            model=self.default_model,
        ):
            start_time = time.time()

            try:
                # Get the input value
                input_key = list(inputs.keys())[0] if inputs else "input"
                input_value = inputs.get(input_key, "")

                result = flow(input_value)

                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)

                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                self.log_error(e, "langflow_loaded_flow")
                raise

    def load_flow(
        self,
        flow_definition: Union[Dict[str, Any], str, Path],
    ) -> Any:
        """
        Load a flow from a definition.
        
        Args:
            flow_definition: Flow JSON (dict, string, or path)
            
        Returns:
            Loaded flow object
        """
        if isinstance(flow_definition, Path) or (
            isinstance(flow_definition, str) and Path(flow_definition).exists()
        ):
            with open(flow_definition, "r") as f:
                flow_definition = json.load(f)
        elif isinstance(flow_definition, str):
            flow_definition = json.loads(flow_definition)

        if not self._langflow_available:
            raise ImportError("LangFlow is not installed")

        from langflow import load_flow_from_json

        flow_definition = self._inject_ollama_settings(flow_definition)
        return load_flow_from_json(flow_definition)

    def export_flow(
        self,
        flow: Any,
        output_path: Union[str, Path],
    ) -> Path:
        """
        Export a flow to a JSON file.
        
        Args:
            flow: The flow to export
            output_path: Output file path
            
        Returns:
            Path to the exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if hasattr(flow, "to_dict"):
            flow_dict = flow.to_dict()
        elif hasattr(flow, "export"):
            flow_dict = flow.export()
        else:
            raise ValueError("Cannot export flow: no to_dict or export method")

        with open(output_path, "w") as f:
            json.dump(flow_dict, f, indent=2)

        return output_path

    def list_components(self) -> List[Dict[str, Any]]:
        """
        List available LangFlow components.
        
        Returns:
            List of component information
        """
        if not self._langflow_available:
            return []

        try:
            from langflow.components import get_all_components

            components = get_all_components()
            return [
                {
                    "name": c.__name__,
                    "type": c.component_type if hasattr(c, "component_type") else "unknown",
                    "description": c.__doc__ or "",
                }
                for c in components
            ]
        except Exception as e:
            logger.warning(f"Failed to list components: {e}")
            return []

    async def deploy_flow(
        self,
        flow_id: str,
        name: str,
        flow_definition: Dict[str, Any],
        namespace: Optional[str] = None,
        model_endpoint: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Deploy a LangFlow flow to Kubernetes.
        
        Args:
            flow_id: Unique identifier for the flow
            name: Deployment name
            flow_definition: Flow JSON definition
            namespace: Kubernetes namespace
            model_endpoint: LLM endpoint URL
            **kwargs: Additional deployment parameters
            
        Returns:
            DeploymentInfo if successful
        """
        from agentic_assistants.kubernetes import (
            DeploymentManager,
            FlowDeploymentConfig,
            ResourceRequirements,
        )

        deployer = DeploymentManager(config=self.config)

        resources = ResourceRequirements(
            cpu_request=kwargs.get("cpu_request", "100m"),
            cpu_limit=kwargs.get("cpu_limit", "1000m"),
            memory_request=kwargs.get("memory_request", "512Mi"),
            memory_limit=kwargs.get("memory_limit", "2Gi"),
        )

        config = FlowDeploymentConfig(
            flow_id=flow_id,
            name=name,
            namespace=namespace or self.config.kubernetes.default_deploy_namespace,
            replicas=kwargs.get("replicas", 1),
            framework="langflow",
            model_endpoint=model_endpoint,
            state_backend=kwargs.get("state_backend", "minio"),
            env_vars={"FLOW_DEFINITION": json.dumps(flow_definition)},
            resources=resources,
        )

        deployment = await deployer.deploy_flow(config)

        if deployment:
            logger.info(f"Deployed LangFlow flow {name} to Kubernetes")
        else:
            logger.error(f"Failed to deploy LangFlow flow {name}")

        return deployment

    def create_simple_chat_flow(
        self,
        system_message: str = "You are a helpful assistant.",
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a simple chat flow definition.
        
        This is a helper method to create a basic flow without
        using the LangFlow UI.
        
        Args:
            system_message: System message for the chat
            model: Model to use
            
        Returns:
            Flow definition dictionary
        """
        return {
            "nodes": [
                {
                    "id": "chat-1",
                    "type": "chat",
                    "data": {
                        "type": "OllamaChat",
                        "model": model or self.default_model,
                        "base_url": self.config.ollama.host,
                        "system_message": system_message,
                    },
                },
            ],
            "edges": [],
        }
