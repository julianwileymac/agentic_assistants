# requires: openai
"""OpenAI Swarm (educational): lightweight handoffs via functions returning another Agent.

Swarm is a separate package (`swarm`) built on the OpenAI Python SDK. This script builds
real Agent objects and prints the handoff flow without calling the API.
"""

from __future__ import annotations

from typing import Any


def main() -> None:
    try:
        from swarm import Agent
    except ImportError:
        print(
            "Install OpenAI Swarm to run this example (in addition to openai):\n"
            "  pip install git+https://github.com/openai/swarm.git\n\n"
            "Handoff pattern:\n"
            "  specialist = Agent(name='Specialist', instructions='...')\n"
            "  def handoff_to_specialist():\n"
            "      return specialist  # returning an Agent transfers control\n"
            "  router = Agent(name='Router', functions=[handoff_to_specialist], ...)\n"
            "  Swarm().run(agent=router, messages=[...])\n"
        )
        return

    haiku_agent = Agent(
        name="HaikuAgent",
        instructions="Reply only in haiku form when you speak.",
    )

    def handoff_to_haiku_agent() -> Agent:
        """Transfer the conversation to the agent that speaks in haikus."""
        return haiku_agent

    router_agent = Agent(
        name="RouterAgent",
        instructions=(
            "You are the first contact. If the user wants poetry or haikus, call "
            "handoff_to_haiku_agent(). Otherwise answer briefly in plain prose."
        ),
        functions=[handoff_to_haiku_agent],
    )

    print("=== Swarm — basic handoff setup ===")
    print(f"\nPrimary agent: {router_agent.name}")
    print(f"  instructions (excerpt): {router_agent.instructions[:120]}...")
    print(f"  functions: {[f.__name__ for f in router_agent.functions]}")

    print(f"\nHandoff target: {haiku_agent.name}")
    print(f"  instructions: {haiku_agent.instructions}")

    print(
        """
--- Handoff flow (client.run) ---
1. Swarm passes messages to the active Agent's instructions as the system prompt.
2. If the model calls handoff_to_haiku_agent(), Swarm executes the Python function.
3. Because that function returns another Agent object, execution switches to HaikuAgent.
4. Subsequent completions use HaikuAgent.instructions until another handoff occurs.
5. Chat history is preserved; only the active system prompt changes.

This is the idiomatic Swarm 'handoff_to_*' pattern: name functions clearly, return Agent.

--- Live run (requires OPENAI_API_KEY) ---
  from swarm import Swarm
  client = Swarm()
  response = client.run(
      agent=router_agent,
      messages=[{"role": "user", "content": "I want a haiku about rivers."}],
  )
  print(response.agent.name, response.messages[-1])
"""
    )

    print("\n--- Simulated outcome (no API call) ---")
    print("  user: I want a haiku about rivers.")
    print("  model would call: handoff_to_haiku_agent()")
    next_agent: Any = handoff_to_haiku_agent()
    print(f"  swarm switches active agent -> {next_agent.name}")


if __name__ == "__main__":
    main()
