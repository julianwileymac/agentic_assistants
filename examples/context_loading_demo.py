"""
Context Loading Demo for AI Assistants

This example demonstrates how to use the ContextLoader utility
to prepare context for local LLM-based coding assistants.

Usage:
    python examples/context_loading_demo.py
    
    # Or with the CLI
    agentic run examples/context_loading_demo.py
"""

from agentic_assistants.utils.context_loader import (
    ContextLoader,
    load_context_for_chat,
    print_context_summary,
)


def demo_basic_usage():
    """Show basic context loading."""
    print("=" * 60)
    print("BASIC USAGE")
    print("=" * 60)
    
    loader = ContextLoader()
    
    # Load core context (minimal, always useful)
    core = loader.load_core_context()
    print(f"\nCore context loaded: ~{loader.estimate_tokens(core)} tokens")
    print("-" * 40)
    print(core[:800])
    print("...")


def demo_task_specific():
    """Show task-specific context loading."""
    print("\n" + "=" * 60)
    print("TASK-SPECIFIC CONTEXT")
    print("=" * 60)
    
    loader = ContextLoader()
    
    # Available tasks
    tasks = ["add_adapter", "add_cli_command", "add_config", "debug", "understand"]
    
    for task in tasks:
        context = loader.load_for_task(task)
        tokens = loader.estimate_tokens(context)
        print(f"\n{task}: ~{tokens} tokens")


def demo_prompt_formatting():
    """Show how to format a complete prompt."""
    print("\n" + "=" * 60)
    print("FORMATTED PROMPT")
    print("=" * 60)
    
    loader = ContextLoader()
    
    # Load context for adding an adapter
    context = loader.load_for_task("add_adapter")
    
    # Format into a prompt
    prompt = loader.format_for_prompt(
        context=context,
        task_description="""Create a new adapter for the AutoGen framework.

Requirements:
1. Extend BaseAdapter
2. Implement run() method for executing AutoGen workflows
3. Use track_run() for MLFlow + OpenTelemetry tracking
4. Follow the same patterns as CrewAIAdapter""",
        max_tokens=4000,
    )
    
    print(f"\nFormatted prompt (~{loader.estimate_tokens(prompt)} tokens):")
    print("-" * 40)
    print(prompt[:1500])
    print("...")


def demo_chat_session():
    """Simulate using context in an Ollama chat session."""
    print("\n" + "=" * 60)
    print("OLLAMA CHAT SESSION DEMO")
    print("=" * 60)
    
    from agentic_assistants import AgenticConfig, OllamaManager
    
    config = AgenticConfig()
    ollama = OllamaManager(config)
    
    # Check if Ollama is running
    if not ollama.is_running():
        print("\nOllama is not running. Start it with: agentic ollama start")
        print("Showing what the prompt would look like instead...")
        
        context = load_context_for_chat("understand")
        print(f"\nContext to load (~{len(context)//4} tokens):")
        print("-" * 40)
        print(context[:1000])
        print("...")
        return
    
    # Load context
    context = load_context_for_chat("understand")
    
    # Build messages with context
    messages = [
        {
            "role": "system",
            "content": f"""You are a coding assistant helping with the Agentic Assistants project.
            
Here is the project context:

{context}

Use this context to answer questions about the codebase accurately."""
        },
        {
            "role": "user",
            "content": "How do I create a new adapter for a different agent framework?",
        },
    ]
    
    print("\nSending question to Ollama with codebase context...")
    print("-" * 40)
    
    try:
        response = ollama.chat(messages)
        print("\nResponse:")
        print(response["message"]["content"])
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Ollama is running and a model is available.")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("CONTEXT LOADER DEMO")
    print("Preparing context for AI coding assistants")
    print("=" * 60)
    
    # Show summary first
    print("\n")
    print_context_summary()
    
    # Run demos
    demo_basic_usage()
    demo_task_specific()
    demo_prompt_formatting()
    demo_chat_session()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("""
1. Use ContextLoader in your own scripts:
   from agentic_assistants.utils.context_loader import ContextLoader
   loader = ContextLoader()
   context = loader.load_for_task("add_adapter")

2. Copy context to clipboard for external AI assistants:
   python -c "from agentic_assistants.utils.context_loader import ContextLoader; print(ContextLoader().load_core_context())"

3. Customize context for your specific needs by editing:
   .index/context/*.md
""")


if __name__ == "__main__":
    main()

