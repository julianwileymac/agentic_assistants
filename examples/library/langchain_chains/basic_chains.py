# requires: langchain langchain-core
"""LCEL composition: RunnablePassthrough, RunnableLambda, and the `|` pipe operator.

Uses FakeListChatModel so chains run with no API keys.
"""

from __future__ import annotations


def main() -> None:
    try:
        from langchain_core.language_models.fake import FakeListChatModel
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
    except ImportError:
        print("Install: pip install langchain langchain-core")
        return

    # One canned reply per chain that invokes this LLM (FakeListChatModel cycles).
    llm = FakeListChatModel(
        responses=[
            "Paris is the capital of France.",
            "Brussels is one capital city in the European Union.",
        ]
    )

    # Pattern 1: prompt | model | parser (simple sequential pipe)
    prompt_geo = ChatPromptTemplate.from_messages(
        [("system", "Answer in one short sentence."), ("human", "{country}")]
    )
    chain_geo = prompt_geo | llm | StrOutputParser()
    out1 = chain_geo.invoke({"country": "What is the capital of France?"})
    print("=== Pattern 1: prompt | llm | StrOutputParser ===")
    print(out1)

    # Pattern 2: RunnablePassthrough with extra keys (dict in, dict out)
    enrich = RunnablePassthrough.assign(
        word_count=RunnableLambda(lambda d: len(d["text"].split())),
    )
    upper = RunnableLambda(lambda d: {**d, "shout": d["text"].upper()})
    chain_enrich = enrich | upper
    print("\n=== Pattern 2: RunnablePassthrough.assign + RunnableLambda ===")
    print(chain_enrich.invoke({"text": "hello chain world"}))

    # Pattern 3: RunnableParallel fan-out, then merge
    parallel = RunnableParallel(
        summary=RunnableLambda(lambda x: f"len={len(x['q'])}"),
        echo=RunnableLambda(lambda x: x["q"]),
    )
    print("\n=== Pattern 3: RunnableParallel ===")
    print(parallel.invoke({"q": "parallel inputs"}))

    # Pattern 4: branch with passthrough and lambda (multi-step without LLM on second branch)
    def prepend_topic(d: dict) -> dict:
        return {"prompt": f"Topic: {d['topic']}\nQuestion: {d['question']}"}

    prompt_qa = ChatPromptTemplate.from_template("{prompt}")
    branch = (
        RunnableLambda(prepend_topic)
        | prompt_qa
        | llm
        | StrOutputParser()
    )
    print("\n=== Pattern 4: Lambda reshaping before prompt | llm ===")
    print(branch.invoke({"topic": "geography", "question": "Name one EU capital."}))


if __name__ == "__main__":
    main()
