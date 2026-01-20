"""
Evaluation nodes for quality assessment.

This module provides flow nodes for evaluating outputs:
- LLMJudgeNode: Use an LLM to evaluate quality
- FaithfulnessNode: Check if response is grounded in context
- RelevanceNode: Check if response is relevant to query

These nodes can emit RL metrics for reinforcement learning optimization.

Example:
    >>> from agentic_assistants.pipelines.nodes import LLMJudgeNode
    >>> 
    >>> judge = LLMJudgeNode(config=LLMJudgeConfig(
    ...     criteria=["accuracy", "clarity", "completeness"],
    ...     emit_rl_metric=True,
    ... ))
    >>> 
    >>> result = judge.run({
    ...     "query": "What is machine learning?",
    ...     "response": "Machine learning is...",
    ... })
    >>> print(result.outputs["scores"])
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from agentic_assistants.pipelines.nodes.base import BaseFlowNode, NodeConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Configuration Classes
# =============================================================================

@dataclass
class LLMJudgeConfig(NodeConfig):
    """Configuration for LLMJudgeNode."""
    
    # Model to use for evaluation
    model: str = "llama3.2"
    
    # Evaluation criteria
    criteria: List[str] = field(default_factory=lambda: ["accuracy", "relevance", "completeness"])
    
    # Score range (min, max)
    score_range: Tuple[int, int] = (1, 5)
    
    # Custom evaluation prompt template
    prompt_template: str = ""
    
    # Whether to emit RL metrics
    emit_rl_metric: bool = True
    
    # Name for the RL metric
    metric_name: str = "response_quality"
    
    # Model host
    host: str = "http://localhost:11434"


@dataclass
class FaithfulnessConfig(NodeConfig):
    """Configuration for FaithfulnessNode."""
    
    # Minimum faithfulness threshold
    threshold: float = 0.8
    
    # Model for evaluation
    model: str = "llama3.2"
    
    # Whether to emit RL metric
    emit_rl_metric: bool = True
    
    # Host URL
    host: str = "http://localhost:11434"


@dataclass
class RelevanceConfig(NodeConfig):
    """Configuration for RelevanceNode."""
    
    # Minimum relevance threshold
    threshold: float = 0.7
    
    # Model for evaluation
    model: str = "llama3.2"
    
    # Whether to emit RL metric
    emit_rl_metric: bool = True
    
    # Host URL
    host: str = "http://localhost:11434"


# =============================================================================
# Node Implementations
# =============================================================================

class LLMJudgeNode(BaseFlowNode):
    """
    Node for evaluating outputs using an LLM as judge.
    
    Inputs:
        query: The original query
        response: The response to evaluate
        context: Optional context used for generation
        
    Outputs:
        scores: Dictionary of criterion scores
        overall_score: Average score across criteria
        feedback: Evaluation feedback text
    """
    
    node_type = "llm_judge"
    config_class = LLMJudgeConfig
    
    DEFAULT_PROMPT = """You are an expert evaluator. Rate the following response on a scale of {min_score} to {max_score} for each criterion.

Query: {query}

Response: {response}

{context_section}

Evaluate the response on these criteria:
{criteria_list}

For each criterion, provide:
1. A score from {min_score} to {max_score}
2. A brief justification

Format your response as:
CRITERION: score - justification

