# requires: marvin openai
"""Marvin @ai_classifier for enum-based classification.

Demonstrates:
- Enum classification with natural language input
- Sentiment, intent, and topic classification
"""

from __future__ import annotations

from enum import Enum


class Sentiment(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Intent(Enum):
    QUESTION = "question"
    COMPLAINT = "complaint"
    PRAISE = "praise"
    REQUEST = "request"
    INFORMATION = "information"


class Topic(Enum):
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    BUSINESS = "business"
    HEALTH = "health"
    ENTERTAINMENT = "entertainment"
    SPORTS = "sports"


def demo_classifiers():
    """Run marvin.classify on sample strings with graceful fallback."""
    try:
        import marvin
    except ImportError:
        print("Install: pip install marvin openai")
        print()
        print("Classifier enums defined:")
        for cls in (Sentiment, Intent, Topic):
            print(f"  {cls.__name__}: {[e.value for e in cls]}")
        print()
        print("Usage: marvin.classify('your text', labels=Sentiment)")
        return

    samples: list[tuple[str, type[Enum]]] = [
        ("I absolutely love this new feature!", Sentiment),
        ("Why is my bill wrong again?", Intent),
        ("The new GPU architecture doubles throughput.", Topic),
    ]

    print("--- marvin.classify attempts ---")
    for text, labels in samples:
        try:
            result = marvin.classify(text, labels=labels)
            print(f"  {labels.__name__}: {result!r} for {text!r}")
        except Exception as exc:
            print(f"  {labels.__name__}: failed ({type(exc).__name__}: {exc})")
            print(f"    Text was: {text!r}")
            if labels is Sentiment:
                print("    Example fallback label: Sentiment.POSITIVE")
            elif labels is Intent:
                print("    Example fallback label: Intent.COMPLAINT")
            else:
                print("    Example fallback label: Topic.TECHNOLOGY")


def main() -> None:
    """Run marvin.classify samples with offline fallback hints."""
    demo_classifiers()


if __name__ == "__main__":
    main()
