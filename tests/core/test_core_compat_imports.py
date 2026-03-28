from __future__ import annotations

from agentic_assistants.core import BaseDTO, InMemoryRepository, ObservabilityManager, PaginatedResponse


def test_core_compat_exports() -> None:
    assert BaseDTO is not None
    assert InMemoryRepository is not None
    assert ObservabilityManager is not None
    assert PaginatedResponse is not None

