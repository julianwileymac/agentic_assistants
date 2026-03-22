"""Multi-level storage starter."""

from agentic_assistants.observability.usage_tracker import UsageTracker
from agentic_assistants.vectordb.base import Document
from agentic_assistants.vectordb.scoped_store import ScopedVectorStore


def main() -> None:
    store = ScopedVectorStore(project_id="multilevel-storage-kb")
    tracker = UsageTracker()

    store.add(
        Document(id="seed", content="Storage tiers improve reliability."),
        collection="knowledge",
    )
    results = store.search(
        "Why use storage tiers?",
        collection="knowledge",
        top_k=3,
        include_global=True,
    )
    tracker.track_rag_query(
        knowledge_base="knowledge",
        query="Why use storage tiers?",
        num_results=len(results),
        duration_ms=10.0,
        used_for_generation=False,
    )
    print(f"Retrieved {len(results)} result(s).")


if __name__ == "__main__":
    main()

