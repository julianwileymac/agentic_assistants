"""Multi-level storage demo."""

from agentic_assistants.observability.usage_tracker import UsageTracker
from agentic_assistants.vectordb.base import Document
from agentic_assistants.vectordb.scoped_store import ScopedVectorStore


def main() -> None:
    store = ScopedVectorStore(project_id="demo-project")
    tracker = UsageTracker()

    store.add(
        Document(
            id="intro",
            content="Multi-level storage combines vectors, artifacts, and analytics.",
            metadata={"source": "demo"},
        ),
        collection="knowledge",
    )

    results = store.search(
        "What is multi-level storage?",
        collection="knowledge",
        top_k=3,
        include_global=True,
        include_parent_scopes=True,
    )
    print(f"Results: {len(results)}")

    tracker.track_rag_query(
        knowledge_base="knowledge",
        query="What is multi-level storage?",
        num_results=len(results),
        duration_ms=5.0,
        used_for_generation=False,
        metadata={"template": "multilevel-storage-kb"},
    )
    print("Tracked usage event in SQLite.")


if __name__ == "__main__":
    main()

