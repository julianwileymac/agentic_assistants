"""
State-machine orchestration primitives inspired by graph-based agent runtimes.
"""

from __future__ import annotations

import asyncio
import copy
import logging
from collections import defaultdict, deque
from typing import Any, AsyncIterator, Awaitable, Callable, Mapping, MutableMapping, Optional
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)

START = "__start__"
END = "__end__"

StateType = MutableMapping[str, Any]
NodeFn = Callable[[StateType], Mapping[str, Any] | Awaitable[Mapping[str, Any]]]


@runtime_checkable
class Checkpointer(Protocol):
    """Protocol for saving/loading graph state by graph id."""

    async def save(self, graph_id: str, state: Mapping[str, Any]) -> None:
        ...

    async def load(self, graph_id: str) -> Optional[dict[str, Any]]:
        ...


class InMemoryCheckpointer:
    """In-memory state checkpointer useful for tests and local runs."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    async def save(self, graph_id: str, state: Mapping[str, Any]) -> None:
        self._store[graph_id] = copy.deepcopy(dict(state))

    async def load(self, graph_id: str) -> Optional[dict[str, Any]]:
        saved = self._store.get(graph_id)
        return copy.deepcopy(saved) if saved is not None else None


@runtime_checkable
class StateNode(Protocol):
    """Protocol for graph nodes operating over shared mutable state."""

    async def __call__(self, state: StateType) -> Mapping[str, Any]:
        ...


class ConditionalEdge:
    """Routes from one node to another based on state-dependent keys."""

    def __init__(self, condition: Callable[[StateType], str], routes: dict[str, str]) -> None:
        self.condition = condition
        self.routes = routes

    def resolve(self, state: StateType) -> str:
        route_key = self.condition(state)
        if route_key not in self.routes:
            raise ValueError(
                f"Condition returned '{route_key}', valid routes are: {sorted(self.routes)}"
            )
        return self.routes[route_key]


def _merge_state(current: StateType, update: Mapping[str, Any]) -> StateType:
    merged = dict(current)
    for key, value in update.items():
        if key in merged and isinstance(merged[key], list) and isinstance(value, list):
            merged[key] = merged[key] + value
        else:
            merged[key] = value
    return merged


class StateMachine:
    """Builder object for creating executable state graphs."""

    def __init__(
        self,
        state_reducer: Optional[Callable[[StateType, Mapping[str, Any]], StateType]] = None,
    ) -> None:
        self._nodes: dict[str, NodeFn] = {}
        self._edges: dict[str, list[str]] = defaultdict(list)
        self._conditional_edges: dict[str, ConditionalEdge] = {}
        self._state_reducer = state_reducer or _merge_state

    def add_node(self, name: str, fn: NodeFn) -> StateMachine:
        if name in (START, END):
            raise ValueError(f"'{name}' is a reserved node name")
        self._nodes[name] = fn
        return self

    def add_edge(self, source: str, target: str) -> StateMachine:
        self._edges[source].append(target)
        return self

    def add_conditional_edge(
        self,
        source: str,
        condition: Callable[[StateType], str],
        routes: dict[str, str],
    ) -> StateMachine:
        self._conditional_edges[source] = ConditionalEdge(condition, routes)
        return self

    def set_entry_point(self, node_name: str) -> StateMachine:
        return self.add_edge(START, node_name)

    def set_finish_point(self, node_name: str) -> StateMachine:
        return self.add_edge(node_name, END)

    def compile(
        self,
        *,
        max_steps: int = 100,
        checkpointer: Optional[Checkpointer] = None,
    ) -> CompiledGraph:
        if START not in self._edges:
            raise ValueError("No entry point defined. Add an edge from START.")
        for name in self._nodes:
            if name not in self._edges and name not in self._conditional_edges:
                logger.debug("Node '%s' has no outgoing edges", name)
        return CompiledGraph(
            nodes=dict(self._nodes),
            edges=dict(self._edges),
            conditional_edges=dict(self._conditional_edges),
            state_reducer=self._state_reducer,
            max_steps=max_steps,
            checkpointer=checkpointer,
        )


class CompiledGraph:
    """Executable graph produced by StateMachine.compile()."""

    def __init__(
        self,
        *,
        nodes: dict[str, NodeFn],
        edges: dict[str, list[str]],
        conditional_edges: dict[str, ConditionalEdge],
        state_reducer: Callable[[StateType, Mapping[str, Any]], StateType],
        max_steps: int,
        checkpointer: Optional[Checkpointer] = None,
    ) -> None:
        self._nodes = nodes
        self._edges = edges
        self._conditional_edges = conditional_edges
        self._reducer = state_reducer
        self._max_steps = max_steps
        self._checkpointer = checkpointer

    def _next_nodes(self, current: str, state: StateType) -> list[str]:
        targets: list[str] = []
        if current in self._edges:
            targets.extend(self._edges[current])
        if current in self._conditional_edges:
            targets.append(self._conditional_edges[current].resolve(state))
        return targets

    async def _invoke_node(self, node_name: str, state: StateType) -> Mapping[str, Any]:
        fn = self._nodes.get(node_name)
        if fn is None:
            raise ValueError(f"Node '{node_name}' is not registered")

        if asyncio.iscoroutinefunction(fn):
            update = await fn(state)
        else:
            update = fn(state)
            if asyncio.iscoroutine(update):
                update = await update

        if not isinstance(update, Mapping):
            raise TypeError(
                f"Node '{node_name}' returned {type(update).__name__}; expected a mapping update"
            )
        return update

    async def _load_initial_state(
        self,
        initial_state: Mapping[str, Any],
        *,
        graph_id: Optional[str],
        resume: bool,
    ) -> StateType:
        state = dict(initial_state)
        if resume and graph_id and self._checkpointer is not None:
            checkpoint_state = await self._checkpointer.load(graph_id)
            if checkpoint_state is not None:
                state = self._reducer(checkpoint_state, state)
        state.setdefault("__steps__", [])
        return state

    async def _save_checkpoint(self, graph_id: Optional[str], state: StateType) -> None:
        if graph_id and self._checkpointer is not None:
            await self._checkpointer.save(graph_id, state)

    async def invoke(
        self,
        initial_state: Mapping[str, Any],
        *,
        graph_id: Optional[str] = None,
        resume: bool = False,
    ) -> dict[str, Any]:
        state = await self._load_initial_state(initial_state, graph_id=graph_id, resume=resume)
        queue: deque[str] = deque(self._next_nodes(START, state))
        steps = 0

        while queue:
            if steps >= self._max_steps:
                raise RuntimeError(
                    f"Graph exceeded max_steps={self._max_steps}. "
                    "Check for loops or increase max_steps."
                )

            node_name = queue.popleft()
            if node_name == END:
                await self._save_checkpoint(graph_id, state)
                return dict(state)

            update = await self._invoke_node(node_name, state)
            state = self._reducer(state, update)
            state["__steps__"].append(node_name)
            steps += 1
            await self._save_checkpoint(graph_id, state)
            queue.extend(self._next_nodes(node_name, state))

        return dict(state)

    async def stream(
        self,
        initial_state: Mapping[str, Any],
        *,
        graph_id: Optional[str] = None,
        resume: bool = False,
    ) -> AsyncIterator[dict[str, Any]]:
        state = await self._load_initial_state(initial_state, graph_id=graph_id, resume=resume)
        queue: deque[str] = deque(self._next_nodes(START, state))
        steps = 0

        while queue:
            if steps >= self._max_steps:
                raise RuntimeError(
                    f"Graph exceeded max_steps={self._max_steps}. "
                    "Check for loops or increase max_steps."
                )

            node_name = queue.popleft()
            if node_name == END:
                await self._save_checkpoint(graph_id, state)
                yield dict(state)
                return

            update = await self._invoke_node(node_name, state)
            state = self._reducer(state, update)
            state["__steps__"].append(node_name)
            steps += 1
            await self._save_checkpoint(graph_id, state)
            yield copy.deepcopy(state)
            queue.extend(self._next_nodes(node_name, state))

        yield dict(state)


__all__ = [
    "START",
    "END",
    "Checkpointer",
    "InMemoryCheckpointer",
    "StateNode",
    "ConditionalEdge",
    "StateMachine",
    "CompiledGraph",
]

