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

    def load_file(self, relative_path: str) -> str:
        """
        Load a file's contents.
        
        Args:
            relative_path: Path relative to .index/ directory
        
        Returns:
            File contents as string
        """
        if relative_path.startswith("../"):
            file_path = self.project_root / relative_path[3:]
        else:
            file_path = self.index_dir / relative_path
        
        try:
            return file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning(f"Context file not found: {file_path}")
            return f"[File not found: {relative_path}]"

    def load_core_context(self) -> str:
        """
        Load core context files (architecture + API surface).
        
        This is the minimum context needed for most tasks.
        Approximately 800-1000 tokens.
        
        Returns:
            Formatted context string
        """
        architecture = self.load_file("context/architecture.md")
        api = self.load_file("context/api-surface.md")
        
        return f"""# Agentic Assistants - Core Context

## Architecture
{architecture}

## Public API
{api}
"""

    def load_full_context(self) -> str:
        """
        Load all context files.
        
        Use this for models with larger context windows (8K+).
        Approximately 2000-2500 tokens.
        
        Returns:
            Formatted context string
        """
        parts = ["# Agentic Assistants - Full Context\n"]
        
        for name, filename in self.CONTEXT_FILES.items():
            content = self.load_file(f"context/{filename}")
            parts.append(f"\n## {name.title()}\n{content}")
        
        return "\n".join(parts)

    def load_for_task(self, task: str) -> str:
        """
        Load context optimized for a specific task.
        
        Args:
            task: Task type. One of:
                  - add_adapter: Creating a new framework adapter
                  - add_cli_command: Adding a CLI command
                  - add_config: Adding configuration options
                  - debug: Debugging issues
                  - understand: Understanding the codebase
        
        Returns:
            Formatted context string
        """
        if task not in self.TASK_FILES:
            available = ", ".join(self.TASK_FILES.keys())
            logger.warning(f"Unknown task '{task}'. Available: {available}")
            return self.load_core_context()
        
        files = self.TASK_FILES[task]
        parts = [f"# Context for: {task}\n"]
        
        for file_path in files:
            content = self.load_file(file_path)
            filename = Path(file_path).name
            parts.append(f"\n## {filename}\n```\n{content}\n```")
        
        return "\n".join(parts)

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Uses rough approximation of 4 characters per token.
        
        Args:
            text: Text to estimate
        
        Returns:
            Estimated token count
        """
        return len(text) // 4

    def get_context_summary(self) -> dict:
        """
        Get summary of available context and estimated sizes.
        
        Returns:
            Dictionary with context options and token estimates
        """
        summary = {
            "core_context": {
                "files": ["architecture.md", "api-surface.md"],
                "estimated_tokens": self.estimate_tokens(self.load_core_context()),
            },
            "full_context": {
                "files": list(self.CONTEXT_FILES.values()),
                "estimated_tokens": self.estimate_tokens(self.load_full_context()),
            },
            "tasks": {},
        }
        
        for task in self.TASK_FILES:
            context = self.load_for_task(task)
            summary["tasks"][task] = {
                "files": self.TASK_FILES[task],
                "estimated_tokens": self.estimate_tokens(context),
            }
        
        return summary

    def format_for_prompt(
        self,
        context: str,
        task_description: str,
        max_tokens: int = 4000,
    ) -> str:
        """
        Format context and task into a ready-to-use prompt.
        
        Args:
            context: Context string from load_* methods
            task_description: What you want the AI to do
            max_tokens: Maximum context tokens (trims if needed)
        
        Returns:
            Formatted prompt string
        """
        # Estimate and trim if needed
        context_tokens = self.estimate_tokens(context)
        if context_tokens > max_tokens * 0.7:  # Leave room for task + response
            # Truncate context
            char_limit = int(max_tokens * 0.7 * 4)
            context = context[:char_limit] + "\n[Context truncated for token limit]"
        
        return f"""{context}

---

## Your Task

{task_description}

Please follow the project patterns and conventions shown above.
"""


def load_context_for_chat(task: str = "understand") -> str:
    """
    Convenience function to load context for a chat session.
    
    Args:
        task: Task type (see ContextLoader.load_for_task)
    
    Returns:
        Ready-to-use context string
    """
    loader = ContextLoader()
    return loader.load_for_task(task)


def print_context_summary():
    """Print a summary of available context options."""
    loader = ContextLoader()
    summary = loader.get_context_summary()
    
    print("Available Context Options:")
    print("=" * 50)
    
    print(f"\nCore Context: ~{summary['core_context']['estimated_tokens']} tokens")
    print(f"  Files: {', '.join(summary['core_context']['files'])}")
    
    print(f"\nFull Context: ~{summary['full_context']['estimated_tokens']} tokens")
    print(f"  Files: {', '.join(summary['full_context']['files'])}")
    
    print("\nTask-Specific Context:")
    for task, info in summary["tasks"].items():
        print(f"\n  {task}: ~{info['estimated_tokens']} tokens")
        for f in info["files"]:
            print(f"    - {f}")


if __name__ == "__main__":
    # Demo usage
    print_context_summary()
    print("\n" + "=" * 50)
    print("\nExample - Loading core context:")
    print("=" * 50)
    
    loader = ContextLoader()
    core = loader.load_core_context()
    print(core[:500] + "...\n")
    print(f"Total tokens: ~{loader.estimate_tokens(core)}")

