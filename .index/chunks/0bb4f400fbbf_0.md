# Chunk: 0bb4f400fbbf_0

- source: `src/agentic_assistants/utils/context_loader.py`
- lines: 1-99
- chunk: 1/4

```
"""
Context loader utility for AI coding assistants.

This module provides utilities for loading and formatting codebase context
optimized for local LLMs with limited context windows.

Example:
    >>> from agentic_assistants.utils.context_loader import ContextLoader
    >>> 
    >>> loader = ContextLoader()
    >>> context = loader.load_core_context()
    >>> print(context)  # Ready to paste into an AI assistant
    
    >>> # For specific tasks
    >>> context = loader.load_for_task("add_adapter")
"""

from pathlib import Path
from typing import Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class ContextLoader:
    """
    Load and format codebase context for AI assistants.
    
    This class helps prepare context that fits within limited
    context windows of local LLMs (Ollama models).
    
    Attributes:
        project_root: Root directory of the project
        index_dir: Path to .index directory
    """

    # Context file paths relative to .index/context/
    CONTEXT_FILES = {
        "architecture": "architecture.md",
        "patterns": "patterns.md",
        "api": "api-surface.md",
        "guide": "ollama-assistant.md",
    }

    # Task-specific file recommendations
    TASK_FILES = {
        "add_adapter": [
            "context/architecture.md",
            "context/patterns.md",
            "../src/agentic_assistants/adapters/base.py",
        ],
        "add_cli_command": [
            "context/patterns.md",
            "../src/agentic_assistants/cli.py",
        ],
        "add_config": [
            "context/api-surface.md",
            "../src/agentic_assistants/config.py",
        ],
        "debug": [
            "context/architecture.md",
            "context/api-surface.md",
        ],
        "understand": [
            "context/architecture.md",
            "context/api-surface.md",
            "context/patterns.md",
        ],
    }

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the context loader.
        
        Args:
            project_root: Root directory of the project. 
                          Defaults to finding it automatically.
        """
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Try to find project root by looking for pyproject.toml
            self.project_root = self._find_project_root()
        
        self.index_dir = self.project_root / ".index"

    def _find_project_root(self) -> Path:
        """Find the project root by looking for pyproject.toml."""
        current = Path(__file__).resolve()
        
        for parent in current.parents:
            if (parent / "pyproject.toml").exists():
                return parent
        
        # Fallback to current working directory
        return Path.cwd()

```
