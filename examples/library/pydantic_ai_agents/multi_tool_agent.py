# requires: pydantic-ai pydantic
"""PydanticAI agent with multiple tools.

Demonstrates:
- @agent.tool decorator for defining tools
- Async tool execution
- Tool result handling in agent context
"""

from __future__ import annotations

import math
from typing import Optional

from pydantic import BaseModel, Field


class ResearchResult(BaseModel):
    """Structured research output."""

    query: str
    findings: list[str]
    sources_consulted: int
    confidence: float = Field(ge=0.0, le=1.0)
    calculation_result: Optional[float] = None


def demo_multi_tool_agent():
    """Show an agent with multiple registered tools."""
    try:
        from pydantic_ai import Agent

        agent: Agent[None, ResearchResult] = Agent(
            "openai:gpt-4o-mini",
            output_type=ResearchResult,
            system_prompt="You are a research assistant with access to tools.",
            defer_model_check=True,
        )

        @agent.tool_plain
        def calculate(expression: str) -> str:
            """Evaluate a mathematical expression safely."""
            allowed = set("0123456789+-*/().% ")
            if not all(c in allowed for c in expression):
                return f"Error: invalid characters in expression"
            try:
                result = eval(expression, {"__builtins__": {}}, {"math": math})
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {e}"

        @agent.tool_plain
        def search_database(query: str, limit: int = 5) -> str:
            """Search an internal knowledge base."""
            mock_results = [
                f"Result {i}: Information about '{query}' (relevance: {0.9 - i * 0.1:.1f})"
                for i in range(min(limit, 5))
            ]
            return "\n".join(mock_results)

        @agent.tool_plain
        def get_current_date() -> str:
            """Get the current date and time."""
            from datetime import datetime, timezone
            return datetime.now(timezone.utc).isoformat()

        print("Agent configured with 3 tools:")
        print("  1. calculate - evaluates math expressions")
        print("  2. search_database - queries internal knowledge base")
        print("  3. get_current_date - returns current UTC datetime")
        print()
        print("Output schema:", ResearchResult.model_json_schema())

        print("\n--- Direct tool execution (same functions the agent can call) ---")
        print("calculate('2 + 2'):", calculate("2 + 2"))
        print("search_database('machine learning', 3):\n", search_database("machine learning", 3))
        print("get_current_date():", get_current_date())

        print("\n--- Agent run with TestModel (exercises tool + structured output path) ---")
        try:
            from pydantic_ai.models.test import TestModel

            with agent.override(model=TestModel()):
                run = agent.run_sync("Use tools then summarize: what is sqrt(144)?")
                print("agent.run_sync -> ResearchResult:", run.output)
        except Exception as e:
            print(f"TestModel agent run failed ({type(e).__name__}: {e}).")
            print(
                "The agent would call registered tools, then validate a ResearchResult from the model output."
            )

        print("\n--- Optional: live OpenAI (needs OPENAI_API_KEY) ---")
        try:
            from pydantic_ai.models import infer_model

            live = infer_model("openai:gpt-4o-mini")
            with agent.override(model=live):
                live_run = agent.run_sync("Brief research note on Python 3.12.")
            print("Live model output:", live_run.output)
        except Exception as e:
            print(f"Skipping live OpenAI ({type(e).__name__}: {e}).")

    except ImportError:
        print("Install pydantic-ai: pip install pydantic-ai")


def main() -> None:
    """Run the multi-tool agent example."""
    demo_multi_tool_agent()


if __name__ == "__main__":
    main()
