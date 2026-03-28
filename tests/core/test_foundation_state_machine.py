from __future__ import annotations

import pytest

from agentic_assistants.core.foundation import (
    END,
    START,
    InMemoryCheckpointer,
    StateMachine,
)


@pytest.mark.asyncio
async def test_state_machine_invoke_with_checkpoint() -> None:
    async def step(state):
        return {"counter": state.get("counter", 0) + 1}

    machine = StateMachine()
    machine.add_node("step", step)
    machine.add_edge(START, "step")
    machine.add_edge("step", END)

    graph = machine.compile(checkpointer=InMemoryCheckpointer())
    result = await graph.invoke({"counter": 0}, graph_id="g1")
    assert result["counter"] == 1
    assert result["__steps__"] == ["step"]


@pytest.mark.asyncio
async def test_state_machine_conditional_edge() -> None:
    async def choose(state):
        return {"route": "left"}

    async def left(state):
        return {"outcome": "ok"}

    machine = StateMachine()
    machine.add_node("choose", choose)
    machine.add_node("left", left)
    machine.add_edge(START, "choose")
    machine.add_conditional_edge("choose", lambda s: s["route"], {"left": "left"})
    machine.add_edge("left", END)

    graph = machine.compile()
    result = await graph.invoke({})
    assert result["outcome"] == "ok"