Finally, provide an overall assessment."""
    
    def __init__(self, config: Optional[LLMJudgeConfig] = None, **kwargs):
        super().__init__(config or LLMJudgeConfig(), **kwargs)
        self.config: LLMJudgeConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query", "")
        response = inputs.get("response", "")
        context = inputs.get("context", "")
        
        if not response:
            return {"scores": {}, "overall_score": 0, "feedback": "No response to evaluate"}
        
        try:
            from langchain_ollama import ChatOllama
            from langchain_core.messages import HumanMessage, SystemMessage
            
            llm = ChatOllama(
                model=self.config.model,
                base_url=self.config.host,
                temperature=0.1,  # Low temperature for consistent evaluation
            )
            
            # Build evaluation prompt
            template = self.config.prompt_template or self.DEFAULT_PROMPT
            
            context_section = f"Context used:\n{context}" if context else ""
            criteria_list = "\n".join(f"- {c}" for c in self.config.criteria)
            
            prompt = template.format(
                query=query,
                response=response,
                context_section=context_section,
                criteria_list=criteria_list,
                min_score=self.config.score_range[0],
                max_score=self.config.score_range[1],
            )
            
            messages = [
                SystemMessage(content="You are an objective evaluator. Be fair and consistent in your assessments."),
                HumanMessage(content=prompt),
            ]
            
            eval_response = llm.invoke(messages)
            eval_text = eval_response.content
            
            # Parse scores from response
            scores = self._parse_scores(eval_text)
            
            # Calculate overall score
            if scores:
                overall_score = sum(scores.values()) / len(scores)
            else:
                # Fallback to middle of range
                overall_score = (self.config.score_range[0] + self.config.score_range[1]) / 2
            
            # Normalize to 0-1 for RL metric
            normalized_score = (overall_score - self.config.score_range[0]) / (
                self.config.score_range[1] - self.config.score_range[0]
            )
            
            # Emit metrics
            self.emit_metric("overall_score", overall_score)
            for criterion, score in scores.items():
                self.emit_metric(f"score_{criterion}", score)
            
            # Emit RL metric
            if self.config.emit_rl_metric:
                self.emit_rl_metric(self.config.metric_name, normalized_score)
            
            return {
                "scores": scores,
                "overall_score": overall_score,
                "normalized_score": normalized_score,
                "feedback": eval_text,
            }
            
        except ImportError:
            logger.warning("LLM not available for evaluation")
            return {"scores": {}, "overall_score": 0, "feedback": "LLM not available"}
        except Exception as e:
            logger.error(f"LLM evaluation failed: {e}")
            raise
    
    def _parse_scores(self, text: str) -> Dict[str, float]:
        """Parse scores from evaluation text."""
        scores = {}
        
        for criterion in self.config.criteria:
            # Look for patterns like "CRITERION: 4" or "criterion - 4"
            import re
            pattern = rf"{criterion}[:\-\s]+(\d+(?:\.\d+)?)"
            match = re.search(pattern, text, re.IGNORECASE)
            
            if match:
                try:
                    score = float(match.group(1))
                    # Clamp to score range
                    score = max(self.config.score_range[0], min(self.config.score_range[1], score))
                    scores[criterion] = score
                except ValueError:
                    pass
        
        return scores
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "response": {"type": "string"},
                "context": {"type": "string"},
            },
            "required": ["response"],
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "scores": {"type": "object"},
                "overall_score": {"type": "number"},
                "normalized_score": {"type": "number"},
                "feedback": {"type": "string"},
            },
        }


class FaithfulnessNode(BaseFlowNode):
    """
    Node for checking if a response is faithful to the context.
    
    Inputs:
        response: The generated response
        context: The context/documents used
        
    Outputs:
        score: Faithfulness score (0-1)
        passed: Whether it meets the threshold
        claims: Identified claims and their verification
    """
    
    node_type = "faithfulness"
    config_class = FaithfulnessConfig
    
    def __init__(self, config: Optional[FaithfulnessConfig] = None, **kwargs):
        super().__init__(config or FaithfulnessConfig(), **kwargs)
        self.config: FaithfulnessConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        response = inputs.get("response", "")
        context = inputs.get("context", "")
        
        if not response:
            return {"score": 0, "passed": False, "claims": []}
        
        if not context:
            # Cannot verify faithfulness without context
            return {"score": 0.5, "passed": False, "claims": [], "warning": "No context provided"}
        
        try:
            from langchain_ollama import ChatOllama
            from langchain_core.messages import HumanMessage, SystemMessage
            
            llm = ChatOllama(
                model=self.config.model,
                base_url=self.config.host,
                temperature=0.1,
            )
            
            prompt = f"""Evaluate whether the following response is faithful to the provided context.
