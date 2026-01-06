"""
ReAct (Reasoning and Acting) Pattern implementation.

This module provides the ReAct pattern that interleaves:
- Reasoning: Thinking about what to do
- Acting: Executing actions/tools
- Observing: Processing results

Example:
    >>> from agentic_assistants.patterns import ReActPattern
    >>> 
    >>> react = ReActPattern(tools=[search_tool, calc_tool])
    >>> result = react.execute("Find the population of France")
"""

import re
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.telemetry import trace_function
from agentic_assistants.patterns.base import AgenticPattern, PatternConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ReActConfig(PatternConfig):
    """
    Configuration for ReAct pattern.
    
    Attributes:
        max_iterations: Maximum reasoning-acting cycles
        stop_phrases: Phrases that indicate completion
        thought_prefix: Prefix for thought/reasoning
        action_prefix: Prefix for actions
        observation_prefix: Prefix for observations
        final_answer_prefix: Prefix for final answer
    """
    
    name: str = "react"
    description: str = "Reasoning and Acting pattern"
    max_iterations: int = 10
    stop_phrases: list = None
    thought_prefix: str = "Thought:"
    action_prefix: str = "Action:"
    action_input_prefix: str = "Action Input:"
    observation_prefix: str = "Observation:"
    final_answer_prefix: str = "Final Answer:"
    
    def __post_init__(self):
        if self.stop_phrases is None:
            self.stop_phrases = [self.final_answer_prefix]


