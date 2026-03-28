# requires: marvin prefect pydantic openai
"""Marvin + Prefect integration for intelligent data pipelines.

Demonstrates:
- Using Marvin AI functions inside Prefect flows
- Combining orchestration with AI-powered processing
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProcessedRecord(BaseModel):
    original: str
    sentiment: float = 0.0
    category: str = ""
    summary: str = ""


def _offline_analyze(text: str) -> ProcessedRecord:
    """Deterministic stand-in when Marvin cannot run."""
    lowered = text.lower()
    if "great" in lowered or "love" in lowered:
        sentiment = 0.7
        category = "praise"
    elif "terrible" in lowered or "waited" in lowered:
        sentiment = -0.6
        category = "complaint"
    else:
        sentiment = 0.0
        category = "neutral"
    summary = text[:80] + ("…" if len(text) > 80 else "")
    return ProcessedRecord(
        original=text,
        sentiment=sentiment,
        category=category,
        summary=summary,
    )


def demo_integration():
    """Define and optionally run a Marvin + Prefect flow."""
    try:
        import marvin
        from prefect import flow, task
    except ImportError:
        print("Install: pip install marvin prefect openai")
        return

    @task
    def fetch_records() -> list[str]:
        return [
            "Great product! Love the new features.",
            "Terrible service, waited 3 hours.",
            "Average experience, nothing special.",
        ]

    @task
    def analyze_record(text: str) -> ProcessedRecord:
        sentiment = marvin.cast(
            text,
            target=float,
            instructions="Return a sentiment score from -1 (negative) to 1 (positive).",
        )
        category = marvin.classify(text, labels=["praise", "complaint", "neutral"])
        summary = marvin.cast(
            text,
            target=str,
            instructions="Single concise sentence summary.",
        )
        return ProcessedRecord(
            original=text,
            sentiment=sentiment,
            category=str(category),
            summary=summary,
        )

    @flow(name="ai-powered-etl")
    def ai_pipeline():
        records = fetch_records()
        return [analyze_record(r) for r in records]

    print("Marvin + Prefect integration pattern defined.")
    print("  Flow: ai-powered-etl")
    print("  Tasks: fetch_records -> analyze_record (per record)")
    print("\n--- Running flow (requires Marvin + API access) ---")
    try:
        results = ai_pipeline()
        for rec in results:
            print(" ", rec.model_dump())
    except Exception as exc:
        print(f"Flow run failed ({type(exc).__name__}: {exc}).")
        print("Offline deterministic preview:")
        for text in [
            "Great product! Love the new features.",
            "Terrible service, waited 3 hours.",
            "Average experience, nothing special.",
        ]:
            print(" ", _offline_analyze(text).model_dump())


def main() -> None:
    """Run the Prefect + Marvin flow, or print deterministic record previews."""
    demo_integration()


if __name__ == "__main__":
    main()
