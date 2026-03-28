# requires: deepeval
"""HallucinationMetric and FaithfulnessMetric with grounded context."""

from __future__ import annotations


def main() -> None:
    print("DeepEval: HallucinationMetric + FaithfulnessMetric")
    print("-" * 60)
    try:
        from deepeval.metrics import FaithfulnessMetric, HallucinationMetric
        from deepeval.test_case import LLMTestCase
    except ImportError:
        print(
            "Missing dependency. Install with:\n"
            "  pip install deepeval"
        )
        return

    grounded = LLMTestCase(
        input="Who founded the company?",
        actual_output="Jane Doe founded Acme Corp in 2010.",
        context=["Acme Corp was founded by Jane Doe in 2010."],
    )
    drifting = LLMTestCase(
        input="Who founded the company?",
        actual_output="Elon Musk founded Acme Corp on Mars in 2099.",
        context=["Acme Corp was founded by Jane Doe in 2010."],
    )

    for label, tc in ("grounded", grounded), ("hallucination-prone", drifting):
        print(f"\nCase [{label}]:")
        print(f"  context: {tc.context}")
        print(f"  actual_output: {tc.actual_output!r}")

    try:
        from deepeval import evaluate
    except ImportError:
        try:
            from deepeval.evaluate import evaluate
        except ImportError:
            print("Could not import evaluate() from deepeval.")
            return

    hall = HallucinationMetric(threshold=0.5)
    faith = FaithfulnessMetric(threshold=0.5)
    print(
        "\nThese metrics are LLM-as-judge by default and need a configured judge model / API.\n"
        "Running evaluate() where possible...\n"
    )
    try:
        results = evaluate(test_cases=[grounded, drifting], metrics=[hall, faith])
        print(results)
    except Exception as exc:
        print(f"evaluate() failed in this environment: {exc}")
        print("Expected usage: evaluate(test_cases=[...], metrics=[HallucinationMetric(), ...])")


if __name__ == "__main__":
    main()
