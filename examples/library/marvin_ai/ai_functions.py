# requires: marvin openai
"""Marvin @ai_fn for AI-powered utility functions.

Demonstrates:
- Decorating functions with @ai_fn
- Function signature drives AI behavior
- Sentiment, summarization, translation use cases
"""

from __future__ import annotations


def demo_ai_functions():
    """Register Marvin @marvin.fn helpers and attempt real invocations."""
    try:
        import marvin
    except ImportError:
        print("Install: pip install marvin openai")
        print()
        print("Pattern: decorate functions with @marvin.fn")
        print("The function signature + docstring tell the AI what to do.")
        print("The function body is empty - AI provides the implementation.")
        return

    @marvin.fn
    def sentiment(text: str) -> float:
        """Return sentiment score from -1.0 (negative) to 1.0 (positive)."""

    @marvin.fn
    def summarize(text: str, max_words: int = 50) -> str:
        """Summarize the text in at most max_words words."""

    @marvin.fn
    def translate(text: str, target_language: str = "Spanish") -> str:
        """Translate the text to the target language."""

    @marvin.fn
    def extract_keywords(text: str, count: int = 5) -> list[str]:
        """Extract the most important keywords from the text."""

    print("Marvin AI Functions registered:")
    for fn in (sentiment, summarize, translate, extract_keywords):
        print(f"  {fn.__name__}: {fn.__doc__}")

    sample = (
        "This release is fantastic; it fixed every pain point we had with onboarding. "
        "The new dashboard loads in under a second."
    )
    long_text = (
        "Marvin lets you treat LLM calls like normal Python. "
        "You declare types and docstrings; the framework handles prompting. "
        "It pairs well with Pydantic for structured outputs."
    )

    print("\n--- Invocation attempts (need OPENAI_API_KEY) ---")

    for label, call in [
        ("sentiment", lambda: sentiment(sample)),
        ("summarize", lambda: summarize(long_text, max_words=20)),
        ("translate", lambda: translate("Good morning, team!", target_language="French")),
        ("extract_keywords", lambda: extract_keywords(long_text, count=4)),
    ]:
        try:
            out = call()
            print(f"  {label}: {out!r}")
        except Exception as exc:
            print(f"  {label}: skipped ({type(exc).__name__}: {exc})")
            if label == "sentiment":
                print("    Example offline: ~0.85 for clearly positive product text.")
            elif label == "summarize":
                print(
                    "    Example offline: 'Marvin wraps LLM calls as typed Python; "
                    "works with Pydantic.'"
                )
            elif label == "translate":
                print("    Example offline: 'Bonjour à toute l'équipe !'")
            else:
                print("    Example offline: ['Marvin', 'Pydantic', 'LLM', 'Python']")


def main() -> None:
    """Register @marvin.fn helpers and attempt live calls with graceful fallback."""
    demo_ai_functions()


if __name__ == "__main__":
    main()
