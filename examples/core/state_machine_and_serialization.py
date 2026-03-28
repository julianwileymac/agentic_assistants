from __future__ import annotations

import asyncio

from agentic_assistants.core.foundation import (
    END,
    START,
    InMemoryCheckpointer,
    StateMachine,
    get_serializer,
)


async def increment(state: dict[str, int]) -> dict[str, int]:
    return {"count": state.get("count", 0) + 1}


async def main() -> None:
    sm = StateMachine()
    sm.add_node("increment", increment)
    sm.add_edge(START, "increment")
    sm.add_edge("increment", END)

    graph = sm.compile(checkpointer=InMemoryCheckpointer())
    state = await graph.invoke({"count": 0}, graph_id="demo")

    serializer = get_serializer("json")
    encoded = serializer.encode(state)
    decoded = serializer.decode(encoded)

    print("State:", state)
    print("Encoded bytes:", encoded)
    print("Decoded:", decoded)


if __name__ == "__main__":
    asyncio.run(main())

