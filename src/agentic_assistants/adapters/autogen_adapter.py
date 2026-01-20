"""
Microsoft AutoGen framework adapter with integrated observability.

This adapter wraps AutoGen agents and conversations to provide:
- MLFlow experiment tracking for conversations
- OpenTelemetry tracing for agent interactions
- Standardized metrics and logging
- Multi-agent conversation support

Example:
    >>> from agentic_assistants.adapters import AutoGenAdapter
    >>> 
    >>> adapter = AutoGenAdapter()
    >>> 
    >>> # Create agents
    >>> assistant = adapter.create_assistant_agent("assistant", system_message="You are helpful.")
    >>> user_proxy = adapter.create_user_proxy_agent("user_proxy")
    >>> 
    >>> # Run conversation with tracking
    >>> result = adapter.run_conversation(
    ...     user_proxy,
    ...     assistant,
    ...     message="Write a Python function to calculate fibonacci numbers",
    ...     experiment_name="code-gen-experiment"
    ... )
"""

import time
from typing import Any, Callable, Dict, List, Optional, Union

from agentic_assistants.adapters.base import BaseAdapter
from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class AutoGenAdapter(BaseAdapter):
    """
    Adapter for Microsoft AutoGen framework integration.
    
    This adapter provides observability wrappers for AutoGen agents,
    tracking conversations, agent interactions, and code execution.
    
    AutoGen supports multi-agent conversations with features like:
    - AssistantAgent: LLM-powered agents
    - UserProxyAgent: Human-in-the-loop or automated user proxies
    - GroupChat: Multi-agent group conversations
    - Code execution: Sandboxed code execution capabilities
    
    Attributes:
        config: Agentic configuration instance
        default_model: Default LLM model for agents
    """

    framework_name = "autogen"

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        default_model: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the AutoGen adapter.
        
        Args:
            config: Configuration instance
            default_model: Default model for agents (uses config default if None)
            **kwargs: Additional arguments passed to BaseAdapter
        """
        super().__init__(config, name="AutoGen", **kwargs)
        self.default_model = default_model or self.config.ollama.default_model
        self._autogen_available = self._check_autogen()

    def _check_autogen(self) -> bool:
        """Check if AutoGen is available."""
        try:
            import autogen
            return True
        except ImportError:
            logger.warning(
                "AutoGen is not installed. Install with: pip install pyautogen"
            )
            return False

    def _get_llm_config(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Get LLM configuration for AutoGen agents.
        
        Args:
            model: Model name (uses default if None)
            temperature: Sampling temperature
            **kwargs: Additional LLM parameters
            
        Returns:
            LLM configuration dictionary
        """
        model_name = model or self.default_model
        
        # Configure for Ollama
        return {
            "config_list": [
                {
                    "model": model_name,
                    "base_url": f"{self.config.ollama.host}/v1",
                    "api_key": "ollama",  # Ollama doesn't need a real key
                }
            ],
            "temperature": temperature,
            "timeout": self.config.ollama.timeout,
            **kwargs,
        }

    def run(
        self,
        initiator: Any,
        recipient: Any,
        message: str,
        **kwargs,
    ) -> Any:
        """
        Run a conversation between two agents.
        
        This is a convenience method that calls run_conversation.
        
        Args:
            initiator: The agent initiating the conversation
            recipient: The agent receiving the message
            message: Initial message to start the conversation
            **kwargs: Additional arguments passed to run_conversation
            
        Returns:
            Conversation result
        """
        return self.run_conversation(initiator, recipient, message, **kwargs)

    def run_conversation(
        self,
        initiator: Any,
        recipient: Any,
        message: str,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        max_turns: int = 10,
        clear_history: bool = True,
    ) -> Any:
        """
        Run a conversation between two agents with full observability.
        
        Args:
            initiator: The agent initiating the conversation
            recipient: The agent receiving the message
            message: Initial message to start the conversation
            experiment_name: MLFlow experiment name (optional)
            run_name: Name for this run
            tags: Additional tags for the run
            max_turns: Maximum conversation turns
            clear_history: Clear conversation history before starting
            
        Returns:
            Conversation result
            
        Example:
            >>> result = adapter.run_conversation(
            ...     user_proxy,
            ...     assistant,
            ...     message="Write a hello world program",
            ...     experiment_name="code-gen"
            ... )
        """
        if not self._autogen_available:
            raise ImportError("AutoGen is not installed. Install with: pip install pyautogen")

        # Set experiment if specified
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        # Build run name
        actual_run_name = run_name or f"autogen-{time.strftime('%Y%m%d-%H%M%S')}"

        # Build parameters
        params = {
            "framework": "autogen",
            "model": self.default_model,
            "max_turns": max_turns,
            "initiator": getattr(initiator, "name", "initiator"),
            "recipient": getattr(recipient, "name", "recipient"),
        }

        # Build tags
        all_tags = {"framework": "autogen"}
        if tags:
            all_tags.update(tags)

        with self.track_run(
            actual_run_name,
            tags=all_tags,
            params=params,
            agent_name=getattr(initiator, "name", "autogen_agent"),
            model=self.default_model,
        ):
            start_time = time.time()

            try:
                logger.info(f"Starting AutoGen conversation: {actual_run_name}")

                # Get RAG context if available
                rag_context = ""
                if self._knowledge_base:
                    results = self.get_rag_context(message)
                    if results:
                        rag_context = "\n\nRelevant context:\n" + "\n".join(
                            f"- {r['content'][:500]}" for r in results[:3]
                        )
                        message = message + rag_context

                # Run the conversation
                if clear_history:
                    initiator.reset()
                    recipient.reset()
                
                result = initiator.initiate_chat(
                    recipient,
                    message=message,
                    max_turns=max_turns,
                    clear_history=clear_history,
                )

                duration = time.time() - start_time

                # Log success metrics
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)
                
                # Try to extract conversation details
                try:
                    chat_history = getattr(result, "chat_history", [])
                    self.tracker.log_metric("num_turns", len(chat_history))
                except Exception:
                    pass

                logger.info(f"AutoGen conversation completed in {duration:.2f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                self.log_error(e, "autogen_conversation")
                logger.error(f"AutoGen conversation failed after {duration:.2f}s: {e}")
                raise

    def create_assistant_agent(
        self,
        name: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        human_input_mode: str = "NEVER",
        code_execution_config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """
        Create an AutoGen AssistantAgent.
        
        Args:
            name: Agent name
            system_message: System message/prompt for the agent
            model: LLM model to use (uses default if None)
            human_input_mode: How to handle human input ("NEVER", "ALWAYS", "TERMINATE")
            code_execution_config: Code execution configuration
            **kwargs: Additional AssistantAgent parameters
            
        Returns:
            Configured AssistantAgent
            
        Example:
            >>> assistant = adapter.create_assistant_agent(
            ...     name="code_assistant",
            ...     system_message="You are an expert Python programmer.",
            ...     model="codellama"
            ... )
        """
        if not self._autogen_available:
            raise ImportError("AutoGen is not installed. Install with: pip install pyautogen")

        from autogen import AssistantAgent

        llm_config = self._get_llm_config(model)
        
        default_system_message = (
            "You are a helpful AI assistant. "
            "Solve tasks using your coding and language skills. "
            "Reply TERMINATE when the task is complete."
        )

        return AssistantAgent(
            name=name,
            system_message=system_message or default_system_message,
            llm_config=llm_config,
            human_input_mode=human_input_mode,
            code_execution_config=code_execution_config,
            **kwargs,
        )

    def create_user_proxy_agent(
        self,
        name: str = "user_proxy",
        human_input_mode: str = "NEVER",
        max_consecutive_auto_reply: int = 10,
        is_termination_msg: Optional[Callable] = None,
        code_execution_config: Optional[Union[Dict, bool]] = None,
        **kwargs,
    ) -> Any:
        """
        Create an AutoGen UserProxyAgent.
        
        Args:
            name: Agent name
            human_input_mode: How to handle human input ("NEVER", "ALWAYS", "TERMINATE")
            max_consecutive_auto_reply: Max auto replies before stopping
            is_termination_msg: Function to check for termination
            code_execution_config: Code execution configuration (False to disable)
            **kwargs: Additional UserProxyAgent parameters
            
        Returns:
            Configured UserProxyAgent
            
        Example:
            >>> user_proxy = adapter.create_user_proxy_agent(
            ...     name="user",
            ...     human_input_mode="NEVER",
            ...     code_execution_config={"work_dir": "coding"}
            ... )
        """
        if not self._autogen_available:
            raise ImportError("AutoGen is not installed. Install with: pip install pyautogen")

        from autogen import UserProxyAgent

        # Default termination check
        if is_termination_msg is None:
            is_termination_msg = lambda x: x.get("content", "").rstrip().endswith("TERMINATE")

        # Default code execution config
        if code_execution_config is None:
            code_execution_config = {
                "work_dir": "coding",
                "use_docker": False,
            }

        return UserProxyAgent(
            name=name,
            human_input_mode=human_input_mode,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            is_termination_msg=is_termination_msg,
            code_execution_config=code_execution_config,
            **kwargs,
        )

    def create_group_chat(
        self,
        agents: List[Any],
        messages: Optional[List[Dict]] = None,
        max_round: int = 10,
        admin_name: str = "Admin",
        speaker_selection_method: str = "auto",
        **kwargs,
    ) -> Any:
        """
        Create an AutoGen GroupChat.
        
        Args:
            agents: List of agents participating in the chat
            messages: Initial messages (optional)
            max_round: Maximum rounds of conversation
            admin_name: Name of the admin
            speaker_selection_method: How to select the next speaker
            **kwargs: Additional GroupChat parameters
            
        Returns:
            Configured GroupChat
        """
        if not self._autogen_available:
            raise ImportError("AutoGen is not installed. Install with: pip install pyautogen")

        from autogen import GroupChat

        return GroupChat(
            agents=agents,
            messages=messages or [],
            max_round=max_round,
            admin_name=admin_name,
            speaker_selection_method=speaker_selection_method,
            **kwargs,
        )

    def create_group_chat_manager(
        self,
        group_chat: Any,
        model: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Create a GroupChatManager for managing group conversations.
        
        Args:
            group_chat: The GroupChat instance
            model: LLM model to use (uses default if None)
            **kwargs: Additional GroupChatManager parameters
            
        Returns:
            Configured GroupChatManager
        """
        if not self._autogen_available:
            raise ImportError("AutoGen is not installed. Install with: pip install pyautogen")

        from autogen import GroupChatManager

        llm_config = self._get_llm_config(model)

        return GroupChatManager(
            groupchat=group_chat,
            llm_config=llm_config,
            **kwargs,
        )

    def run_group_chat(
        self,
        initiator: Any,
        manager: Any,
        message: str,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Run a group chat with full observability.
        
        Args:
            initiator: The agent initiating the conversation
            manager: The GroupChatManager
            message: Initial message
            experiment_name: MLFlow experiment name
            run_name: Name for this run
            tags: Additional tags
            
        Returns:
            Group chat result
        """
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        actual_run_name = run_name or f"autogen-group-{time.strftime('%Y%m%d-%H%M%S')}"

        params = {
            "framework": "autogen",
            "mode": "group_chat",
            "model": self.default_model,
        }

        all_tags = {"framework": "autogen", "mode": "group_chat"}
        if tags:
            all_tags.update(tags)

        with self.track_run(
            actual_run_name,
            tags=all_tags,
            params=params,
            agent_name="autogen_group",
            model=self.default_model,
        ):
            start_time = time.time()

            try:
                logger.info(f"Starting AutoGen group chat: {actual_run_name}")

                result = initiator.initiate_chat(
                    manager,
                    message=message,
                )

                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)

                logger.info(f"AutoGen group chat completed in {duration:.2f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                self.log_error(e, "autogen_group_chat")
                raise

    async def deploy_autogen_team(
        self,
        team_id: str,
        name: str,
        agents_config: List[Dict[str, Any]],
        namespace: Optional[str] = None,
        model_endpoint: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Deploy an AutoGen agent team to Kubernetes.
        
        Args:
            team_id: Unique identifier for the team
            name: Deployment name
            agents_config: Configuration for each agent
            namespace: Kubernetes namespace
            model_endpoint: LLM endpoint URL
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
            agent_id=team_id,
            name=name,
            namespace=namespace or self.config.kubernetes.default_deploy_namespace,
            replicas=kwargs.get("replicas", 1),
            framework="autogen",
            model_endpoint=model_endpoint,
            tools=[],
            env_vars={"AGENTS_CONFIG": str(agents_config)},
            resources=resources,
        )

        deployment = await deployer.deploy_agent(config)

        if deployment:
            logger.info(f"Deployed AutoGen team {name} to Kubernetes")
        else:
            logger.error(f"Failed to deploy AutoGen team {name}")

        return deployment
