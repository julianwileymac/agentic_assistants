# requires: ragas
"""Custom RAGAS metric: subclass Metric, apply a rubric, run evaluate()."""

from __future__ import annotations


def main() -> None:
    print("Custom RAGAS metric: subclass + rubric + evaluate")
    print("-" * 60)
    try:
        from datasets import Dataset
        from ragas import evaluate
    except ImportError:
        print(
            "Missing dependency. Install with:\n"
            "  pip install ragas datasets"
        )
        return

    rows = {
        "question": ["Say hi politely.", "Give a blunt order."],
        "answer": ["Thank you for asking; hello!", "Do it now."],
    }
    print("Manual rubric (politeness): 1.0 if 'please' or 'thank you' in answer")
    print("Scores without RAGAS:", [_politeness_score(a) for a in rows["answer"]])

    MetricBase = None
    try:
        from ragas.metrics.base import Metric as MetricBase
    except ImportError:
        print(
            "\nCould not import ragas.metrics.base.Metric — API differs by version.\n"
            "Consult RAGAS docs for the Metric base class in your release.\n"
        )
        return

    class PolitenessMetric(MetricBase):
        """Example rubric metric: politeness keywords in the answer."""

        name = "politeness_rubric"

        def init(self, **kwargs):  # noqa: ARG002
            return None

        async def _single_turn_ascore(self, sample, callbacks):  # noqa: ARG002
            ans = getattr(sample, "response", None) or getattr(sample, "answer", "") or ""
            text = str(ans).lower()
            return 1.0 if ("please" in text or "thank you" in text) else 0.0

    ds = Dataset.from_dict(rows)
    custom = PolitenessMetric()
    print(f"\nTrying evaluate() with {custom.name!r} ...")
    try:
        result = evaluate(ds, metrics=[custom])
        print(result)
    except Exception as exc:
        print(f"evaluate() failed (Metric interface may differ in your RAGAS version): {exc}")


def _politeness_score(answer: str) -> float:
    t = answer.lower()
    return 1.0 if ("please" in t or "thank you" in t) else 0.0


if __name__ == "__main__":
    main()
