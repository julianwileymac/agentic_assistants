"""
Lesson Planner Agent for generating structured lesson plans.

Uses Ollama to generate comprehensive, structured lesson plans
from topics, with support for different difficulty levels and
customization options.
"""

import json
import re
from typing import Any, Dict, List, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.ollama import OllamaManager
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


LESSON_PLAN_SYSTEM_PROMPT = """You are an expert educational content designer and curriculum developer. 
Your task is to create comprehensive, well-structured lesson plans that facilitate effective learning.

When creating lesson plans:
1. Start with clear learning objectives
2. Structure content in a logical progression from simple to complex
3. Include practical exercises and real-world examples
4. Add checkpoints for self-assessment
5. Provide additional resources for deeper learning
6. Consider different learning styles (visual, auditory, kinesthetic)

Always output your lesson plan in valid JSON format."""


LESSON_PLAN_TEMPLATE = """Create a detailed lesson plan for the following topic:

Topic: {topic_name}
Description: {topic_description}
Difficulty Level: {difficulty_level}
{additional_context}

Requirements:
- Include exercises: {include_exercises}
- Include resources: {include_resources}

Please create a comprehensive lesson plan with the following JSON structure:
{{
    "title": "Lesson plan title",
    "overview": "Brief overview of what the learner will achieve",
    "objectives": ["Learning objective 1", "Learning objective 2", ...],
    "prerequisites": ["Prerequisite knowledge 1", ...],
    "estimated_duration_minutes": <total estimated time>,
    "sections": [
        {{
            "title": "Section title",
            "content": "Detailed content for this section (use markdown formatting)",
            "summary": "Brief summary of key points",
            "section_type": "content|exercise|quiz|reading|project",
            "estimated_minutes": <time for this section>,
            "resources": [
                {{"type": "link|video|book|article", "title": "Resource title", "url": "optional url"}}
            ],
            "exercises": [
                {{"description": "Exercise description", "difficulty": "easy|medium|hard"}}
            ]
        }}
    ]
}}

Make the content engaging and practical. Use clear explanations and include examples where helpful."""


