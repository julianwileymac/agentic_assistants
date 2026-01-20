"""
CrewAI framework adapter with integrated observability.

This adapter wraps CrewAI crews and agents to provide:
- MLFlow experiment tracking for crew runs
- OpenTelemetry tracing for agent interactions
- Standardized metrics and logging
- Kubernetes deployment support

Example:
    >>> from crewai import Agent, Task, Crew
    >>> from agentic_assistants.adapters import CrewAIAdapter
    >>> 
    >>> adapter = CrewAIAdapter()
    >>> 
    >>> # Create your crew
    >>> researcher = Agent(name="Researcher", ...)
    >>> writer = Agent(name="Writer", ...)
    >>> crew = Crew(agents=[researcher, writer], tasks=[...])
    >>> 
    >>> # Run with tracking
    >>> result = adapter.run_crew(
    ...     crew,
    ...     inputs={"topic": "AI agents"},
    ...     experiment_name="research-experiment"
    ... )
    >>> 
    >>> # Deploy to Kubernetes
    >>> deployment = await adapter.deploy_crew(
    ...     crew_id="my-crew",
    ...     name="research-crew",
    ...     model_endpoint="http://ollama.model-serving:11434"
    ... )
"""

import time
from typing import Any, Optional

from agentic_assistants.adapters.base import BaseAdapter
from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class CrewAIAdapter(BaseAdapter):
    """
    Adapter for CrewAI framework integration.
    
    This adapter provides observability wrappers for CrewAI crews,
    tracking agent interactions, task execution, and crew performance.
    
    Attributes:
        config: Agentic configuration instance
        default_model: Default LLM model for agents
    """

    framework_name = "crewai"

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        default_model: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the CrewAI adapter.
        
        Args:
            config: Configuration instance
            default_model: Default model for agents (uses config default if None)
            **kwargs: Additional arguments passed to BaseAdapter
        """
        super().__init__(config, name="CrewAI", **kwargs)
        self.default_model = default_model or self.config.ollama.default_model

    def run(self, crew: Any, inputs: Optional[dict] = None, **kwargs) -> Any:
        """
        Run a CrewAI crew with tracking.
        
        This is a convenience method that calls run_crew.
        
        Args:
            crew: The CrewAI Crew instance
            inputs: Input dictionary for the crew
            **kwargs: Additional arguments passed to run_crew
        
        Returns:
            Crew execution result
        """
        return self.run_crew(crew, inputs, **kwargs)

    def run_crew(
        self,
        crew: Any,
        inputs: Optional[dict] = None,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> Any:
        """
        Run a CrewAI crew with full observability.
        
        Args:
            crew: The CrewAI Crew instance to run
            inputs: Input dictionary for the crew
            experiment_name: MLFlow experiment name (optional)
            run_name: Name for this run
            tags: Additional tags for the run
        
        Returns:
            The crew execution result
        
        Example:
            >>> crew = Crew(agents=[...], tasks=[...])
            >>> result = adapter.run_crew(
            ...     crew,
            ...     inputs={"topic": "machine learning"},
            ...     experiment_name="research-v2",
            ...     run_name="ml-research-001"
            ... )
        """
        # Set experiment if specified
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        # Build run name
        actual_run_name = run_name or f"crew-{time.strftime('%Y%m%d-%H%M%S')}"

        # Build parameters
        params = {
            "framework": "crewai",
            "model": self.default_model,
            "input_keys": list(inputs.keys()) if inputs else [],
        }

        # Add crew info if available
        try:
            params["agent_count"] = len(crew.agents)
            params["task_count"] = len(crew.tasks)
            params["agents"] = [a.role for a in crew.agents]
        except Exception:
            pass

        # Build tags
        all_tags = {"framework": "crewai"}
        if tags:
            all_tags.update(tags)

        with self.track_run(actual_run_name, tags=all_tags, params=params):
            start_time = time.time()

            try:
                logger.info(f"Starting CrewAI crew: {actual_run_name}")

                # Run the crew
                result = crew.kickoff(inputs=inputs)

                duration = time.time() - start_time

                # Log success metrics
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)

                # Log result if it's a string
                if isinstance(result, str):
                    self.tracker.log_text(result, "output/crew_result.txt")

                logger.info(f"Crew completed in {duration:.2f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                logger.error(f"Crew failed after {duration:.2f}s: {e}")
                raise

    def create_ollama_agent(
        self,
        role: str,
        goal: str,
        backstory: str,
        model: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Create a CrewAI agent configured for Ollama.
        
        This is a convenience method for creating agents that use
        Ollama as the LLM provider.
        
        Args:
            role: Agent's role description
            goal: Agent's goal
            backstory: Agent's backstory
            model: Ollama model to use (uses default if None)
            **kwargs: Additional Agent parameters
        
        Returns:
            Configured CrewAI Agent
        
        Example:
            >>> researcher = adapter.create_ollama_agent(
            ...     role="Research Analyst",
            ...     goal="Find accurate information on topics",
            ...     backstory="Expert researcher with years of experience",
            ...     model="llama3.2"
            ... )
        """
        try:
            from crewai import Agent
            from langchain_ollama import ChatOllama
        except ImportError as e:
            raise ImportError(
                "CrewAI and langchain-ollama are required. "
                "Install with: pip install crewai langchain-ollama"
            ) from e

        model_name = model or self.default_model

        # Create Ollama LLM
        llm = ChatOllama(
            model=model_name,
            base_url=self.config.ollama.host,
        )

        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            verbose=True,
            **kwargs,
        )

    def create_task(
        self,
        description: str,
        agent: Any,
        expected_output: str,
        **kwargs,
    ) -> Any:
        """
        Create a CrewAI task.
        
        Args:
            description: Task description
            agent: Agent to assign the task to
            expected_output: Description of expected output
            **kwargs: Additional Task parameters
        
        Returns:
            Configured CrewAI Task
        """
        try:
            from crewai import Task
        except ImportError as e:
            raise ImportError("CrewAI is required. Install with: pip install crewai") from e

        return Task(
            description=description,
            agent=agent,
            expected_output=expected_output,
            **kwargs,
        )

    def create_crew(
        self,
        agents: list,
        tasks: list,
        verbose: bool = True,
        **kwargs,
    ) -> Any:
        """
        Create a CrewAI crew.
        
        Args:
            agents: List of agents
            tasks: List of tasks
            verbose: Enable verbose output
            **kwargs: Additional Crew parameters
        
        Returns:
            Configured CrewAI Crew
        """
        try:
            from crewai import Crew
        except ImportError as e:
            raise ImportError("CrewAI is required. Install with: pip install crewai") from e

        return Crew(
            agents=agents,
            tasks=tasks,
            verbose=verbose,
            **kwargs,
        )

    async def deploy_crew(
        self,
        crew_id: str,
        name: str,
        namespace: Optional[str] = None,
        replicas: int = 1,
        model_endpoint: Optional[str] = None,
        tools: Optional[list[str]] = None,
        env_vars: Optional[dict[str, str]] = None,
        cpu_request: str = "100m",
        cpu_limit: str = "1000m",
        memory_request: str = "256Mi",
        memory_limit: str = "1Gi",
    ) -> Any:
        """
        Deploy a CrewAI crew to Kubernetes.
        
        This method creates a Kubernetes deployment for running the crew
        as a persistent service.
        
        Args:
            crew_id: Unique identifier for the crew
            name: Deployment name
            namespace: Kubernetes namespace (uses default if None)
            replicas: Number of replicas
            model_endpoint: LLM endpoint URL (e.g., Ollama service)
            tools: List of tools to include
            env_vars: Additional environment variables
            cpu_request: CPU request
            cpu_limit: CPU limit
            memory_request: Memory request
            memory_limit: Memory limit
        
        Returns:
            DeploymentInfo if successful
        
        Example:
            >>> deployment = await adapter.deploy_crew(
            ...     crew_id="research-crew-001",
            ...     name="research-crew",
            ...     model_endpoint="http://ollama.model-serving:11434",
            ...     replicas=2
            ... )
        """
        from agentic_assistants.kubernetes import (
            DeploymentManager,
            AgentDeploymentConfig,
            ResourceRequirements,
        )
        
        deployer = DeploymentManager(config=self.config)
        
        resources = ResourceRequirements(
            cpu_request=cpu_request,
            cpu_limit=cpu_limit,
            memory_request=memory_request,
            memory_limit=memory_limit,
        )
        
        config = AgentDeploymentConfig(
            agent_id=crew_id,
            name=name,
            namespace=namespace or self.config.kubernetes.default_deploy_namespace,
            replicas=replicas,
            framework="crewai",
            model_endpoint=model_endpoint,
            tools=tools or [],
            env_vars=env_vars or {},
            resources=resources,
        )
        
        deployment = await deployer.deploy_agent(config)
        
        if deployment:
            logger.info(f"Deployed crew {name} to Kubernetes")
        else:
            logger.error(f"Failed to deploy crew {name}")
        
        return deployment

    async def undeploy_crew(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Remove a crew deployment from Kubernetes.
        
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
            logger.info(f"Undeployed crew {name} from Kubernetes")
        else:
            logger.error(f"Failed to undeploy crew {name}")
        
        return success

    async def get_crew_deployment_status(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> dict:
        """
        Get the status of a crew deployment.
        
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