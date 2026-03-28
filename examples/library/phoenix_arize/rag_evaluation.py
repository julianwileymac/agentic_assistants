# requires: arize-phoenix

"""
RAG evaluation patterns with mock retrieval: relevance, faithfulness, and hallucination signals.

Builds a small tabular eval report (pandas if available) and shows how scores map to Phoenix
concepts (annotations / experiments). No live LLM or Phoenix server required.
"""

from __future__ import annotations


def _tokens(text: str) -> set[str]:
    return {t for t in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if t}


def relevance_score(query: str, contexts: list[str]) -> float:
    q = _tokens(query)
    if not q:
        return 0.0
    best = 0.0
    for doc in contexts:
        d = _tokens(doc)
        if not d:
            continue
        best = max(best, len(q & d) / len(q))
    return best


def faithfulness_score(answer: str, contexts: list[str]) -> float:
    a = _tokens(answer)
    if not a:
        return 1.0
    ctx = set().union(*(_tokens(c) for c in contexts)) if contexts else set()
    supported = len(a & ctx)
    return supported / len(a)


def hallucination_rate(answer: str, contexts: list[str]) -> float:
    a = _tokens(answer)
    if not a:
        return 0.0
    ctx = set().union(*(_tokens(c) for c in contexts)) if contexts else set()
    return len(a - ctx) / len(a)


def main() -> None:
    try:
        import phoenix as px
    except ImportError as exc:  # pragma: no cover
        print("Install arize-phoenix to run this example:", exc)
        return

    rows = [
        {
            "query": "What is the capital of France?",
            "reference": "Paris is the capital of France.",
            "response": "The capital of France is Paris.",
            "contexts": [
                "France is in Western Europe.",
                "Paris is the capital and largest city of France.",
            ],
        },
        {
            "query": "Who invented the telephone?",
            "reference": "Alexander Graham Bell is credited with the first practical telephone patent.",
            "response": "Thomas Edison invented the telephone in 1876.",
            "contexts": [
                "Bell filed his telephone patent in 1876.",
                "Early telephony experiments involved multiple inventors.",
            ],
        },
        {
            "query": "Define photosynthesis.",
            "reference": "Plants convert light into chemical energy.",
            "response": "Photosynthesis converts light energy into chemical energy in plants.",
            "contexts": [
                "Chloroplasts absorb light for photosynthesis.",
                "Plants produce oxygen during photosynthesis.",
            ],
        },
    ]

    print("=" * 60)
    print("Mock RAG eval (lexical proxies - replace with Phoenix evals / LLM judges in prod)")
    print("=" * 60)
    print(f"  phoenix import OK: {px.__name__} {getattr(px, '__version__', '')}".strip())

    try:
        import pandas as pd

        use_df = True
    except ImportError:
        use_df = False

    records: list[dict[str, object]] = []
    for r in rows:
        rel = relevance_score(r["query"], r["contexts"])
        faith = faithfulness_score(r["response"], r["contexts"])
        hall = hallucination_rate(r["response"], r["contexts"])
        records.append(
            {
                "query": r["query"],
                "relevance": round(rel, 3),
                "faithfulness": round(faith, 3),
                "hallucination_rate": round(hall, 3),
            }
        )

    if use_df:
        df = pd.DataFrame.from_records(records)
        print()
        print(df.to_string(index=False))
    else:
        for rec in records:
            print(rec)

    print()
    print("Phoenix-oriented workflow:")
    print("  1) Log traces with RETRIEVER + LLM spans (see llm_tracing.py).")
    print("  2) Export spans or join offline eval tables (relevance / faithfulness / hallucination).")
    print("  3) Use Phoenix datasets & experiments to compare prompts or retrieval settings.")
    print("  4) Swap lexical scores for phoenix.evals LLM-based evaluators when keys are available.")


if __name__ == "__main__":
    main()
