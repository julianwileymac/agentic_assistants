# requires: pydantic-ai pydantic
"""PydanticAI streaming structured output.

Demonstrates:
- Streaming responses with partial structured output
- Progressive validation as chunks arrive
- Stream consumption patterns
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ArticleSummary(BaseModel):
    """Structured article summary built progressively via streaming."""

    title: str
    author: str = ""
    main_points: list[str] = Field(default_factory=list)
    sentiment: str = Field(default="neutral", description="positive, neutral, or negative")
    word_count_estimate: int = Field(default=0, ge=0)
    key_quotes: list[str] = Field(default_factory=list)


async def demo_streaming():
    """Show streaming structured output with PydanticAI."""
    try:
        from pydantic_ai import Agent

        agent: Agent[None, ArticleSummary] = Agent(
            "openai:gpt-4o-mini",
            output_type=ArticleSummary,
            system_prompt="Summarize articles in the requested structured format.",
            defer_model_check=True,
        )

        print("Streaming agent configured.")
        print("Typical pattern (current API prefers stream_output + get_output):")
        print()
        print("  async with agent.run_stream('Summarize this article...') as result:")
        print("      async for partial in result.stream_output(debounce_by=None):")
        print("          print(partial)  # Partial ArticleSummary (Pydantic partial validation)")
        print("      final = await result.get_output()")
        print("      print(final)")

        print("\n--- Runnable: streaming with TestModel (no API key) ---")
        try:
            from pydantic_ai.models.test import TestModel

            async def run_stream_demo() -> None:
                with agent.override(model=TestModel()):
                    async with agent.run_stream("Summarize a short piece about renewable energy.") as result:
                        async for partial in result.stream_output(debounce_by=None):
                            print("  partial:", partial)
                        final = await result.get_output()
                        print("  final validated output:", final)

            await run_stream_demo()
        except Exception as e:
            print(f"Streaming demo failed ({type(e).__name__}: {e}).")
            print(
                "run_stream yields partial ArticleSummary instances as the model streams; "
                "get_output() returns the final validated model."
            )

        print("\n--- Optional: stream with live OpenAI ---")
        try:
            from pydantic_ai.models import infer_model

            live = infer_model("openai:gpt-4o-mini")

            async def run_live_stream() -> None:
                with agent.override(model=live):
                    async with agent.run_stream("2-sentence article about SQLite.") as result:
                        async for partial in result.stream_output(debounce_by=None):
                            print("  live partial:", partial)
                        print("  live final:", await result.get_output())

            await run_live_stream()
        except Exception as e:
            print(f"Skipping live streaming ({type(e).__name__}: {e}).")

    except ImportError:
        print("Install pydantic-ai: pip install pydantic-ai")


def main() -> None:
    import asyncio

    asyncio.run(demo_streaming())


if __name__ == "__main__":
    main()
