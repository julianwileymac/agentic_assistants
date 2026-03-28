# requires: agno
"""Agno: Agent with tools and structured output (output_schema).

Demonstrates description, instructions, and plain callables as tools. No API key needed
to print configuration; live runs require a model and provider credentials.
"""

from __future__ import annotations


def main() -> None:
    try:
        from pydantic import BaseModel, Field

        from agno.agent import Agent
    except ImportError:
        print(
            "Install agno (and pydantic) to run this example: pip install agno pydantic\n\n"
            "Expected pattern:\n"
            "  from pydantic import BaseModel, Field\n"
            "  from agno.agent import Agent\n"
            "  class Answer(BaseModel):\n"
            "      summary: str\n"
            "      confidence: float = Field(ge=0, le=1)\n"
            "  def roll_dice(sides: int = 6) -> str:\n"
            "      return str(random.randint(1, sides))\n"
            "  agent = Agent(\n"
            "      name='Demo',\n"
            "      description='Dice + structured summaries',\n"
            "      instructions=['Be concise', 'Use tools when randomness is needed'],\n"
            "      tools=[roll_dice],\n"
            "      output_schema=Answer,\n"
            "      model=OpenAIChat(id='gpt-4o-mini'),\n"
            "  )\n"
        )
        return

    import random

    class DemoAnswer(BaseModel):
        """Structured final response."""

        summary: str = Field(description="Short natural language summary")
        confidence: float = Field(ge=0, le=1, description="Self-rated confidence")

    def roll_dice(sides: int = 6) -> str:
        """Roll an N-sided die (simulated locally)."""
        s = max(2, min(int(sides), 100))
        return str(random.randint(1, s))

    agent = Agent(
        name="structured_demo_agent",
        description="Answers with a structured object and can roll dice via a tool.",
        instructions=[
            "You are a demo assistant.",
            "When the user asks for randomness, call roll_dice.",
            "Otherwise respond with a structured DemoAnswer-compatible result at the end of reasoning.",
        ],
        tools=[roll_dice],
        output_schema=DemoAnswer,
        markdown=False,
        model=None,
    )

    print("=== Agno — Agent with tools + output_schema ===")
    print(f"\nname: {agent.name}")
    print(f"description: {agent.description}")
    print("instructions:")
    for line in agent.instructions or []:
        print(f"  - {line}")
    print(f"\noutput_schema: {DemoAnswer.__name__}")
    print(DemoAnswer.model_json_schema())
    print("\nTool callable registered:")
    doc = roll_dice.__doc__ or "no docstring"
    print(f"  roll_dice: {doc.strip()}")

    tool_list = getattr(agent, "tools", None)
    print(f"\nagent.tools (count): {len(tool_list) if tool_list else 0}")

    print(
        """
--- Tool definition pattern ---
- Pass plain functions in `tools=[...]`; Agno builds schemas from signatures + docstrings.
- `output_schema` constrains the final model output to a Pydantic model (when a model is set).

--- Run (needs credentials) ---
  from agno.models.openai import OpenAIChat
  agent.model = OpenAIChat(id='gpt-4o-mini')
  response = agent.run('Roll a d20 and summarize the outcome.')
  print(response.content)
"""
    )


if __name__ == "__main__":
    main()
