# requires: langchain langchain-core
"""RAG-style LCEL chain: mock retriever, prompt template, StrOutputParser.

No vector DB or embeddings — retriever returns fixed Documents from the query string.
"""

from __future__ import annotations

def main() -> None:
    try:
        from langchain_core.documents import Document
        from langchain_core.language_models.fake import FakeListChatModel
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.runnables import RunnableLambda, RunnablePassthrough
    except ImportError:
        print("Install: pip install langchain langchain-core")
        return

    def mock_retriever(query: str) -> list[Document]:
        return [
            Document(
                page_content="The project deadline is Friday. Owner: Ops team.",
                metadata={"source": "wiki"},
            ),
            Document(
                page_content="Deployments must pass CI before merge.",
                metadata={"source": "runbook"},
            ),
            Document(
                page_content=f"Keyword hit for query: {query!r}",
                metadata={"source": "synthetic"},
            ),
        ]

    def format_docs(docs: list[Document]) -> str:
        return "\n\n".join(f"[{d.metadata.get('source', '?')}] {d.page_content}" for d in docs)

    retrieve_context = (
        RunnableLambda(lambda d: d["question"])
        | RunnableLambda(lambda q: mock_retriever(q))
        | RunnableLambda(format_docs)
    )

    rag_prompt = ChatPromptTemplate.from_template(
        "Use only the context to answer.\n\nContext:\n{context}\n\nQuestion: {question}"
    )

    llm = FakeListChatModel(
        responses=[
            "According to the context, the deadline is Friday and the owner is the Ops team."
        ]
    )

    chain = (
        RunnablePassthrough.assign(context=retrieve_context)
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    print("=== RAG LCEL structure ===")
    print(chain.invoke({"question": "When is the deadline and who owns it?"}))


if __name__ == "__main__":
    main()
