# requires: openai
"""OpenAI Swarm: shared context_variables read/write from agent instructions and tools."""

from __future__ import annotations

from typing import Any


def main() -> None:
    try:
        from swarm import Agent
        from swarm.types import Result
    except ImportError:
        print(
            "Install Swarm:\n"
            "  pip install git+https://github.com/openai/swarm.git\n\n"
            "Context variables flow:\n"
            "  def bump_counter(context_variables):\n"
            "      n = int(context_variables.get('counter', 0)) + 1\n"
            "      return Result(value='ok', context_variables={'counter': n})\n"
            "  client.run(..., context_variables={'counter': 0})\n"
        )
        return

    def instructions_with_context(context_variables: dict[str, Any]) -> str:
        user = context_variables.get("user_name", "guest")
        tier = context_variables.get("tier", "free")
        return (
            f"You help {user} (tier={tier}). "
            "You may call set_tier_pro() if they confirm a successful upgrade payment."
        )

    def set_tier_pro(context_variables: dict[str, Any]) -> Result:
        """Mark the session as pro tier after upgrade confirmation."""
        name = context_variables.get("user_name", "user")
        return Result(
            value=f"{name} is now on tier=pro",
            context_variables={"tier": "pro"},
        )

    def note_topic(context_variables: dict[str, Any], topic: str) -> Result:
        """Store the user's current topic in shared context."""
        return Result(
            value=f"remembered topic={topic!r}",
            context_variables={"last_topic": topic},
        )

    agent = Agent(
        name="ContextAgent",
        instructions=instructions_with_context,
        functions=[set_tier_pro, note_topic],
    )

    print("=== Swarm — context_variables ===")
    print(f"\nAgent: {agent.name}")
    print("instructions: callable(context_variables) -> str")
    sample_ctx = {"user_name": "Ravi", "tier": "free"}
    rendered = instructions_with_context(sample_ctx)
    print(f"\nSample rendered system prompt:\n  {rendered}")

    print("\nTool functions accept context_variables dict (injected by Swarm):")
    for fn in agent.functions:
        print(f"  - {fn.__name__}")

    print(
        """
--- Variable flow ---
1. client.run(..., context_variables={...}) seeds shared key/value state.
2. If instructions is callable, Swarm passes context_variables so prompts can personalize.
3. Tool functions may accept a context_variables parameter to read state.
4. Returning Result(..., context_variables={...}) merges updates into the shared dict.
5. Response.context_variables reflects the latest merged map.
"""
    )

    ctx: dict[str, Any] = {"user_name": "Ravi", "tier": "free"}
    print("--- Simulated merge (no API) ---")
    print(f"  start: {ctx}")
    r1 = note_topic(ctx, topic="billing question")
    ctx.update(r1.context_variables or {})
    print(f"  after note_topic: {ctx} | tool value: {r1.value}")
    r2 = set_tier_pro(ctx)
    ctx.update(r2.context_variables or {})
    print(f"  after set_tier_pro: {ctx} | tool value: {r2.value}")


if __name__ == "__main__":
    main()
