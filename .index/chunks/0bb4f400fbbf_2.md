# Chunk: 0bb4f400fbbf_2

- source: `src/agentic_assistants/utils/context_loader.py`
- lines: 175-270
- chunk: 3/4

```
t in self.TASK_FILES:
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
```
