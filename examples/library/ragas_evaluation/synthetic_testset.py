# requires: ragas
"""RAGAS TestsetGenerator: diverse QA pairs from documents (concept + sample rows)."""

from __future__ import annotations


def main() -> None:
    print("RAGAS synthetic / augmented test sets from documents")
    print("-" * 60)

    documents = [
        "Feast is an open-source feature store for ML.",
        "Temporal provides durable workflow execution for distributed systems.",
        "RAGAS offers metrics for evaluating RAG and agent pipelines.",
    ]
    print("Sample source documents:")
    for i, d in enumerate(documents, 1):
        print(f"  {i}. {d}")

    print(
        "\nHow TestsetGenerator typically works:\n"
        "  - Chunk documents and optionally embed / cluster for diversity.\n"
        "  - Use an LLM to propose questions and reference answers per chunk.\n"
        "  - Filter or deduplicate so the final set covers multiple topics and styles.\n"
    )

    try:
        from ragas.testset import TestsetGenerator
    except ImportError:
        print(
            "TestsetGenerator import failed. Install with:\n"
            "  pip install ragas\n"
            "Print-only demo: no generator invoked (needs LLM + document loaders in practice)."
        )
        return

    print(f"TestsetGenerator class available: {TestsetGenerator}")
    print(
        "Typical construction (names vary by RAGAS version):\n"
        "  generator = TestsetGenerator.from_langchain(\n"
        "      llm=..., embedding_model=..., document_loader=...\n"
        "  )\n"
        "  testset = generator.generate_with_langchain_docs(docs, test_size=10)\n"
        "\nThis script stops short of calling generate_* without API keys and corpora.\n"
    )


if __name__ == "__main__":
    main()
