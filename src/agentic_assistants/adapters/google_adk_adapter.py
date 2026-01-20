"""
Google Agent Development Kit (ADK) adapter with integrated observability.

This adapter wraps Google's ADK agents to provide:
- MLFlow experiment tracking for agent runs
- OpenTelemetry tracing for agent interactions
- Standardized metrics and logging

Note: Google ADK is still in development. This adapter provides a
forward-compatible interface that will be fully implemented when
the ADK is publicly released.

Example:
    >>> from agentic_assistants.adapters import GoogleADKAdapter
    >>> 
    >>> adapter = GoogleADKAdapter()
    >>> 
    >>> # Create an agent
    >>> agent = adapter.create_agent(
    ...     name="assistant",
    ...     instructions="You are a helpful assistant.",
    ... )
    >>> 
    >>> # Run with tracking
    >>> result = adapter.run(agent, query="Hello!")
"""

import time
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.adapters.base import BaseAdapter
from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class GoogleADKAdapter(BaseAdapter):
    """
    Adapter for Google Agent Development Kit (ADK) integration.
    
    This adapter provides observability wrappers for Google ADK agents,
    tracking agent runs, tool calls, and session management.
    
    Google ADK features:
    - Agent: Core agent abstraction
    - Tools: Function calling capabilities
    - Sessions: Conversation state management
    - Memory: Built-in memory systems
    
    Attributes:
        config: Agentic configuration instance
        default_model: Default LLM model for agents
    """

    framework_name = "google_adk"

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        default_model: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the Google ADK adapter.
        
        Args:
            config: Configuration instance
            default_model: Default model for agents (uses config default if None)
            **kwargs: Additional arguments passed to BaseAdapter
        """
        super().__init__(config, name="GoogleADK", **kwargs)
        self.default_model = default_model or self.config.ollama.default_model
        self._adk_available = self._check_adk()
        self._sessions: Dict[str, Any] = {}

    def _check_adk(self) -> bool:
        """Check if Google ADK is available."""
        try:
            # Google ADK import - will be updated when package is released
            # For now, we check for the genai package as a proxy
            import google.generativeai as genai
            return True
        except ImportError:
            logger.warning(
                "Google ADK/GenAI is not installed. "
                "Install with: pip install google-generativeai"
            )
            return False

    def run(
        self,
        agent: Any,
        query: str,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Run an agent with a query.
        
        Args:
            agent: The ADK agent to run
            query: User query/input
            session_id: Optional session ID for conversation continuity
            **kwargs: Additional arguments
            
        Returns:
            Agent response
        """
        return self.run_agent(agent, query, session_id=session_id, **kwargs)

    def run_agent(
        self,
        agent: Any,
        query: str,
        session_id: Optional[str] = None,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        context: Optional[str] = None,
    ) -> Any:
        """
        Run a Google ADK agent with full observability.
        
        Args:
            agent: The ADK agent to run
            query: User query/input
            session_id: Session ID for conversation continuity
            experiment_name: MLFlow experiment name
            run_name: Name for this run
            tags: Additional tags
            context: Additional context to provide
            
        Returns:
            Agent response
        """
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        actual_run_name = run_name or f"adk-{time.strftime('%Y%m%d-%H%M%S')}"

        params = {
            "framework": "google_adk",
            "model": self.default_model,
            "session_id": session_id,
        }

        all_tags = {"framework": "google_adk"}
        if tags:
            all_tags.update(tags)

        with self.track_run(
            actual_run_name,
            tags=all_tags,
            params=params,
            agent_name=getattr(agent, "name", "adk_agent"),
            model=self.default_model,
        ):
            start_time = time.time()

            try:
                logger.info(f"Starting Google ADK agent: {actual_run_name}")

                # Get RAG context if available
                full_query = query
                if self._knowledge_base:
                    results = self.get_rag_context(query)
                    if results:
                        rag_context = "\n\nRelevant context:\n" + "\n".join(
                            f"- {r['content'][:500]}" for r in results[:3]
                        )
                        full_query = query + rag_context

                # Add explicit context if provided
                if context:
                    full_query = f"Context: {context}\n\nQuery: {full_query}"

                # Run the agent
                # Note: This will be updated when ADK API is finalized
                if hasattr(agent, "run"):
                    result = agent.run(full_query)
                elif hasattr(agent, "generate"):
                    result = agent.generate(full_query)
                elif hasattr(agent, "chat"):
                    result = agent.chat(full_query)
                else:
                    # Fallback for generic callable
                    result = agent(full_query)

                duration = time.time() - start_time

                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)

                # Store in memory if enabled
                if self._memory:
                    self.store_memory(
                        f"Q: {query[:200]}\nA: {str(result)[:500]}",
                        {"type": "conversation", "agent": actual_run_name},
                    )

                logger.info(f"Google ADK agent completed in {duration:.2f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                self.log_error(e, "google_adk_agent")
                raise

    def create_agent(
        self,
        name: str,
        instructions: str,
        model: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        **kwargs,
    ) -> Any:
        """
        Create a Google ADK agent.
        
        Args:
            name: Agent name
            instructions: System instructions for the agent
            model: Model to use (uses default if None)
            tools: List of tool functions
            **kwargs: Additional agent parameters
            
        Returns:
            Configured ADK agent
        """
        if not self._adk_available:
            raise ImportError(
                "Google ADK is not installed. Install with: pip install google-generativeai"
            )

        # This will be updated when ADK is released
        # For now, create a wrapper class
        return ADKAgentWrapper(
            name=name,
            instructions=instructions,
            model=model or self.default_model,
            tools=tools or [],
            config=self.config,
            **kwargs,
        )

    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new conversation session.
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            The session ID
        """
        import uuid
        
        sid = session_id or str(uuid.uuid4())
        self._sessions[sid] = {
            "messages": [],
            "created_at": time.time(),
        }
        return sid

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def add_to_session(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        """Add a message to a session."""
        if session_id in self._sessions:
            self._sessions[session_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": time.time(),
            })

    def clear_session(self, session_id: str) -> bool:
        """Clear a session's message history."""
        if session_id in self._sessions:
            self._sessions[session_id]["messages"] = []
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    async def deploy_agent(
        self,
        agent_id: str,
        name: str,
        instructions: str,
        namespace: Optional[str] = None,
        model_endpoint: Optional[str] = None,
        tools: Optional[List[str]] = None,
        **kwargs,
    ) -> Any:
        """
        Deploy a Google ADK agent to Kubernetes.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Deployment name
            instructions: Agent instructions
            namespace: Kubernetes namespace
            model_endpoint: LLM endpoint URL
            tools: List of tool names
            **kwargs: Additional deployment parameters
            
        Returns:
            DeploymentInfo if successful
        """
        from agentic_assistants.kubernetes import (
            DeploymentManager,
            AgentDeploymentConfig,
            ResourceRequirements,
        )

        deployer = DeploymentManager(config=self.config)

        resources = ResourceRequirements(
            cpu_request=kwargs.get("cpu_request", "100m"),
            cpu_limit=kwargs.get("cpu_limit", "1000m"),
            memory_request=kwargs.get("memory_request", "256Mi"),
            memory_limit=kwargs.get("memory_limit", "1Gi"),
        )

        config = AgentDeploymentConfig(
            agent_id=agent_id,
            name=name,
            namespace=namespace or self.config.kubernetes.default_deploy_namespace,
            replicas=kwargs.get("replicas", 1),
            framework="google_adk",
            model_endpoint=model_endpoint,
            tools=tools or [],
            env_vars={"AGENT_INSTRUCTIONS": instructions},
            resources=resources,
        )

        deployment = await deployer.deploy_agent(config)

        if deployment:
            logger.info(f"Deployed Google ADK agent {name} to Kubernetes")
        else:
            logger.error(f"Failed to deploy Google ADK agent {name}")

        return deployment


class ADKAgentWrapper:
    """
    Wrapper class for Google ADK agent functionality.
    
    This provides a consistent interface while the actual ADK
    is in development. It can use the Google GenAI API or
    fall back to local Ollama.
    """

    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        tools: List[Callable],
        config: AgenticConfig,
        **kwargs,
    ):
        """Initialize the agent wrapper."""
        self.name = name
        self.instructions = instructions
        self.model = model
        self.tools = tools
        self.config = config
        self._history: List[Dict[str, str]] = []
        self._use_local = kwargs.get("use_local", True)

    def run(self, query: str) -> str:
        """Run the agent with a query."""
        return self.generate(query)

    def generate(self, query: str) -> str:
        """Generate a response to the query."""
        if self._use_local:
            return self._generate_local(query)
        else:
            return self._generate_google(query)

    def _generate_local(self, query: str) -> str:
        """Generate using local Ollama."""
        import httpx

        messages = [{"role": "system", "content": self.instructions}]
        messages.extend(self._history)
        messages.append({"role": "user", "content": query})

        response = httpx.post(
            f"{self.config.ollama.host}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
            },
            timeout=self.config.ollama.timeout,
        )
        response.raise_for_status()

        result = response.json()
        content = result.get("message", {}).get("content", "")

        # Update history
        self._history.append({"role": "user", "content": query})
        self._history.append({"role": "assistant", "content": content})

        return content

    def _generate_google(self, query: str) -> str:
        """Generate using Google GenAI API."""
        try:
            import google.generativeai as genai

            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                f"{self.instructions}\n\nUser: {query}"
            )
            return response.text
        except Exception as e:
            logger.warning(f"Google GenAI failed, falling back to local: {e}")
            return self._generate_local(query)

    def chat(self, query: str) -> str:
        """Alias for generate."""
        return self.generate(query)

    def reset(self) -> None:
        """Reset conversation history."""
        self._history = []

    def __call__(self, query: str) -> str:
        """Make the agent callable."""
        return self.generate(query)
