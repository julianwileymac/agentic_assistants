# Chunk: 0bb4f400fbbf_1

- source: `src/agentic_assistants/utils/context_loader.py`
- lines: 89-182
- chunk: 2/4

```
 looking for pyproject.toml."""
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
```