class LessonPlannerAgent:
    """
    Agent for generating structured lesson plans using Ollama.
    
    This agent creates comprehensive lesson plans with:
    - Clear learning objectives
    - Structured sections with content
    - Practical exercises
    - Resource recommendations
    - Time estimates
    
    Example:
        >>> planner = LessonPlannerAgent()
        >>> plan = planner.generate_plan(
        ...     topic_name="Machine Learning Basics",
        ...     difficulty_level="beginner"
        ... )
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the lesson planner agent.
        
        Args:
            config: Agentic configuration instance
            model: Ollama model to use (defaults to config default)
            system_prompt: Custom system prompt for generation
        """
        self.config = config or AgenticConfig()
        self.model = model or self.config.ollama.default_model
        self.system_prompt = system_prompt or LESSON_PLAN_SYSTEM_PROMPT
        self._ollama = OllamaManager(self.config)
    
    def generate_plan(
        self,
        topic_name: str,
        topic_description: str = "",
        difficulty_level: str = "intermediate",
        additional_context: Optional[str] = None,
        include_exercises: bool = True,
        include_resources: bool = True,
        custom_requirements: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a structured lesson plan for a topic.
        
        Args:
            topic_name: Name of the topic to create a lesson plan for
            topic_description: Additional description of the topic
            difficulty_level: beginner, intermediate, advanced, or expert
            additional_context: Extra context to include in generation
            include_exercises: Whether to include practical exercises
            include_resources: Whether to include resource recommendations
            custom_requirements: Custom requirements to add to the prompt
        
        Returns:
            Dictionary containing the structured lesson plan
        """
        logger.info(f"Generating lesson plan for: {topic_name}")
        
        # Build the prompt
        context_section = ""
        if additional_context:
            context_section = f"\nAdditional Context:\n{additional_context}\n"
        if custom_requirements:
            context_section += f"\nCustom Requirements:\n{custom_requirements}\n"
        
        prompt = LESSON_PLAN_TEMPLATE.format(
            topic_name=topic_name,
            topic_description=topic_description or "No additional description provided",
            difficulty_level=difficulty_level,
            additional_context=context_section,
            include_exercises=include_exercises,
            include_resources=include_resources,
        )
        
        # Generate using Ollama
        try:
            self._ollama.ensure_running()
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
            
            response = self._ollama.chat(
                messages=messages,
                model=self.model,
            )
            
            response_text = response.get("message", {}).get("content", "")
            
            # Parse JSON from response
            plan_data = self._parse_lesson_plan(response_text)
            
            # Store the generation prompt for reference
            plan_data["generation_prompt"] = prompt
            
            logger.info(f"Generated lesson plan with {len(plan_data.get('sections', []))} sections")
            
            return plan_data
            
        except Exception as e:
            logger.error(f"Failed to generate lesson plan: {e}")
            # Return a basic fallback plan
            return self._create_fallback_plan(topic_name, topic_description, difficulty_level)
    
    def _parse_lesson_plan(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the lesson plan JSON from the LLM response.
        
        Args:
            response_text: Raw response text from the LLM
        
        Returns:
            Parsed lesson plan dictionary
        """
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON: {e}")
        
        # If JSON parsing fails, try to extract structured content
        logger.warning("Could not parse JSON from response, creating structured plan from text")
        return self._extract_plan_from_text(response_text)
    
    def _extract_plan_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract a lesson plan structure from unstructured text.
        
        This is a fallback when JSON parsing fails.
        """
        # Basic extraction - split into sections based on common patterns
        sections = []
        current_section = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for section headers (numbered or with specific keywords)
            if re.match(r'^(?:\d+\.|#{1,3}|Section:?)', line):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "title": re.sub(r'^(?:\d+\.|#{1,3}|Section:?)\s*', '', line),
                    "content": "",
                    "section_type": "content",
                    "estimated_minutes": 15,
                    "resources": [],
                    "exercises": [],
                }
            elif current_section:
                current_section["content"] += line + "\n"
        
        if current_section:
            sections.append(current_section)
        
        # If no sections were extracted, create a single section
        if not sections:
            sections = [{
                "title": "Main Content",
                "content": text[:2000],
                "section_type": "content",
                "estimated_minutes": 30,
                "resources": [],
                "exercises": [],
            }]
        
        return {
            "title": "Lesson Plan",
            "overview": text[:500] if len(text) > 500 else text,
            "objectives": ["Understand the key concepts"],
            "prerequisites": [],
            "estimated_duration_minutes": len(sections) * 15,
            "sections": sections,
        }
    
    def _create_fallback_plan(
        self,
        topic_name: str,
        topic_description: str,
        difficulty_level: str,
    ) -> Dict[str, Any]:
        """
        Create a fallback lesson plan when generation fails.
        """
        return {
            "title": f"Lesson Plan: {topic_name}",
            "overview": f"A structured approach to learning {topic_name}. {topic_description}",
            "objectives": [
                f"Understand the fundamentals of {topic_name}",
                "Apply key concepts through practical exercises",
                "Evaluate understanding through self-assessment",
            ],
            "prerequisites": [],
            "estimated_duration_minutes": 120,
            "sections": [
                {
                    "title": "Introduction",
                    "content": f"Welcome to this lesson on {topic_name}. In this section, we'll explore the basic concepts and why they matter.",
                    "summary": "Introduction to the topic and its importance",
                    "section_type": "content",
                    "estimated_minutes": 15,
                    "resources": [],
                    "exercises": [],
                },
                {
                    "title": "Core Concepts",
                    "content": f"The core concepts of {topic_name} form the foundation of understanding. Let's explore each one in detail.",
                    "summary": "Fundamental concepts and principles",
                    "section_type": "content",
                    "estimated_minutes": 30,
                    "resources": [],
                    "exercises": [],
                },
                {
                    "title": "Practical Application",
                    "content": "Now let's put what we've learned into practice with hands-on exercises.",
                    "summary": "Hands-on practice and application",
                    "section_type": "exercise",
                    "estimated_minutes": 45,
                    "resources": [],
                    "exercises": [
                        {
                            "description": f"Apply the concepts of {topic_name} to a practical scenario",
                            "difficulty": "medium",
                        }
                    ],
                },
                {
                    "title": "Review and Assessment",
                    "content": "Let's review what we've learned and test your understanding.",
                    "summary": "Review key takeaways and self-assessment",
                    "section_type": "quiz",
                    "estimated_minutes": 20,
                    "resources": [],
                    "exercises": [],
                },
                {
                    "title": "Next Steps",
                    "content": "Congratulations on completing this lesson! Here are some suggestions for continuing your learning journey.",
                    "summary": "Suggestions for further learning",
                    "section_type": "content",
                    "estimated_minutes": 10,
                    "resources": [],
                    "exercises": [],
                },
            ],
        }
    
    def enhance_section(
        self,
        section: Dict[str, Any],
        topic_context: str,
        enhancement_type: str = "expand",
    ) -> Dict[str, Any]:
        """
        Enhance a specific section of a lesson plan.
        
        Args:
            section: The section to enhance
            topic_context: Context about the overall topic
            enhancement_type: Type of enhancement (expand, simplify, add_examples)
        
        Returns:
            Enhanced section dictionary
        """
        enhancement_prompts = {
            "expand": "Expand this section with more detailed explanations and examples.",
            "simplify": "Simplify this section for easier understanding by beginners.",
            "add_examples": "Add more practical examples and use cases to this section.",
            "add_exercises": "Add practical exercises and hands-on activities.",
        }
        
        prompt = f"""Given this lesson section about {topic_context}:

Title: {section.get('title', '')}
Content: {section.get('content', '')}

{enhancement_prompts.get(enhancement_type, enhancement_prompts['expand'])}

Return the enhanced section in JSON format with the same structure:
{{
    "title": "Section title",
    "content": "Enhanced content",
    "summary": "Updated summary",
    "section_type": "{section.get('section_type', 'content')}",
    "estimated_minutes": <updated time estimate>,
    "resources": [...],
    "exercises": [...]
}}"""

        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
            
            response = self._ollama.chat(messages=messages, model=self.model)
            response_text = response.get("message", {}).get("content", "")
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Section enhancement failed: {e}")
        
        return section
    
    def generate_section_quiz(
        self,
        section: Dict[str, Any],
        num_questions: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions for a lesson section.
        
        Args:
            section: The section to generate questions for
            num_questions: Number of questions to generate
        
        Returns:
            List of quiz question dictionaries
        """
        prompt = f"""Generate {num_questions} quiz questions to test understanding of this lesson section:

Title: {section.get('title', '')}
Content: {section.get('content', '')}

Return questions as a JSON array:
[
    {{
        "question": "Question text",
        "type": "multiple_choice|true_false|short_answer",
        "options": ["A", "B", "C", "D"],  // for multiple choice only
        "correct_answer": "The correct answer",
        "explanation": "Why this is correct"
    }}
]"""

        try:
            messages = [
                {"role": "system", "content": "You are an expert at creating educational assessments."},
                {"role": "user", "content": prompt},
            ]
            
            response = self._ollama.chat(messages=messages, model=self.model)
            response_text = response.get("message", {}).get("content", "")
            
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Quiz generation failed: {e}")
        
        return []