A faithful response only contains information that can be verified from the context.

Context:
{context}

Response:
{response}

Identify the key claims in the response and check if each is supported by the context.
Rate overall faithfulness from 0.0 (completely unfaithful) to 1.0 (completely faithful).

Format:
CLAIMS:
1. [claim] - SUPPORTED/NOT SUPPORTED
2. [claim] - SUPPORTED/NOT SUPPORTED
...

FAITHFULNESS SCORE: [0.0-1.0]"""

            messages = [
                SystemMessage(content="You are a fact-checker. Be strict and objective."),
                HumanMessage(content=prompt),
            ]
            
            eval_response = llm.invoke(messages)
            eval_text = eval_response.content
            
            # Parse score
            import re
            score_match = re.search(r"FAITHFULNESS SCORE:\s*([\d.]+)", eval_text, re.IGNORECASE)
            score = float(score_match.group(1)) if score_match else 0.5
            score = max(0.0, min(1.0, score))
            
            passed = score >= self.config.threshold
            
            # Emit metrics
            self.emit_metric("faithfulness_score", score)
            
            if self.config.emit_rl_metric:
                self.emit_rl_metric("faithfulness", score)
            
            return {
                "score": score,
                "passed": passed,
                "feedback": eval_text,
            }
            
        except ImportError:
            logger.warning("LLM not available")
            return {"score": 0.5, "passed": False, "error": "LLM not available"}
        except Exception as e:
            logger.error(f"Faithfulness check failed: {e}")
            raise


class RelevanceNode(BaseFlowNode):
    """
    Node for checking if a response is relevant to the query.
    
    Inputs:
        query: The original query
        response: The generated response
        
    Outputs:
        score: Relevance score (0-1)
        passed: Whether it meets the threshold
    """
    
    node_type = "relevance"
    config_class = RelevanceConfig
    
    def __init__(self, config: Optional[RelevanceConfig] = None, **kwargs):
        super().__init__(config or RelevanceConfig(), **kwargs)
        self.config: RelevanceConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query", "")
        response = inputs.get("response", "")
        
        if not query or not response:
            return {"score": 0, "passed": False}
        
        try:
            from langchain_ollama import ChatOllama
            from langchain_core.messages import HumanMessage, SystemMessage
            
            llm = ChatOllama(
                model=self.config.model,
                base_url=self.config.host,
                temperature=0.1,
            )
            
            prompt = f"""Evaluate how relevant the following response is to the query.
A relevant response directly addresses what the user is asking.

Query: {query}

Response: {response}

Rate relevance from 0.0 (completely irrelevant) to 1.0 (perfectly relevant).

RELEVANCE SCORE: [0.0-1.0]
EXPLANATION: [brief explanation]"""

            messages = [
                SystemMessage(content="You evaluate response relevance objectively."),
                HumanMessage(content=prompt),
            ]
            
            eval_response = llm.invoke(messages)
            eval_text = eval_response.content
            
            # Parse score
            import re
            score_match = re.search(r"RELEVANCE SCORE:\s*([\d.]+)", eval_text, re.IGNORECASE)
            score = float(score_match.group(1)) if score_match else 0.5
            score = max(0.0, min(1.0, score))
            
            passed = score >= self.config.threshold
            
            # Emit metrics
            self.emit_metric("relevance_score", score)
            
            if self.config.emit_rl_metric:
                self.emit_rl_metric("relevance", score)
            
            return {
                "score": score,
                "passed": passed,
                "feedback": eval_text,
            }
            
        except ImportError:
            logger.warning("LLM not available")
            return {"score": 0.5, "passed": False, "error": "LLM not available"}
        except Exception as e:
            logger.error(f"Relevance check failed: {e}")
            raise
