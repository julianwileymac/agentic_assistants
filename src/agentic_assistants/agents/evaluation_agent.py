"""
Evaluation Agent for grading learning responses.

Uses Ollama to evaluate user responses against learning objectives,
providing detailed feedback and scores.
"""

import json
import re
from typing import Any, Dict, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.ollama import OllamaManager
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


EVALUATION_SYSTEM_PROMPT = """You are an expert educational evaluator and learning coach. 
Your task is to assess learner responses fairly and provide constructive, helpful feedback.

When evaluating responses:
1. Assess accuracy and completeness of the response
2. Consider the depth of understanding demonstrated
3. Look for application of concepts, not just memorization
4. Provide specific, actionable feedback for improvement
5. Be encouraging while maintaining high standards
6. Consider partial credit for partially correct answers

Always provide a balanced evaluation that helps the learner grow."""


EVALUATION_TEMPLATE = """Evaluate the following response to a learning assessment question.

Question: {question}

Learner's Response: {response}

Evaluation Type: {evaluation_type}
- comprehension: Test of factual understanding and recall
- application: Test of ability to apply concepts to scenarios
- synthesis: Test of ability to combine ideas creatively
- analysis: Test of ability to break down and examine concepts

{context}

Please evaluate the response and provide your assessment in JSON format:
{{
    "score": <0-100 numeric score>,
    "grade": "<letter grade: A, B, C, D, or F>",
    "feedback": "<detailed, constructive feedback for the learner>",
    "strengths": ["Strength 1", "Strength 2", ...],
    "areas_for_improvement": ["Area 1", "Area 2", ...],
    "key_missing_points": ["Missing point 1", ...],
    "suggestions": "<specific suggestions for further learning>",
    "confidence": <0.0-1.0 confidence in the evaluation>
}}

Be fair but thorough. Provide feedback that helps the learner understand what they did well and how to improve."""


