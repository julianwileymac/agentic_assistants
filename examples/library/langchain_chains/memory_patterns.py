# requires: langchain langchain-core
"""Memory: ConversationBufferMemory (classic chain) and RunnableWithMessageHistory (LCEL).

Uses FakeListChatModel for deterministic replies without API keys.
"""

from __future__ import annotations


def main() -> None:
    try:
        from langchain_core.language_models.fake import FakeListChatModel
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.runnables.history import RunnableWithMessageHistory
        from langchain_core.chat_history import InMemoryChatMessageHistory
    except ImportError:
        print("Install: pip install langchain langchain-core")
        return

    llm = FakeListChatModel(responses=["Nice to meet you, Dana.", "Your name is Dana."])

    # --- Pattern A: RunnableWithMessageHistory (preferred LCEL) ---
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Remember the user's name if they say it."),
            MessagesPlaceholder("history"),
            ("human", "{input}"),
        ]
    )
    base_chain = prompt | llm

    store: dict[str, InMemoryChatMessageHistory] = {}

    def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    with_history = RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    cfg = {"configurable": {"session_id": "user-123"}}

    print("=== RunnableWithMessageHistory ===")
    r1 = with_history.invoke({"input": "My name is Dana."}, config=cfg)
    print("turn 1:", r1)
    r2 = with_history.invoke({"input": "What is my name?"}, config=cfg)
    print("turn 2:", r2)

    # --- Pattern B: ConversationBufferMemory + ConversationChain (langchain package) ---
    try:
        from langchain.chains import ConversationChain
        from langchain.memory import ConversationBufferMemory
    except ImportError as exc:
        print(f"\n(Skipping ConversationBufferMemory demo: {exc})")
        return

    memory = ConversationBufferMemory(return_messages=True)
    classic = ConversationChain(llm=llm, memory=memory, verbose=False)

    print("\n=== ConversationBufferMemory + ConversationChain ===")
    print(classic.invoke({"input": "I like Python."}))
    print(classic.invoke({"input": "What did I just say I like?"}))


if __name__ == "__main__":
    main()
