"""Local RAG Studio starter."""

from agentic_assistants.patterns.rag_pattern import RAGPattern
from agentic_assistants.vectordb.base import VectorStore


def main() -> None:
    store = VectorStore.create(backend="lancedb")
    rag = RAGPattern(vector_store=store, collection="local_rag_studio", top_k=5)
    print("Local RAG Studio. Type 'exit' to stop.")
    while True:
        q = input("query> ").strip()
        if not q or q.lower() == "exit":
            break
        result = rag.query(q)
        print(f"\n{result.output}\n")


if __name__ == "__main__":
    main()