class EvaluationAgent:
    """
    Agent for evaluating learning responses using Ollama.
    
    This agent:
    - Grades user responses on a 0-100 scale
    - Provides detailed, constructive feedback
    - Identifies strengths and areas for improvement
    - Offers suggestions for further learning
    
    Example:
        >>> evaluator = EvaluationAgent()
        >>> result = evaluator.evaluate(
        ...     question="Explain the concept of recursion",
        ...     response="Recursion is when a function calls itself...",
        ...     evaluation_type="comprehension"
        ... )
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        strict_grading: bool = False,
    ):
        """
        Initialize the evaluation agent.
        
        Args:
            config: Agentic configuration instance
            model: Ollama model to use
            system_prompt: Custom system prompt
            strict_grading: If True, apply stricter grading standards
        """
        self.config = config or AgenticConfig()
        self.model = model or self.config.ollama.default_model
        self.system_prompt = system_prompt or EVALUATION_SYSTEM_PROMPT
        self.strict_grading = strict_grading
        self._ollama = OllamaManager(self.config)
    
    def evaluate(
        self,
        question: str,
        response: str,
        evaluation_type: str = "comprehension",
        context: str = "",
        rubric: Optional[Dict[str, Any]] = None,
        expected_points: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a learner's response to a question.
        
        Args:
            question: The question that was asked
            response: The learner's response
            evaluation_type: Type of evaluation (comprehension, application, etc.)
            context: Additional context about the topic/lesson
            rubric: Optional grading rubric with criteria and weights
            expected_points: Optional list of points the answer should cover
        
        Returns:
            Dictionary with score, grade, feedback, and detailed breakdown
        """
        logger.info(f"Evaluating response for: {question[:50]}...")
        
        # Build context section
        context_section = ""
        if context:
            context_section += f"\nTopic Context:\n{context}\n"
        if rubric:
            context_section += f"\nGrading Rubric:\n{json.dumps(rubric, indent=2)}\n"
        if expected_points:
            context_section += f"\nExpected Points to Cover:\n"
            for point in expected_points:
                context_section += f"- {point}\n"
        
        if self.strict_grading:
            context_section += "\nNote: Apply strict grading standards.\n"
        
        prompt = EVALUATION_TEMPLATE.format(
            question=question,
            response=response,
            evaluation_type=evaluation_type,
            context=context_section,
        )
        
        try:
            self._ollama.ensure_running()
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
            
            ollama_response = self._ollama.chat(
                messages=messages,
                model=self.model,
            )
            
            response_text = ollama_response.get("message", {}).get("content", "")
            
            # Parse evaluation result
            result = self._parse_evaluation(response_text)
            
            # Ensure required fields
            result = self._validate_result(result)
            
            logger.info(f"Evaluation complete: score={result['score']}, grade={result['grade']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return self._create_fallback_evaluation(response)
    
    def _parse_evaluation(self, response_text: str) -> Dict[str, Any]:
        """Parse evaluation JSON from LLM response."""
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse evaluation JSON: {e}")
        
        # Fallback: try to extract key information from text
        return self._extract_evaluation_from_text(response_text)
    
    def _extract_evaluation_from_text(self, text: str) -> Dict[str, Any]:
        """Extract evaluation data from unstructured text."""
        result = {
            "score": 70,
            "grade": "C",
            "feedback": text[:500],
            "strengths": [],
            "areas_for_improvement": [],
            "key_missing_points": [],
            "suggestions": "",
            "confidence": 0.5,
        }
        
        # Try to find score
        score_match = re.search(r'(\d{1,3})\s*(?:/\s*100|%|points?)', text, re.IGNORECASE)
        if score_match:
            result["score"] = min(100, int(score_match.group(1)))
            result["grade"] = self._score_to_grade(result["score"])
        
        # Try to find grade
        grade_match = re.search(r'\b([ABCDF][+-]?)\b', text)
        if grade_match and not score_match:
            result["grade"] = grade_match.group(1)
            result["score"] = self._grade_to_score(result["grade"])
        
        return result
    
    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required fields are present and valid."""
        defaults = {
            "score": 0,
            "grade": "F",
            "feedback": "Evaluation completed.",
            "strengths": [],
            "areas_for_improvement": [],
            "key_missing_points": [],
            "suggestions": "",
            "confidence": 0.5,
        }
        
        for key, default in defaults.items():
            if key not in result or result[key] is None:
                result[key] = default
        
        # Validate score range
        result["score"] = max(0, min(100, float(result["score"])))
        
        # Ensure grade matches score
        if not result.get("grade") or result["grade"] not in ["A", "A+", "A-", "B", "B+", "B-", "C", "C+", "C-", "D", "D+", "D-", "F"]:
            result["grade"] = self._score_to_grade(result["score"])
        
        return result
    
    def _create_fallback_evaluation(self, response: str) -> Dict[str, Any]:
        """Create a fallback evaluation when the LLM fails."""
        # Basic heuristic evaluation based on response length and structure
        words = len(response.split())
        
        if words < 10:
            score = 30
            feedback = "The response is too brief. Please provide more detail and explanation."
        elif words < 30:
            score = 50
            feedback = "The response shows some understanding but lacks depth. Consider expanding on key points."
        elif words < 100:
            score = 65
            feedback = "The response demonstrates basic understanding. More specific examples would strengthen it."
        else:
            score = 75
            feedback = "The response is detailed. Review for accuracy and completeness."
        
        return {
            "score": score,
            "grade": self._score_to_grade(score),
            "feedback": feedback,
            "strengths": ["Response provided"],
            "areas_for_improvement": ["Could not perform detailed evaluation - please review manually"],
            "key_missing_points": [],
            "suggestions": "Review the material and consider expanding your response.",
            "confidence": 0.3,
        }
    
    @staticmethod
    def _score_to_grade(score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 93:
            return "A"
        elif score >= 90:
            return "A-"
        elif score >= 87:
            return "B+"
        elif score >= 83:
            return "B"
        elif score >= 80:
            return "B-"
        elif score >= 77:
            return "C+"
        elif score >= 73:
            return "C"
        elif score >= 70:
            return "C-"
        elif score >= 67:
            return "D+"
        elif score >= 63:
            return "D"
        elif score >= 60:
            return "D-"
        else:
            return "F"
    
    @staticmethod
    def _grade_to_score(grade: str) -> float:
        """Convert letter grade to approximate numeric score."""
        grade_map = {
            "A+": 98, "A": 95, "A-": 92,
            "B+": 88, "B": 85, "B-": 82,
            "C+": 78, "C": 75, "C-": 72,
            "D+": 68, "D": 65, "D-": 62,
            "F": 50,
        }
        return grade_map.get(grade.upper(), 70)
    
    def evaluate_with_rubric(
        self,
        question: str,
        response: str,
        rubric: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate a response against a specific rubric.
        
        Args:
            question: The question asked
            response: The learner's response
            rubric: Rubric with criteria and point values
                    Format: {"criteria_name": {"description": str, "points": int}, ...}
        
        Returns:
            Detailed evaluation with per-criterion scores
        """
        prompt = f"""Evaluate this response against the provided rubric.

Question: {question}

Response: {response}

Rubric:
{json.dumps(rubric, indent=2)}

Evaluate each criterion and provide scores. Return JSON:
{{
    "total_score": <sum of earned points>,
    "max_score": <sum of possible points>,
    "percentage": <percentage earned>,
    "grade": "<letter grade>",
    "criteria_scores": {{
        "<criterion_name>": {{
            "earned": <points earned>,
            "possible": <points possible>,
            "feedback": "<specific feedback for this criterion>"
        }}
    }},
    "overall_feedback": "<overall feedback>",
    "strengths": [...],
    "areas_for_improvement": [...]
}}"""

        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
            
            ollama_response = self._ollama.chat(messages=messages, model=self.model)
            response_text = ollama_response.get("message", {}).get("content", "")
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Rubric evaluation failed: {e}")
        
        # Fallback
        max_score = sum(c.get("points", 0) for c in rubric.values())
        return {
            "total_score": max_score * 0.7,
            "max_score": max_score,
            "percentage": 70,
            "grade": "C",
            "criteria_scores": {},
            "overall_feedback": "Evaluation could not be completed with full detail.",
            "strengths": [],
            "areas_for_improvement": [],
        }
    
    def compare_responses(
        self,
        question: str,
        responses: list,
        criteria: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Compare multiple responses to the same question.
        
        Useful for peer assessment or comparing different approaches.
        
        Args:
            question: The question asked
            responses: List of responses to compare
            criteria: Optional list of criteria to evaluate on
        
        Returns:
            Comparison results with rankings and analysis
        """
        criteria_text = ""
        if criteria:
            criteria_text = f"\nEvaluate on these criteria: {', '.join(criteria)}"
        
        responses_text = "\n\n".join(
            f"Response {i+1}:\n{r}" for i, r in enumerate(responses)
        )
        
        prompt = f"""Compare and rank these responses to the same question.

Question: {question}
{criteria_text}

{responses_text}

Provide your analysis in JSON format:
{{
    "rankings": [
        {{"response_number": 1, "rank": <1 being best>, "score": <0-100>, "summary": "Brief summary"}}
    ],
    "best_response": <response number>,
    "comparison_notes": "What distinguishes the responses",
    "common_strengths": [...],
    "common_weaknesses": [...]
}}"""

        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
            
            ollama_response = self._ollama.chat(messages=messages, model=self.model)
            response_text = ollama_response.get("message", {}).get("content", "")
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Response comparison failed: {e}")
        
        return {
            "rankings": [
                {"response_number": i+1, "rank": i+1, "score": 70, "summary": ""}
                for i in range(len(responses))
            ],
            "best_response": 1,
            "comparison_notes": "Comparison could not be completed.",
            "common_strengths": [],
            "common_weaknesses": [],
        }
