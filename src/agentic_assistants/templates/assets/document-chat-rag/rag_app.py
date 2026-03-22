"""Minimal local document RAG app."""

from agentic_assistants.patterns.rag_pattern import RAGPattern
from agentic_assistants.vectordb.base import VectorStore


def main() -> None:
    store = VectorStore.create()
    rag = RAGPattern(vector_store=store, collection="docs", top_k=5)

    print("Ask questions about your indexed docs. Type 'exit' to quit.")
    while True:
        query = input("query> ").strip()
        if not query or query.lower() == "exit":
            break
        result = rag.query(query)
        print(f"\n{result.output}\n")


if __name__ == "__main__":
    main()

