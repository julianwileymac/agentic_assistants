"""
Agno framework adapter with integrated observability.

This adapter wraps Agno agents and teams to provide:
- MLFlow experiment tracking for agent runs
- OpenTelemetry tracing for agent interactions
- Standardized metrics and logging
- Multi-model and team support

Agno is a modern agent framework with features like:
- Multi-model support (can use different LLMs for different agents)
- Reasoning modes (chain-of-thought, ReAct, etc.)
- Team collaboration
- Built-in memory and knowledge systems

Example:
    >>> from agentic_assistants.adapters import AgnoAdapter
    >>> 
    >>> adapter = AgnoAdapter()
    >>> 
    >>> # Create an agent
    >>> agent = adapter.create_agent(
    ...     name="researcher",
    ...     instructions="You are a research assistant.",
    ... )
    >>> 
    >>> # Run with tracking
    >>> result = adapter.run(agent, query="What is quantum computing?")
"""

import time
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.adapters.base import BaseAdapter
from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class AgnoAdapter(BaseAdapter):
    """
    Adapter for Agno framework integration.
    
    This adapter provides observability wrappers for Agno agents,
    tracking agent runs, team collaborations, and reasoning processes.
    
    Agno features:
    - Agent: Core agent abstraction with multi-model support
    - Team: Multi-agent collaboration
    - Reasoning modes: Different reasoning strategies
    - Knowledge: Built-in knowledge management
    - Memory: Conversation and long-term memory
    
    Attributes:
        config: Agentic configuration instance
        default_model: Default LLM model for agents
    """

    framework_name = "agno"

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        default_model: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the Agno adapter.
        
        Args:
            config: Configuration instance
            default_model: Default model for agents (uses config default if None)
            **kwargs: Additional arguments passed to BaseAdapter
        """
        super().__init__(config, name="Agno", **kwargs)
        self.default_model = default_model or self.config.ollama.default_model
        self._agno_available = self._check_agno()

    def _check_agno(self) -> bool:
        """Check if Agno is available."""
        try:
            import agno
            return True
        except ImportError:
            logger.warning(
                "Agno is not installed. Install with: pip install agno"
            )
            return False

    def run(
        self,
        agent: Any,
        query: str,
        **kwargs,
    ) -> Any:
        """
        Run an agent with a query.
        
        Args:
            agent: The Agno agent to run
            query: User query/input
            **kwargs: Additional arguments
            
        Returns:
            Agent response
        """
        return self.run_agent(agent, query, **kwargs)

    def run_agent(
        self,
        agent: Any,
        query: str,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        reasoning_mode: Optional[str] = None,
        stream: bool = False,
    ) -> Any:
        """
        Run an Agno agent with full observability.
        
        Args:
            agent: The Agno agent to run
            query: User query/input
            experiment_name: MLFlow experiment name
            run_name: Name for this run
            tags: Additional tags
            reasoning_mode: Reasoning strategy (cot, react, etc.)
            stream: Whether to stream the response
            
        Returns:
            Agent response
        """
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        actual_run_name = run_name or f"agno-{time.strftime('%Y%m%d-%H%M%S')}"

        params = {
            "framework": "agno",
            "model": getattr(agent, "model", self.default_model),
            "reasoning_mode": reasoning_mode,
            "stream": stream,
        }

        all_tags = {"framework": "agno"}
        if tags:
            all_tags.update(tags)

        with self.track_run(
            actual_run_name,
            tags=all_tags,
            params=params,
            agent_name=getattr(agent, "name", "agno_agent"),
            model=params["model"],
        ):
            start_time = time.time()

            try:
                logger.info(f"Starting Agno agent: {actual_run_name}")

                # Get RAG context if available
                full_query = query
                if self._knowledge_base:
                    results = self.get_rag_context(query)
                    if results:
                        rag_context = "\n\nRelevant context:\n" + "\n".join(
                            f"- {r['content'][:500]}" for r in results[:3]
                        )
                        full_query = query + rag_context

                # Get memory context if available
                if self._memory:
                    memories = self.get_memory_context(query, limit=5)
                    if memories:
                        memory_context = "\n\nRelevant memories:\n" + "\n".join(
                            f"- {m.get('content', '')[:200]}" for m in memories[:3]
                        )
                        full_query = full_query + memory_context

                # Run the agent
                if self._agno_available:
                    result = self._run_agno_agent(agent, full_query, reasoning_mode, stream)
                else:
                    result = self._run_fallback(agent, full_query)

                duration = time.time() - start_time

                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)

                # Store in memory
                if self._memory:
                    self.store_memory(
                        f"Q: {query[:200]}\nA: {str(result)[:500]}",
                        {"type": "conversation", "agent": actual_run_name},
                    )

                logger.info(f"Agno agent completed in {duration:.2f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                self.log_error(e, "agno_agent")
                raise

    def _run_agno_agent(
        self,
        agent: Any,
        query: str,
        reasoning_mode: Optional[str],
        stream: bool,
    ) -> Any:
        """Run using the actual Agno library."""
        import agno

        # Set reasoning mode if specified
        if reasoning_mode and hasattr(agent, "reasoning"):
            agent.reasoning = reasoning_mode

        # Run the agent
        if stream:
            response_parts = []
            for chunk in agent.run(query, stream=True):
                response_parts.append(chunk)
            return "".join(response_parts)
        else:
            return agent.run(query)

    def _run_fallback(self, agent: Any, query: str) -> str:
        """Run using fallback (for when Agno isn't installed)."""
        if hasattr(agent, "run"):
            return agent.run(query)
        elif hasattr(agent, "generate"):
            return agent.generate(query)
        elif callable(agent):
            return agent(query)
        else:
            raise ValueError("Agent doesn't have a run method")

    def create_agent(
        self,
        name: str,
        instructions: Optional[str] = None,
        model: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        reasoning: str = "default",
        show_tool_calls: bool = False,
        markdown: bool = True,
        **kwargs,
    ) -> Any:
        """
        Create an Agno agent.
        
        Args:
            name: Agent name
            instructions: System instructions for the agent
            model: Model to use (uses default if None)
            tools: List of tool functions
            reasoning: Reasoning mode (default, cot, react)
            show_tool_calls: Whether to show tool calls in output
            markdown: Whether to format output as markdown
            **kwargs: Additional agent parameters
            
        Returns:
            Configured Agno agent
        """
        if not self._agno_available:
            # Return a wrapper that works without Agno
            return AgnoAgentWrapper(
                name=name,
                instructions=instructions,
                model=model or self.default_model,
                tools=tools or [],
                config=self.config,
                reasoning=reasoning,
            )

        import agno
        from agno import Agent

        # Configure model for Ollama
        model_config = agno.Ollama(
            model=model or self.default_model,
            host=self.config.ollama.host,
        )

        return Agent(
            name=name,
            model=model_config,
            instructions=instructions,
            tools=tools or [],
            reasoning=reasoning,
            show_tool_calls=show_tool_calls,
            markdown=markdown,
            **kwargs,
        )

    def create_team(
        self,
        name: str,
        agents: List[Any],
        mode: str = "coordinate",
        show_tool_calls: bool = False,
        **kwargs,
    ) -> Any:
        """
        Create an Agno team of agents.
        
        Args:
            name: Team name
            agents: List of agents in the team
            mode: Team mode (coordinate, route, etc.)
            show_tool_calls: Whether to show tool calls
            **kwargs: Additional team parameters
            
        Returns:
            Configured Agno team
        """
        if not self._agno_available:
            return AgnoTeamWrapper(
                name=name,
                agents=agents,
                mode=mode,
                config=self.config,
            )

        import agno
        from agno import Team

        return Team(
            name=name,
            agents=agents,
            mode=mode,
            show_tool_calls=show_tool_calls,
            **kwargs,
        )

    def run_team(
        self,
        team: Any,
        query: str,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Run an Agno team with full observability.
        
        Args:
            team: The Agno team to run
            query: User query/input
            experiment_name: MLFlow experiment name
            run_name: Name for this run
            tags: Additional tags
            
        Returns:
            Team response
        """
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        actual_run_name = run_name or f"agno-team-{time.strftime('%Y%m%d-%H%M%S')}"

        params = {
            "framework": "agno",
            "mode": "team",
            "model": self.default_model,
        }

        all_tags = {"framework": "agno", "mode": "team"}
        if tags:
            all_tags.update(tags)

        with self.track_run(
            actual_run_name,
            tags=all_tags,
            params=params,
            agent_name=getattr(team, "name", "agno_team"),
            model=self.default_model,
        ):
            start_time = time.time()

            try:
                logger.info(f"Starting Agno team: {actual_run_name}")

                # Get RAG context
                full_query = query
                if self._knowledge_base:
                    results = self.get_rag_context(query)
                    if results:
                        rag_context = "\n\nRelevant context:\n" + "\n".join(
                            f"- {r['content'][:500]}" for r in results[:3]
                        )
                        full_query = query + rag_context

                # Run the team
                if hasattr(team, "run"):
                    result = team.run(full_query)
                else:
                    result = team(full_query)

                duration = time.time() - start_time

                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)

                logger.info(f"Agno team completed in {duration:.2f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                self.log_error(e, "agno_team")
                raise

    async def deploy_agent(
        self,
        agent_id: str,
        name: str,
        instructions: str,
        namespace: Optional[str] = None,
        model_endpoint: Optional[str] = None,
        tools: Optional[List[str]] = None,
        reasoning: str = "default",
        **kwargs,
    ) -> Any:
        """
        Deploy an Agno agent to Kubernetes.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Deployment name
            instructions: Agent instructions
            namespace: Kubernetes namespace
            model_endpoint: LLM endpoint URL
            tools: List of tool names
            reasoning: Reasoning mode
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
            framework="agno",
            model_endpoint=model_endpoint,
            tools=tools or [],
            env_vars={
                "AGENT_INSTRUCTIONS": instructions,
                "REASONING_MODE": reasoning,
            },
            resources=resources,
        )

        deployment = await deployer.deploy_agent(config)

        if deployment:
            logger.info(f"Deployed Agno agent {name} to Kubernetes")
        else:
            logger.error(f"Failed to deploy Agno agent {name}")

        return deployment


class AgnoAgentWrapper:
    """
    Wrapper class for Agno agent functionality.
    
    Provides a consistent interface when Agno isn't installed.
    """

    def __init__(
        self,
        name: str,
        instructions: Optional[str],
        model: str,
        tools: List[Callable],
        config: AgenticConfig,
        reasoning: str = "default",
    ):
        """Initialize the agent wrapper."""
        self.name = name
        self.instructions = instructions or "You are a helpful assistant."
        self.model = model
        self.tools = tools
        self.config = config
        self.reasoning = reasoning
        self._history: List[Dict[str, str]] = []

    def run(self, query: str, stream: bool = False) -> str:
        """Run the agent with a query."""
        import httpx

        # Build system message based on reasoning mode
        system_content = self.instructions
        if self.reasoning == "cot":
            system_content += "\n\nThink step by step before answering."
        elif self.reasoning == "react":
            system_content += "\n\nUse the Reason-Act pattern: first reason about the task, then act."

        messages = [{"role": "system", "content": system_content}]
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

    def reset(self) -> None:
        """Reset conversation history."""
        self._history = []

    def __call__(self, query: str) -> str:
        """Make the agent callable."""
        return self.run(query)


class AgnoTeamWrapper:
    """
    Wrapper class for Agno team functionality.
    """

    def __init__(
        self,
        name: str,
        agents: List[Any],
        mode: str,
        config: AgenticConfig,
    ):
        """Initialize the team wrapper."""
        self.name = name
        self.agents = agents
        self.mode = mode
        self.config = config

    def run(self, query: str) -> str:
        """Run the team with a query."""
        # Simple sequential execution of agents
        current_response = query
        all_responses = []

        for agent in self.agents:
            if hasattr(agent, "run"):
                response = agent.run(current_response)
            elif callable(agent):
                response = agent(current_response)
            else:
                continue

            all_responses.append(f"[{getattr(agent, 'name', 'Agent')}]: {response}")
            current_response = response

        return "\n\n".join(all_responses)

    def __call__(self, query: str) -> str:
        """Make the team callable."""
        return self.run(query)
