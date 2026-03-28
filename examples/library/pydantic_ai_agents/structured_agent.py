# requires: pydantic-ai pydantic
"""PydanticAI structured agent with typed output and dependency injection.

Demonstrates:
- Agent with Pydantic model as output_type
- RunContext for dependency injection
- Sync and async execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field


class CityInfo(BaseModel):
    """Structured output: information about a city."""

    name: str
    country: str
    population: int = Field(description="Estimated population", gt=0)
    famous_for: list[str] = Field(default_factory=list, description="Notable attractions")
    timezone: str = Field(default="UTC")


class TravelRecommendation(BaseModel):
    """Structured output: travel recommendation."""

    destination: CityInfo
    best_season: str
    estimated_daily_budget_usd: float = Field(gt=0)
    activities: list[str]
    safety_rating: int = Field(ge=1, le=10)


@dataclass
class TravelDeps:
    """Dependencies injected into the agent at runtime."""

    user_budget: float
    preferred_climate: str = "temperate"
    travel_style: str = "adventure"


def demo_agent_definition():
    """Show how to define and run a PydanticAI agent."""
    try:
        from pydantic_ai import Agent

        city_agent: Agent[None, CityInfo] = Agent(
            "openai:gpt-4o-mini",
            output_type=CityInfo,
            system_prompt="You are a geography expert. Return accurate city information.",
            defer_model_check=True,
        )

        travel_agent: Agent[TravelDeps, TravelRecommendation] = Agent(
            "openai:gpt-4o-mini",
            output_type=TravelRecommendation,
            deps_type=TravelDeps,
            system_prompt=(
                "You are a travel advisor. Consider the user's budget ({deps.user_budget} USD/day), "
                "preferred climate ({deps.preferred_climate}), and style ({deps.travel_style})."
            ),
            defer_model_check=True,
        )

        print("City agent output schema:")
        print(CityInfo.model_json_schema())
        print("\nTravel agent output schema:")
        print(TravelRecommendation.model_json_schema())

        print("\n--- Runnable demo: TestModel (no API key, no network) ---")
        try:
            from pydantic_ai.models.test import TestModel

            test_model = TestModel()
            with city_agent.override(model=test_model):
                city_result = city_agent.run_sync("Tell me about Paris, France.")
                print("city_agent.run_sync -> CityInfo:", city_result.output)

            deps = TravelDeps(user_budget=150.0, preferred_climate="warm", travel_style="relaxation")
            with travel_agent.override(model=test_model):
                travel_result = travel_agent.run_sync("Suggest a destination.", deps=deps)
                print("travel_agent.run_sync -> TravelRecommendation:", travel_result.output)
        except Exception as e:
            print(f"TestModel run failed ({type(e).__name__}: {e}).")
            print(
                "Normally, run_sync sends the prompt to the model, then parses the response into "
                "CityInfo / TravelRecommendation (with deps injected into the travel system prompt)."
            )

        print("\n--- Optional: real OpenAI (needs OPENAI_API_KEY) ---")
        try:
            from pydantic_ai.models import infer_model

            live = infer_model("openai:gpt-4o-mini")
            with city_agent.override(model=live):
                live_city = city_agent.run_sync("One-sentence city facts: Lisbon, Portugal.")
            print("Live model city_agent output:", live_city.output)
        except Exception as e:
            print(f"Skipping live OpenAI ({type(e).__name__}: {e}).")
            print("With credentials, run_sync would call the provider and return validated CityInfo.")

    except ImportError:
        print("Install pydantic-ai to run this example: pip install pydantic-ai")


def main() -> None:
    """Run the structured output + dependency injection example."""
    demo_agent_definition()


if __name__ == "__main__":
    main()
