"""
Chain of Thought (CoT) Pattern implementation.

This module provides the Chain of Thought pattern for:
- Step-by-step reasoning
- Complex problem decomposition
- Transparent decision making

Example:
    >>> from agentic_assistants.patterns import ChainOfThoughtPattern
    >>> 
    >>> cot = ChainOfThoughtPattern()
    >>> result = cot.execute("Explain how to sort a list")
"""

import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.telemetry import trace_function
from agentic_assistants.patterns.base import AgenticPattern, PatternConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CoTConfig(PatternConfig):
    """
    Configuration for Chain of Thought pattern.
    
    Attributes:
        num_steps: Expected number of reasoning steps
        step_prefix: Prefix for each step
        conclusion_prefix: Prefix for conclusion
        show_reasoning: Include reasoning in output
        prompt_style: Style of CoT prompt ("standard", "structured", "few_shot")
    """
    
    name: str = "chain_of_thought"
    description: str = "Chain of Thought reasoning pattern"
    num_steps: int = 5
    step_prefix: str = "Step"
    conclusion_prefix: str = "Conclusion:"
    show_reasoning: bool = True
    prompt_style: str = "structured"  # standard, structured, few_shot


class ChainOfThoughtPattern(AgenticPattern):
    """
    Chain of Thought reasoning pattern.
    
    This pattern prompts the LLM to think step-by-step,
    breaking down complex problems into manageable reasoning steps.
    
    Supports multiple prompting styles:
    - Standard: Simple "Let's think step by step"
    - Structured: Numbered steps with explicit format
    - Few-shot: Examples of step-by-step reasoning
    
    Attributes:
        llm_fn: Function to call LLM
        cot_config: CoT configuration
    
    Example:
        >>> cot = ChainOfThoughtPattern(prompt_style="structured")
        >>> result = cot.execute("What is 15% of 80?")
        >>> print(result.output)  # Step-by-step solution
    """
    
    STANDARD_TEMPLATE = """Please solve the following problem by thinking step by step.

Problem: {question}

Let's think step by step:"""

    STRUCTURED_TEMPLATE = """Please solve the following problem using clear, numbered steps.

Problem: {question}

Provide your reasoning in the following format:
Step 1: [First step of reasoning]
Step 2: [Second step of reasoning]
...
Conclusion: [Final answer]

Begin your step-by-step analysis:"""

    FEW_SHOT_TEMPLATE = """I'll show you how to solve problems step by step.

Example Problem: What is 25% of 200?
Step 1: I need to find 25% of 200
Step 2: 25% means 25/100 = 0.25
Step 3: Multiply: 200 × 0.25 = 50
Conclusion: 25% of 200 is 50

Example Problem: If a train travels at 60 mph, how far does it go in 2.5 hours?
Step 1: I need to find distance using speed × time
Step 2: Speed = 60 mph
Step 3: Time = 2.5 hours
Step 4: Distance = 60 × 2.5 = 150 miles
Conclusion: The train travels 150 miles

Now solve this problem step by step:

Problem: {question}

Step-by-step solution:"""
    
    def __init__(
        self,
        llm_fn: Optional[Callable] = None,
        config: Optional[AgenticConfig] = None,
        cot_config: Optional[CoTConfig] = None,
        prompt_style: str = "structured",
    ):
        """
        Initialize Chain of Thought pattern.
        
        Args:
            llm_fn: Function to call LLM
            config: Framework configuration
            cot_config: CoT configuration
            prompt_style: Prompting style
        """
        cot_config = cot_config or CoTConfig(prompt_style=prompt_style)
        super().__init__(config=config, pattern_config=cot_config)
        
        self.cot_config = cot_config
        self._llm_fn = llm_fn
    
    @property
    def llm_fn(self) -> Callable:
        """Get or create LLM function."""
        if self._llm_fn is None:
            from agentic_assistants.core.ollama import OllamaManager
            ollama = OllamaManager(self.config)
            self._llm_fn = lambda messages: ollama.chat(messages)["message"]["content"]
        return self._llm_fn
    
    def _get_template(self) -> str:
        """Get prompt template based on style."""
        if self.cot_config.prompt_style == "standard":
            return self.STANDARD_TEMPLATE
        elif self.cot_config.prompt_style == "few_shot":
            return self.FEW_SHOT_TEMPLATE
        else:  # structured
            return self.STRUCTURED_TEMPLATE
    
    @trace_function(attributes={"pattern": "cot", "step": "reason"})
    def _reason(self, question: str) -> str:
        """Generate step-by-step reasoning."""
        start_time = time.time()
        
        template = self._get_template()
        prompt = template.format(question=question)
        
        messages = [{"role": "user", "content": prompt}]
        response = self.llm_fn(messages)
        
        duration_ms = (time.time() - start_time) * 1000
        
        self.record_step(
            action="reason",
            input_data={"question": question, "style": self.cot_config.prompt_style},
            output_data={"response_length": len(response)},
            duration_ms=duration_ms,
        )
        
        return response
    
    def _parse_steps(self, response: str) -> list[dict]:
        """Parse reasoning steps from response."""
        import re
        
        steps = []
        
        # Look for numbered steps
        step_pattern = rf"{self.cot_config.step_prefix}\s*(\d+):?\s*(.+?)(?=(?:{self.cot_config.step_prefix}\s*\d+|{self.cot_config.conclusion_prefix}|$))"
        matches = re.findall(step_pattern, response, re.IGNORECASE | re.DOTALL)
        
        for num, content in matches:
            steps.append({
                "step": int(num),
                "content": content.strip(),
            })
        
        return steps
    
    def _parse_conclusion(self, response: str) -> Optional[str]:
        """Parse conclusion from response."""
        import re
        
        match = re.search(
            rf"{self.cot_config.conclusion_prefix}\s*(.+)",
            response,
            re.IGNORECASE | re.DOTALL
        )
        if match:
            return match.group(1).strip()
        
        # If no explicit conclusion, return last part of response
        lines = response.strip().split("\n")
        if lines:
            return lines[-1].strip()
        return None
    
    def _execute(self, input_data: Any) -> Any:
        """Execute Chain of Thought reasoning."""
        # Handle input
        if isinstance(input_data, str):
            question = input_data
        elif isinstance(input_data, dict):
            question = input_data.get("question", input_data.get("problem", ""))
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}")
        
        # Generate reasoning
        response = self._reason(question)
        
        # Parse steps and conclusion
        steps = self._parse_steps(response)
        conclusion = self._parse_conclusion(response)
        
        # Record parsed steps
        for step in steps:
            self.record_step(
                action=f"reasoning_step_{step['step']}",
                output_data=step["content"][:100],
            )
        
        if self.cot_config.show_reasoning:
            return {
                "reasoning": response,
                "steps": steps,
                "conclusion": conclusion,
            }
        else:
            return conclusion
    
    def solve(
        self,
        problem: str,
        experiment_name: Optional[str] = None,
    ):
        """
        Convenience method to solve a problem.
        
        Args:
            problem: Problem to solve
            experiment_name: MLFlow experiment name
        
        Returns:
            PatternResult with reasoning and conclusion
        """
        return self.execute(
            input_data=problem,
            experiment_name=experiment_name,
            run_name=f"cot-{problem[:20]}",
        )
    
    def explain(
        self,
        concept: str,
        experiment_name: Optional[str] = None,
    ):
        """
        Explain a concept step by step.
        
        Args:
            concept: Concept to explain
            experiment_name: MLFlow experiment name
        
        Returns:
            PatternResult with explanation
        """
        question = f"Explain the concept of {concept} step by step."
        return self.execute(
            input_data=question,
            experiment_name=experiment_name,
            run_name=f"explain-{concept[:20]}",
        )

