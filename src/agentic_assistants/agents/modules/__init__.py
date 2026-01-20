"""
Agent modules for the Framework Assistant.

These modules provide specialized capabilities:
- CodingHelper: Code generation, review, and debugging assistance
- FrameworkGuide: Framework feature guidance and help
- MetaAnalyzerModule: Self-improvement analysis and suggestions
"""

from agentic_assistants.agents.modules.coding_helper import CodingHelperModule
from agentic_assistants.agents.modules.framework_guide import FrameworkGuideModule
from agentic_assistants.agents.modules.meta_analyzer_module import MetaAnalyzerModule

__all__ = [
    "CodingHelperModule",
    "FrameworkGuideModule",
    "MetaAnalyzerModule",
]
