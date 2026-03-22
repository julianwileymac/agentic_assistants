"""Simple RAG retrieval evaluation runner."""

from agentic_assistants.vectordb.base import VectorStore


def main() -> None:
    store = VectorStore.create()
    queries = [
        "Where is CLI implemented?",
        "How do traces sync?",
    ]
    for q in queries:
        hits = store.search(q, collection="rag_eval", top_k=5)
        print({"query": q, "hits": len(hits), "top_score": hits[0].score if hits else 0.0})


if __name__ == "__main__":
    main()

