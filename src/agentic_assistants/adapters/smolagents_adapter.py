"""
HuggingFace smolagents framework adapter with integrated observability.

This adapter wraps the smolagents library to provide:
- MLFlow experiment tracking for agent runs
- OpenTelemetry tracing for tool calls and agent steps
- Standardized metrics and logging

Example:
    >>> from agentic_assistants.adapters import SmolAgentsAdapter
    >>> 
    >>> adapter = SmolAgentsAdapter()
    >>> 
    >>> # Create a code agent with tools
    >>> agent = adapter.create_code_agent(
    ...     tools=[calculator_tool],
    ...     model="HfApiModel"
    ... )
    >>> 
    >>> # Run with tracking
    >>> result = adapter.run_agent(
    ...     agent,
    ...     "What is 25 * 4 + 10?",
    ...     experiment_name="math-agent"
    ... )
"""

import time
from typing import Any, Callable, Optional, Union

from agentic_assistants.adapters.base import BaseAdapter
from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class SmolAgentsAdapter(BaseAdapter):
    """
    Adapter for HuggingFace smolagents framework integration.
    
    This adapter provides observability wrappers for smolagents,
    tracking agent execution, tool calls, and model interactions.
    
    Attributes:
        config: Agentic configuration instance
        default_model_type: Default model type for agents
    """

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        model_type: str = "HfApiModel",
    ):
        """
        Initialize the smolagents adapter.
        
        Args:
            config: Configuration instance
            model_type: Default model type ('HfApiModel', 'TransformersModel', 'LiteLLMModel')
        """
        super().__init__(config, name="SmolAgents")
        self.default_model_type = model_type
        self._tools: dict[str, Any] = {}
        self._agents: dict[str, Any] = {}

    def run(self, agent: Any, task: str, **kwargs) -> Any:
        """
        Run a smolagents agent with tracking.
        
        This is a convenience method that calls run_agent.
        
        Args:
            agent: The smolagents agent
            task: Task description for the agent
            **kwargs: Additional arguments passed to run_agent
        
        Returns:
            Agent execution result
        """
        return self.run_agent(agent, task, **kwargs)

    def create_tool(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Any:
        """
        Create a smolagents tool from a function.
        
        Args:
            func: The function to wrap as a tool
            name: Tool name (uses function name if None)
            description: Tool description (uses docstring if None)
        
        Returns:
            smolagents tool
        
        Example:
            >>> @adapter.create_tool
            ... def calculator(expression: str) -> float:
            ...     '''Evaluate a mathematical expression.'''
            ...     return eval(expression)
        """
        try:
            from smolagents import tool
        except ImportError as e:
            raise ImportError(
                "smolagents is required. Install with: pip install smolagents"
            ) from e

        # If used as decorator without arguments
        if callable(func) and name is None and description is None:
            wrapped = tool(func)
            tool_name = func.__name__
            self._tools[tool_name] = wrapped
            logger.debug(f"Created tool: {tool_name}")
            return wrapped
        
        # If used with arguments
        def decorator(f):
            wrapped = tool(f)
            tool_name = name or f.__name__
            self._tools[tool_name] = wrapped
            logger.debug(f"Created tool: {tool_name}")
            return wrapped
        
        return decorator

    def wrap_tool_with_tracking(self, tool_func: Callable, tool_name: str) -> Callable:
        """
        Wrap a tool function with observability.
        
        Args:
            tool_func: The tool function to wrap
            tool_name: Name of the tool
        
        Returns:
            Wrapped function with telemetry
        """
        def wrapped(*args, **kwargs):
            with self.telemetry.span(
                f"smolagents.tool.{tool_name}",
                attributes={"tool.name": tool_name},
            ) as span_logger:
                start_time = time.time()
                
                try:
                    span_logger.log_event("tool_called", {
                        "tool": tool_name,
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200],
                    })
                    
                    result = tool_func(*args, **kwargs)
                    
                    duration = time.time() - start_time
                    
                    span_logger.log_event("tool_completed", {
                        "tool": tool_name,
                        "result": str(result)[:200],
                        "duration_seconds": duration,
                    })
                    
                    self.log_tool_call(
                        tool_name=tool_name,
                        input_args={"args": args, "kwargs": kwargs},
                        output=result,
                        duration_seconds=duration,
                        success=True,
                    )
                    
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    span_logger.log_error(e)
                    
                    self.log_tool_call(
                        tool_name=tool_name,
                        input_args={"args": args, "kwargs": kwargs},
                        output=None,
                        duration_seconds=duration,
                        success=False,
                        error=str(e),
                    )
                    raise
        
        wrapped.__name__ = tool_func.__name__
        wrapped.__doc__ = tool_func.__doc__
        return wrapped

    def create_model(
        self,
        model_type: Optional[str] = None,
        model_id: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Create a smolagents model instance.
        
        Args:
            model_type: Model type ('HfApiModel', 'TransformersModel', 'LiteLLMModel')
            model_id: Model identifier for the chosen type
            **kwargs: Additional model arguments
        
        Returns:
            smolagents model instance
        
        Example:
            >>> model = adapter.create_model(
            ...     model_type="HfApiModel",
            ...     model_id="meta-llama/Llama-3.2-3B-Instruct"
            ... )
        """
        try:
            from smolagents import HfApiModel, TransformersModel, LiteLLMModel
        except ImportError as e:
            raise ImportError(
                "smolagents is required. Install with: pip install smolagents"
            ) from e

        model_classes = {
            "HfApiModel": HfApiModel,
            "TransformersModel": TransformersModel,
            "LiteLLMModel": LiteLLMModel,
        }

        model_type = model_type or self.default_model_type
        
        if model_type not in model_classes:
            raise ValueError(
                f"Unknown model type: {model_type}. "
                f"Available: {list(model_classes.keys())}"
            )

        with self.telemetry.span(
            "smolagents.create_model",
            attributes={
                "model_type": model_type,
                "model_id": model_id or "default",
            },
        ) as span_logger:
            try:
                cls = model_classes[model_type]
                if model_id:
                    model = cls(model_id=model_id, **kwargs)
                else:
                    model = cls(**kwargs)
                
                span_logger.log_event("model_created", {
                    "type": model_type,
                    "model_id": model_id,
                })
                
                logger.info(f"Created {model_type} model: {model_id or 'default'}")
                return model
                
            except Exception as e:
                span_logger.log_error(e)
                raise

    def create_code_agent(
        self,
        tools: list,
        model: Optional[Any] = None,
        model_type: Optional[str] = None,
        model_id: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Create a smolagents CodeAgent.
        
        Args:
            tools: List of tools for the agent
            model: Pre-created model instance
            model_type: Model type if creating new model
            model_id: Model ID if creating new model
            **kwargs: Additional agent arguments
        
        Returns:
            CodeAgent instance
        
        Example:
            >>> agent = adapter.create_code_agent(
            ...     tools=[calculator, web_search],
            ...     model_type="HfApiModel"
            ... )
        """
        try:
            from smolagents import CodeAgent
        except ImportError as e:
            raise ImportError(
                "smolagents is required. Install with: pip install smolagents"
            ) from e

        with self.telemetry.span(
            "smolagents.create_code_agent",
            attributes={
                "num_tools": len(tools),
                "model_type": model_type or "provided",
            },
        ) as span_logger:
            try:
                # Create model if not provided
                if model is None:
                    model = self.create_model(model_type, model_id)
                
                agent = CodeAgent(tools=tools, model=model, **kwargs)
                
                agent_id = f"code_agent_{len(self._agents)}"
                self._agents[agent_id] = agent
                
                span_logger.log_event("agent_created", {
                    "agent_id": agent_id,
                    "agent_type": "CodeAgent",
                    "num_tools": len(tools),
                })
                
                logger.info(f"Created CodeAgent with {len(tools)} tools")
                return agent
                
            except Exception as e:
                span_logger.log_error(e)
                raise

    def create_tool_calling_agent(
        self,
        tools: list,
        model: Optional[Any] = None,
        model_type: Optional[str] = None,
        model_id: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Create a smolagents ToolCallingAgent.
        
        Args:
            tools: List of tools for the agent
            model: Pre-created model instance
            model_type: Model type if creating new model
            model_id: Model ID if creating new model
            **kwargs: Additional agent arguments
        
        Returns:
            ToolCallingAgent instance
        """
        try:
            from smolagents import ToolCallingAgent
        except ImportError as e:
            raise ImportError(
                "smolagents is required. Install with: pip install smolagents"
            ) from e

        with self.telemetry.span(
            "smolagents.create_tool_calling_agent",
            attributes={
                "num_tools": len(tools),
                "model_type": model_type or "provided",
            },
        ) as span_logger:
            try:
                if model is None:
                    model = self.create_model(model_type, model_id)
                
                agent = ToolCallingAgent(tools=tools, model=model, **kwargs)
                
                agent_id = f"tool_calling_agent_{len(self._agents)}"
                self._agents[agent_id] = agent
                
                span_logger.log_event("agent_created", {
                    "agent_id": agent_id,
                    "agent_type": "ToolCallingAgent",
                    "num_tools": len(tools),
                })
                
                logger.info(f"Created ToolCallingAgent with {len(tools)} tools")
                return agent
                
            except Exception as e:
                span_logger.log_error(e)
                raise

    def run_agent(
        self,
        agent: Any,
        task: str,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
        **kwargs,
    ) -> Any:
        """
        Run a smolagents agent with full observability.
        
        Args:
            agent: The smolagents agent to run
            task: Task description for the agent
            experiment_name: MLFlow experiment name (optional)
            run_name: Name for this run
            tags: Additional tags for the run
            **kwargs: Additional arguments for agent.run()
        
        Returns:
            Agent execution result
        
        Example:
            >>> result = adapter.run_agent(
            ...     agent,
            ...     "Calculate the sum of 1 to 100",
            ...     experiment_name="math-experiments",
            ...     run_name="sum-calculation"
            ... )
        """
        # Set experiment if specified
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        # Determine agent type
        agent_type = type(agent).__name__
        
        # Build run name
        actual_run_name = run_name or f"agent-{agent_type}-{time.strftime('%Y%m%d-%H%M%S')}"

        # Build parameters
        params = {
            "framework": "smolagents",
            "agent_type": agent_type,
            "task_length": len(task),
        }

        # Build tags
        all_tags = {"framework": "smolagents", "agent_type": agent_type}
        if tags:
            all_tags.update(tags)

        with self.track_run(actual_run_name, tags=all_tags, params=params) as (mlflow_run, span_logger):
            start_time = time.time()

            try:
                logger.info(f"Running {agent_type}: {actual_run_name}")
                span_logger.log_input(task)
                
                # Log task
                self.tracker.log_text(task, "input/task.txt")

                # Run the agent
                result = agent.run(task, **kwargs)

                duration = time.time() - start_time

                # Log success metrics
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 1)

                # Log output
                span_logger.log_output(result)
                
                # Log result
                if isinstance(result, str):
                    self.tracker.log_text(result, "output/result.txt")
                else:
                    self.tracker.log_dict(
                        {"result": str(result)[:2000]},
                        "output/result.json",
                    )

                logger.info(f"Agent completed in {duration:.2f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                span_logger.log_error(e)
                logger.error(f"Agent failed after {duration:.2f}s: {e}")
                raise

    def stream_agent(
        self,
        agent: Any,
        task: str,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Stream agent execution with tracking.
        
        Args:
            agent: The smolagents agent to run
            task: Task description
            experiment_name: MLFlow experiment name
            run_name: Name for this run
            **kwargs: Additional arguments
        
        Yields:
            Agent execution steps
        """
        if experiment_name:
            self.tracker.experiment_name = experiment_name

        agent_type = type(agent).__name__
        actual_run_name = run_name or f"stream-{agent_type}-{time.strftime('%Y%m%d-%H%M%S')}"

        params = {
            "framework": "smolagents",
            "agent_type": agent_type,
            "mode": "streaming",
        }

        with self.track_run(actual_run_name, params=params) as (mlflow_run, span_logger):
            start_time = time.time()
            step_count = 0

            try:
                for step in agent.run(task, stream=True, **kwargs):
                    step_count += 1
                    
                    with self.track_step(f"step-{step_count}", step_number=step_count) as step_span:
                        step_span.log_event("step_output", {"step": step_count})
                        yield step
                    
                    self.tracker.log_metric("steps", step_count)

                duration = time.time() - start_time
                self.tracker.log_metrics({
                    "duration_seconds": duration,
                    "total_steps": step_count,
                    "success": 1,
                })

            except Exception as e:
                duration = time.time() - start_time
                self.tracker.log_metric("duration_seconds", duration)
                self.tracker.log_metric("success", 0)
                self.tracker.set_tag("error", str(e))
                span_logger.log_error(e)
                raise

    def get_default_tools(self) -> list:
        """
        Get a list of commonly useful default tools.
        
        Returns:
            List of default tool instances
        """
        try:
            from smolagents import DuckDuckGoSearchTool, VisitWebpageTool
        except ImportError:
            logger.warning("Could not import default tools from smolagents")
            return []

        tools = []
        
        try:
            tools.append(DuckDuckGoSearchTool())
        except Exception as e:
            logger.debug(f"Could not create DuckDuckGoSearchTool: {e}")
        
        try:
            tools.append(VisitWebpageTool())
        except Exception as e:
            logger.debug(f"Could not create VisitWebpageTool: {e}")
        
        return tools

