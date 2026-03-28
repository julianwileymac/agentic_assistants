# requires: agentic-assistants

"""End-to-end mock RAG evaluation using RAGAS-style metrics from core.evaluation."""

from __future__ import annotations

from typing import Any

try:
    from agentic_assistants.core.evaluation import (
        AnswerRelevance,
        ContextRelevance,
        ContextSufficiency,
        EvaluationResult,
        MetricTracker,
    )
except ImportError as exc:  # pragma: no cover
    _IMPORT_ERROR: ImportError | None = exc
else:
    _IMPORT_ERROR = None


if _IMPORT_ERROR is None:

    def _mock_retrieve(query: str, corpus: list[dict[str, str]]) -> str:
        q = query.lower().split()
        best = ""
        best_score = 0
        for doc in corpus:
            text = doc["text"].lower()
            score = sum(1 for t in q if t in text)
            if score > best_score:
                best_score = score
                best = doc["text"]
        return best or "(no context)"

    def _mock_generate(query: str, context: str) -> str:
        # Toy generator: echo key overlap as a fake answer
        words = [w for w in query.split() if len(w) > 3]
        hook = words[0] if words else "result"
        return f"Based on the context, {hook} relates to: {context[:80].strip()}..."

    def main() -> None:
        print("Mock RAG pipeline + RAGAS-style metrics (ContextRelevance, ContextSufficiency, AnswerRelevance)")
        print("-" * 60)

        corpus: list[dict[str, str]] = [
            {"id": "a1", "text": "Python asyncio enables concurrent I/O without threads."},
            {"id": "a2", "text": "Vector databases store embeddings for semantic search in RAG."},
            {"id": "a3", "text": "Temporal workflows are durable and survive process restarts."},
        ]
        queries: list[str] = [
            "How does asyncio help with concurrent Python?",
            "What is a vector database used for?",
            "Why are Temporal workflows durable?",
        ]

        ctx_rel = ContextRelevance()
        ctx_suf = ContextSufficiency()
        ans_rel = AnswerRelevance()
        tracker = MetricTracker(keep_values=False)

        per_case: list[dict[str, Any]] = []

        for query in queries:
            context = _mock_retrieve(query, corpus)
            answer = _mock_generate(query, context)

            cr = ctx_rel.record(query, context)
            cs = ctx_suf.record(answer, context)
            ar = ans_rel.record(query, answer)

            tracker.record("context_relevance", cr)
            tracker.record("context_sufficiency", cs)
            tracker.record("answer_relevance", ar)
            per_case.append(
                {
                    "query": query[:52] + "..." if len(query) > 52 else query,
                    "context_relevance": round(cr, 4),
                    "context_sufficiency": round(cs, 4),
                    "answer_relevance": round(ar, 4),
                }
            )

        result = EvaluationResult(
            context_relevance=ctx_rel,
            context_sufficiency=ctx_suf,
            answer_relevance=ans_rel,
        )

        print("\nPer-query scores:")
        for row in per_case:
            print(f"  q={row['query']!r}")
            print(
                f"    context_relevance={row['context_relevance']} "
                f"context_sufficiency={row['context_sufficiency']} "
                f"answer_relevance={row['answer_relevance']}"
            )

        print("\nAggregated report (EvaluationResult.summary):")
        for k, v in sorted(result.summary().items()):
            print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")

        print("\nMetricTracker means (cross-case):")
        for name in ("context_relevance", "context_sufficiency", "answer_relevance"):
            mv = tracker.get(name)
            print(f"  {name}: mean={mv.mean:.4f} (n={mv.count})")


else:

    def main() -> None:
        print("Install the project so `agentic_assistants` is importable, e.g. `poetry install`.")
        print("Import error:", _IMPORT_ERROR)


if __name__ == "__main__":
    main()