class ReActPattern(AgenticPattern):
    """
    ReAct (Reasoning and Acting) pattern.
    
    This pattern implements a reasoning loop where the agent:
    1. Thinks about what to do next
    2. Takes an action (calls a tool)
    3. Observes the result
    4. Repeats until reaching a final answer
    
    The pattern uses a structured prompt format:
    ```
    Thought: I need to find...
    Action: search
    Action Input: query here
    Observation: [tool result]
    ...
    Final Answer: The answer is...
    ```
    
    Attributes:
        tools: Dictionary of available tools
        llm_fn: Function to call LLM
        react_config: ReAct configuration
    
    Example:
        >>> tools = {
        ...     "search": lambda q: web_search(q),
        ...     "calculate": lambda expr: eval(expr),
        ... }
        >>> 
        >>> react = ReActPattern(tools=tools)
        >>> result = react.execute("What is 2+2?")
    """
    
    SYSTEM_PROMPT_TEMPLATE = """You are a helpful assistant that can reason and use tools to answer questions.

Available tools:
{tools_description}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {question}
"""
    
    def __init__(
        self,
        tools: Optional[dict[str, Callable]] = None,
        llm_fn: Optional[Callable] = None,
        config: Optional[AgenticConfig] = None,
        react_config: Optional[ReActConfig] = None,
    ):
        """
        Initialize the ReAct pattern.
        
        Args:
            tools: Dictionary mapping tool names to callables
            llm_fn: Function to call LLM
            config: Framework configuration
            react_config: ReAct configuration
        """
        react_config = react_config or ReActConfig()
        super().__init__(config=config, pattern_config=react_config)
        
        self.react_config = react_config
        self.tools = tools or {}
        self._llm_fn = llm_fn
    
    @property
    def llm_fn(self) -> Callable:
        """Get or create LLM function."""
        if self._llm_fn is None:
            from agentic_assistants.core.ollama import OllamaManager
            ollama = OllamaManager(self.config)
            self._llm_fn = lambda messages: ollama.chat(messages)["message"]["content"]
        return self._llm_fn
    
    def register_tool(self, name: str, func: Callable, description: str = "") -> None:
        """
        Register a tool for the agent to use.
        
        Args:
            name: Tool name
            func: Tool function
            description: Tool description
        """
        self.tools[name] = {
            "func": func,
            "description": description or f"Tool: {name}",
        }
    
    def _get_tools_description(self) -> str:
        """Get formatted tools description."""
        parts = []
        for name, tool in self.tools.items():
            if isinstance(tool, dict):
                desc = tool.get("description", f"Tool: {name}")
            else:
                desc = f"Tool: {name}"
            parts.append(f"- {name}: {desc}")
        return "\n".join(parts) if parts else "No tools available."
    
    def _get_tool_names(self) -> str:
        """Get comma-separated tool names."""
        return ", ".join(self.tools.keys())
    
    def _build_prompt(self, question: str) -> str:
        """Build the initial ReAct prompt."""
        return self.SYSTEM_PROMPT_TEMPLATE.format(
            tools_description=self._get_tools_description(),
            tool_names=self._get_tool_names(),
            question=question,
        )
    
    @trace_function(attributes={"pattern": "react", "step": "think"})
    def _think(self, messages: list[dict]) -> str:
        """Generate next thought/action from LLM."""
        start_time = time.time()
        response = self.llm_fn(messages)
        duration_ms = (time.time() - start_time) * 1000
        
        self.record_step(
            action="think",
            input_data={"message_count": len(messages)},
            output_data={"response_length": len(response)},
            duration_ms=duration_ms,
        )
        
        return response
    
    def _parse_action(self, response: str) -> tuple[Optional[str], Optional[str]]:
        """
        Parse action and action input from response.
        
        Returns:
            Tuple of (action_name, action_input) or (None, None)
        """
        # Look for Action: and Action Input:
        action_match = re.search(
            rf"{self.react_config.action_prefix}\s*(.+?)(?:\n|$)",
            response,
            re.IGNORECASE
        )
        input_match = re.search(
            rf"{self.react_config.action_input_prefix}\s*(.+?)(?:\n|$)",
            response,
            re.IGNORECASE | re.DOTALL
        )
        
        if action_match:
            action = action_match.group(1).strip()
            action_input = input_match.group(1).strip() if input_match else ""
            return action, action_input
        
        return None, None
    
    def _parse_final_answer(self, response: str) -> Optional[str]:
        """Parse final answer from response."""
        match = re.search(
            rf"{self.react_config.final_answer_prefix}\s*(.+)",
            response,
            re.IGNORECASE | re.DOTALL
        )
        if match:
            return match.group(1).strip()
        return None
    
    @trace_function(attributes={"pattern": "react", "step": "act"})
    def _act(self, action: str, action_input: str) -> str:
        """
        Execute an action using a tool.
        
        Args:
            action: Tool name
            action_input: Input to the tool
        
        Returns:
            Tool result
        """
        start_time = time.time()
        
        if action not in self.tools:
            result = f"Error: Unknown tool '{action}'. Available: {self._get_tool_names()}"
        else:
            try:
                tool = self.tools[action]
                func = tool["func"] if isinstance(tool, dict) else tool
                result = str(func(action_input))
            except Exception as e:
                result = f"Error executing tool: {e}"
        
        duration_ms = (time.time() - start_time) * 1000
        
        self.record_step(
            action="act",
            input_data={"tool": action, "input": action_input},
            output_data={"result_length": len(result)},
            duration_ms=duration_ms,
        )
        
        return result
    
    def _execute(self, input_data: Any) -> Any:
        """Execute the ReAct pattern."""
        # Handle input
        if isinstance(input_data, str):
            question = input_data
        elif isinstance(input_data, dict):
            question = input_data.get("question", input_data.get("query", ""))
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}")
        
        # Build initial prompt
        prompt = self._build_prompt(question)
        messages = [{"role": "user", "content": prompt}]
        
        # ReAct loop
        full_response = ""
        for iteration in range(self.react_config.max_iterations):
            # Get LLM response
            response = self._think(messages)
            full_response += response
            
            # Check for final answer
            final_answer = self._parse_final_answer(response)
            if final_answer:
                logger.debug(f"Found final answer at iteration {iteration + 1}")
                return final_answer
            
            # Parse action
            action, action_input = self._parse_action(response)
            if action is None:
                # No action found, might be confused - ask to continue
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": "Please continue with a Thought, Action, or Final Answer."
                })
                continue
            
            # Execute action
            observation = self._act(action, action_input)
            
            # Add to messages
            messages.append({"role": "assistant", "content": response})
            messages.append({
                "role": "user",
                "content": f"{self.react_config.observation_prefix} {observation}"
            })
        
        # Max iterations reached
        logger.warning(f"Max iterations ({self.react_config.max_iterations}) reached")
        return f"Unable to find answer after {self.react_config.max_iterations} iterations. Last response: {full_response[-500:]}"
    
    def run(
        self,
        question: str,
        experiment_name: Optional[str] = None,
    ):
        """
        Convenience method to run ReAct.
        
        Args:
            question: Question to answer
            experiment_name: MLFlow experiment name
        
        Returns:
            PatternResult with answer
        """
        return self.execute(
            input_data=question,
            experiment_name=experiment_name,
            run_name=f"react-{question[:20]}",
        )

