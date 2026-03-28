# requires: deepeval
"""ContextualRelevancyMetric and AnswerRelevancyMetric for RAG."""

from __future__ import annotations


def main() -> None:
    print("DeepEval RAG metrics: contextual + answer relevancy")
    print("-" * 60)
    try:
        from deepeval.metrics import AnswerRelevancyMetric, ContextualRelevancyMetric
        from deepeval.test_case import LLMTestCase
    except ImportError:
        print(
            "Missing dependency. Install with:\n"
            "  pip install deepeval"
        )
        return

    cases = [
        LLMTestCase(
            input="What policy covers dental?",
            actual_output="The PPO plan includes basic dental coverage.",
            retrieval_context=[
                "Our PPO medical plan includes preventive dental visits twice per year.",
            ],
        ),
        LLMTestCase(
            input="What is the refund window?",
            actual_output="The sky is blue.",
            retrieval_context=[
                "Hardware may be returned within 30 days with receipt.",
            ],
        ),
    ]

    print("Sample RAG-style LLMTestCase rows (retrieval_context = retrieved chunks):")
    for i, c in enumerate(cases, 1):
        print(f"  {i}. Q={c.input!r} A={c.actual_output!r}")
        print(f"     retrieval_context={c.retrieval_context}")

    try:
        from deepeval import evaluate
    except ImportError:
        try:
            from deepeval.evaluate import evaluate
        except ImportError:
            print("Could not import evaluate() from deepeval.")
            return

    ctx_metric = ContextualRelevancyMetric(threshold=0.5)
    ans_metric = AnswerRelevancyMetric(threshold=0.5)

    try:
        results = evaluate(test_cases=cases, metrics=[ctx_metric, ans_metric])
        print("\nEvaluation output:")
        print(results)
    except Exception as exc:
        print(f"\nevaluate() failed in this environment: {exc}")
        print(
            "Without a configured judge model, scores are not produced here.\n"
            "Pattern: evaluate(test_cases=cases, metrics=[ContextualRelevancyMetric(), ...])"
        )


if __name__ == "__main__":
    main()
