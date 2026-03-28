# requires: langchain langchain-core
"""Output parsers: PydanticOutputParser, JsonOutputParser, StrOutputParser with a stub LLM.

FakeListChatModel returns canned JSON / text matching each parser.
"""

from __future__ import annotations

from typing import Literal


def main() -> None:
    try:
        from langchain_core.language_models.fake import FakeListChatModel
        from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser, StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from pydantic import BaseModel, Field
    except ImportError:
        print("Install: pip install langchain langchain-core pydantic")
        return

    class Person(BaseModel):
        name: str = Field(description="Full name")
        role: Literal["engineer", "manager", "other"] = Field(description="Job role bucket")

    class Ticket(BaseModel):
        id: int = Field(description="Ticket id")
        severity: Literal["low", "med", "high"] = Field(description="Severity")

    # --- StrOutputParser: plain text ---
    llm_text = FakeListChatModel(responses=["hello world"])
    text_chain = ChatPromptTemplate.from_template("Say hi: {x}") | llm_text | StrOutputParser()
    print("=== StrOutputParser ===")
    print(text_chain.invoke({"x": "briefly"}))

    # --- PydanticOutputParser: typed extraction ---
    parser_p = PydanticOutputParser(pydantic_object=Person)
    fmt = parser_p.get_format_instructions()
    llm_p = FakeListChatModel(
        responses=['{"name": "Alex Rivera", "role": "engineer"}'],
    )
    chain_p = (
        ChatPromptTemplate.from_template(
            "Extract a person.\n{format_instructions}\nText: {text}\n"
        ).partial(format_instructions=fmt)
        | llm_p
        | parser_p
    )
    print("\n=== PydanticOutputParser ===")
    print(chain_p.invoke({"text": "Alex Rivera joined as a senior engineer."}))

    # --- JsonOutputParser: pydantic-shaped JSON ---
    parser_j = JsonOutputParser(pydantic_object=Ticket)
    fmt_j = parser_j.get_format_instructions()
    llm_j = FakeListChatModel(responses=['{"id": 42, "severity": "high"}'])
    chain_j = (
        ChatPromptTemplate.from_template(
            "Return JSON only for this schema.\n{format_instructions}\nInput: {input}\n"
        ).partial(format_instructions=fmt_j)
        | llm_j
        | parser_j
    )
    print("\n=== JsonOutputParser ===")
    print(chain_j.invoke({"input": "Ticket forty-two is high severity."}))


if __name__ == "__main__":
    main()
