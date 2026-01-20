"""
Agents for the Local Coding Assistant.

This module provides specialized agents for coding tasks:
- CodingAgent: Main coding assistant
- ResearchAgent: Deep analysis and research
- ReviewerAgent: Code review specialist
"""

from examples.local_coding_assistant.agents.coding_agent import CodingAgent
from examples.local_coding_assistant.agents.researcher import ResearchAgent
from examples.local_coding_assistant.agents.reviewer import ReviewerAgent

__all__ = [
    "CodingAgent",
    "ResearchAgent",
    "ReviewerAgent",
]
