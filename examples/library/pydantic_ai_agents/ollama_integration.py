# requires: pydantic-ai pydantic httpx
"""PydanticAI with local Ollama models.

Demonstrates:
- Configuring PydanticAI to use a local Ollama instance
- Structured extraction from local LLM
- Model selection for different tasks
"""

from __future__ import annotations

import os

from pydantic import BaseModel, Field


class CodeReview(BaseModel):
    """Structured code review from an LLM."""

    file_path: str
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    quality_score: int = Field(ge=1, le=10, description="1=terrible, 10=excellent")
    complexity: str = Field(description="low, medium, or high")
    security_concerns: list[str] = Field(default_factory=list)


class EntityExtraction(BaseModel):
    """Named entities extracted from text."""

    persons: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    monetary_amounts: list[str] = Field(default_factory=list)


def demo_ollama_agents():
    """Show PydanticAI agents configured for local Ollama."""
    try:
        from pydantic_ai import Agent

        # Use Ollama with a specific model
        review_agent: Agent[None, CodeReview] = Agent(
            "ollama:codellama",
            output_type=CodeReview,
            system_prompt="You are an expert code reviewer. Analyze the provided code.",
            defer_model_check=True,
        )

        # Use a smaller model for quick extraction tasks
        ner_agent: Agent[None, EntityExtraction] = Agent(
            "ollama:llama3.2",
            output_type=EntityExtraction,
            system_prompt="Extract named entities from the provided text.",
            defer_model_check=True,
        )

        print("Ollama-backed agents configured:")
        print(f"  Code review agent: ollama:codellama")
        print(f"  NER agent: ollama:llama3.2")
        print()
        print("Ensure Ollama is running: ollama serve")
        print("Pull required models: ollama pull codellama && ollama pull llama3.2")
        print()
        print("CodeReview schema:", CodeReview.model_json_schema())
        print("EntityExtraction schema:", EntityExtraction.model_json_schema())

        ollama_base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
        os.environ.setdefault("OLLAMA_BASE_URL", ollama_base)
        print()
        print(f"OLLAMA_BASE_URL (for pydantic-ai Ollama provider): {ollama_base}")

        print("\n--- Wire up Ollama model objects (infer_model) ---")
        try:
            from pydantic_ai.models import infer_model

            for spec in ("ollama:llama3.2", "ollama:codellama"):
                try:
                    model = infer_model(spec)
                    name = getattr(model, "model_name", spec)
                    print(f"  infer_model({spec!r}) -> {type(model).__name__} (model_name={name!r})")
                except Exception as e:
                    print(f"  infer_model({spec!r}) failed ({type(e).__name__}: {e})")
        except Exception as e:
            print(f"  Could not import infer_model ({type(e).__name__}: {e}).")

        print("\n--- Ollama HTTP reachability (/api/tags) ---")
        try:
            import httpx

            resp = httpx.get(f"{ollama_base}/api/tags", timeout=3.0)
            resp.raise_for_status()
            data = resp.json()
            names = [m.get("name", "") for m in data.get("models", [])]
            print(f"Ollama responded OK; {len(names)} model(s) reported (showing up to 5): {names[:5]}")
        except Exception as e:
            print(f"Could not reach Ollama ({type(e).__name__}: {e}).")
            print("Start the daemon with: ollama serve")

        print("\n--- Optional: run NER agent against a live Ollama model ---")
        try:
            from pydantic_ai.models import infer_model

            live_ner = infer_model("ollama:llama3.2")
            with ner_agent.override(model=live_ner):
                ner_result = ner_agent.run_sync(
                    "Alice Johnson met Bob at OpenAI in San Francisco on March 1, 2026. "
                    "They discussed a $2.5M contract."
                )
            print("Entity extraction:", ner_result.output)
        except Exception as e:
            print(f"Skipping live Ollama run ({type(e).__name__}: {e}).")
            print("Pull a model first, e.g.: ollama pull llama3.2")

        print("\n--- Optional: code review agent (often slower / larger model) ---")
        try:
            from pydantic_ai.models import infer_model

            live_review = infer_model("ollama:codellama")
            sample = "def add(a, b):\n    return a + b\n"
            with review_agent.override(model=live_review):
                review_result = review_agent.run_sync(f"Review this Python:\n{sample}")
            print("Code review:", review_result.output)
        except Exception as e:
            print(f"Skipping codellama run ({type(e).__name__}: {e}).")

    except ImportError:
        print("Install pydantic-ai and httpx: pip install pydantic-ai httpx")


def main() -> None:
    """Run the Ollama + PydanticAI example."""
    demo_ollama_agents()


if __name__ == "__main__":
    main()
