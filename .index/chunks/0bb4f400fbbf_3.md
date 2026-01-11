# Chunk: 0bb4f400fbbf_3

- source: `src/agentic_assistants/utils/context_loader.py`
- lines: 254-315
- chunk: 4/4

```
xt = context[:char_limit] + "\n[Context truncated for token limit]"
        
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

```
