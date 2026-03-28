"""
Shared type aliases, TypedDict schemas, and Protocol contracts.
"""

from __future__ import annotations

from typing import Any, Literal, Mapping, MutableMapping, Optional, Protocol, runtime_checkable

from typing_extensions import TypeAlias, TypedDict

JSON: TypeAlias = (
    dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
)

Embedding: TypeAlias = list[float]
Metadata: TypeAlias = dict[str, Any]
NodeInputs: TypeAlias = dict[str, Any]
NodeOutputs: TypeAlias = dict[str, Any]
ToolResult: TypeAlias = dict[str, Any]
ToolSpec: TypeAlias = dict[str, Any]
ModelName: TypeAlias = str
ProviderName: TypeAlias = str
CollectionName: TypeAlias = str
RunID: TypeAlias = str


class ChatMessage(TypedDict, total=False):
    """Chat message used by adapters and memory components."""

    role: str
    content: str
    name: str
    tool_calls: list[dict[str, Any]]
    tool_call_id: str


ChatHistory: TypeAlias = list[ChatMessage]


class TrainingState(TypedDict, total=False):
    """Training state snapshot."""

    epoch: int
    step: int
    loss: float
    learning_rate: float
    metrics: dict[str, float]


class EvalResult(TypedDict, total=False):
    """Evaluation result shape."""

    metric: str
    value: float
    threshold: Optional[float]
    passed: bool


class SkillPayload(TypedDict, total=False):
    """Payload passed into skill routing engines."""

    skill_name: str
    input_data: dict[str, Any]
    context: dict[str, Any]
    config: dict[str, Any]


ExecutionStatus: TypeAlias = Literal["pending", "running", "completed", "failed", "cancelled"]


class ExecutionResult(TypedDict, total=False):
    """Portable execution result for runners, flows, and adapters."""

    run_id: str
    status: ExecutionStatus
    outputs: NodeOutputs
    metrics: dict[str, float]
    error: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]


class AdapterRunMetadata(TypedDict, total=False):
    """Adapter run metadata used for tracing and experiment logging."""

    framework: str
    run_name: str
    agent_name: str
    model: str
    tags: dict[str, str]
    params: dict[str, Any]


@runtime_checkable
class DataCatalogProtocol(Protocol):
    """Minimal catalog contract used by pipeline runners."""

    def load(self, dataset_name: str) -> Any:
        ...

    def save(self, dataset_name: str, data: Any) -> None:
        ...


@runtime_checkable
class HookManagerProtocol(Protocol):
    """Minimal hook manager contract (pluggy-compatible)."""

    hook: Any


@runtime_checkable
class RunnableNodeProtocol(Protocol):
    """Minimal pipeline node contract used by runners."""

    name: str
    input_names: list[str]
    output_names: list[str]

    def run(self, inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        ...


@runtime_checkable
class MutableStateProtocol(Protocol):
    """Mapping-like state object used by graph executors."""

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def get(self, key: str, default: Any = None) -> Any:
        ...

    def update(self, other: Mapping[str, Any]) -> None:
        ...


StateMapping: TypeAlias = MutableMapping[str, Any]


__all__ = [
    "JSON",
    "Embedding",
    "Metadata",
    "NodeInputs",
    "NodeOutputs",
    "ToolResult",
    "ToolSpec",
    "ModelName",
    "ProviderName",
    "CollectionName",
    "RunID",
    "ChatMessage",
    "ChatHistory",
    "TrainingState",
    "EvalResult",
    "SkillPayload",
    "ExecutionStatus",
    "ExecutionResult",
    "AdapterRunMetadata",
    "DataCatalogProtocol",
    "HookManagerProtocol",
    "RunnableNodeProtocol",
    "MutableStateProtocol",
    "StateMapping",
]

