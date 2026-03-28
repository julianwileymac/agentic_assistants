# requires: agno
"""Agno: one Agent with multiple tools (search sim, math, data lookup).

Prints tool list and configuration without calling a remote LLM.
"""

from __future__ import annotations

import json
import math
from typing import Any


def main() -> None:
    try:
        from agno.agent import Agent
    except ImportError:
        print(
            "Install agno to run this example: pip install agno\n\n"
            "Sketch:\n"
            "  tools = [simulate_web_search, calculate_expression, lookup_record]\n"
            "  agent = Agent(name='multi', tools=tools, instructions=[...], model=...)\n"
        )
        return

    def simulate_web_search(query: str, top_k: int = 3) -> str:
        """Simulated web search returning canned snippets (no HTTP)."""
        k = max(1, min(int(top_k), 5))
        results = [
            {"title": f"Result {i + 1} for {query!r}", "snippet": f"Snippet about {query} ({i})."}
            for i in range(k)
        ]
        return json.dumps({"query": query, "results": results})

    def calculate_expression(expression: str) -> str:
        """Evaluate a safe arithmetic expression (+ - * / **, parentheses)."""
        allowed = set("0123456789+-*/().** ")
        if not expression or not all(c in allowed for c in expression):
            return json.dumps({"error": "unsupported expression", "expression": expression})
        try:
            val = eval(expression, {"__builtins__": {}}, {"sqrt": math.sqrt})  # noqa: S307
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"error": str(exc)})
        return json.dumps({"value": val})

    def lookup_record(record_id: str) -> str:
        """Mock key-value lookup by id."""
        db = {"user:1": {"name": "Ada", "tier": "pro"}, "user:2": {"name": "Lin", "tier": "free"}}
        row = db.get(record_id.strip())
        if not row:
            return json.dumps({"found": False, "record_id": record_id})
        return json.dumps({"found": True, "record_id": record_id, **row})

    tools: list[Any] = [simulate_web_search, calculate_expression, lookup_record]

    agent = Agent(
        name="multi_tool_agent",
        description="Search (simulated), calculate, and lookup mock records.",
        instructions=[
            "Pick the minimal tool set needed for each user request.",
            "Prefer calculate_expression for numeric formulas.",
            "Use lookup_record only when an id like user:1 is provided.",
        ],
        tools=tools,
        model=None,
    )

    print("=== Agno — multi-tool agent ===")
    print(f"\nAgent: {agent.name}")
    print(f"Description: {agent.description}")
    print("\nInstructions:")
    for ins in agent.instructions or []:
        print(f"  • {ins}")

    print("\nRegistered tool callables:")
    for fn in tools:
        doc = (fn.__doc__ or "").strip().split("\n")[0]
        print(f"  - {fn.__name__}: {doc}")

    bound = getattr(agent, "tools", None) or []
    print(f"\nagent.tools length: {len(bound)}")

    print("\n--- Sample direct tool calls (no LLM) ---")
    print(simulate_web_search("Agno agents"))
    print(calculate_expression("(2 ** 8) / 4"))
    print(lookup_record("user:1"))


if __name__ == "__main__":
    main()
