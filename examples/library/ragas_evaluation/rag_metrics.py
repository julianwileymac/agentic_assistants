# requires: ragas
"""RAGAS metrics: context_precision, context_recall, faithfulness, answer_relevancy."""

from __future__ import annotations


def main() -> None:
    print("RAGAS RAG metrics with evaluate() on a tiny sample dataset")
    print("-" * 60)
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
    except ImportError:
        print(
            "Missing dependency. Install with:\n"
            "  pip install ragas datasets\n"
            "(RAGAS may pull additional LLM-related dependencies.)"
        )
        return

    sample = {
        "question": [
            "What is the capital of France?",
            "Who wrote Romeo and Juliet?",
        ],
        "contexts": [
            ["Paris is the capital and largest city of France."],
            ["William Shakespeare wrote the play Romeo and Juliet."],
        ],
        "answer": [
            "The capital of France is Paris.",
            "Romeo and Juliet was written by Shakespeare.",
        ],
        "ground_truths": [
            "Paris is the capital of France.",
            "William Shakespeare wrote Romeo and Juliet.",
        ],
    }

    ds = Dataset.from_dict(sample)

    metrics = [context_precision, context_recall, faithfulness, answer_relevancy]
    print("Running evaluate() — may require configured LLM / embeddings in your environment.")
    try:
        result = evaluate(ds, metrics=metrics)
        print("Metric results:")
        print(result)
    except Exception as exc:
        print(f"evaluate() did not complete in this environment: {exc}")
        print("Expected pattern:")
        print("  from ragas import evaluate")
        print("  from datasets import Dataset")
        print("  result = evaluate(dataset, metrics=[context_precision, ...])")


if __name__ == "__main__":
    main()
