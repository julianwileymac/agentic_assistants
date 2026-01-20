"""
Agent implementations for Agentic Assistants.

The main agent is the FrameworkAssistantAgent, which provides:
- Coding assistance with RAG-enhanced context
- Framework guidance and documentation help
- Meta-analysis for self-improvement

Example:
    >>> from agentic_assistants.agents import FrameworkAssistantAgent
    >>> 
    >>> # Create the assistant
    >>> assistant = FrameworkAssistantAgent()
    >>> 
    >>> # Chat with it
    >>> response = assistant.chat("How do I create a CrewAI agent?")
    >>> 
    >>> # Get coding help
    >>> code = assistant.generate_code("Create a data validation function")
"""

from agentic_assistants.agents.framework_assistant import (
    FrameworkAssistantAgent,
    create_framework_assistant,
)
from agentic_assistants.agents.mcp_code_agent import McpOllamaCodingAgent
from agentic_assistants.agents.lesson_planner import LessonPlannerAgent
from agentic_assistants.agents.evaluation_agent import EvaluationAgent
from agentic_assistants.agents.paper_parser import PaperParserAgent

# Agent modules
from agentic_assistants.agents.modules import (
    CodingHelperModule,
    FrameworkGuideModule,
    MetaAnalyzerModule,
)

__all__ = [
    # Main assistant
    "FrameworkAssistantAgent",
    "create_framework_assistant",
    # Modules
    "CodingHelperModule",
    "FrameworkGuideModule",
    "MetaAnalyzerModule",
    # Other agents
    "McpOllamaCodingAgent",
    "LessonPlannerAgent",
    "EvaluationAgent",
    "PaperParserAgent",
]
