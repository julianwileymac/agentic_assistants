from __future__ import annotations

import pytest

from agentic_assistants.core.foundation import (
    AgenticAuditEntity,
    AuditedService,
    FilterSpec,
    InMemoryRepository,
    SortSpec,
)


class Task(AgenticAuditEntity):
    title: str
    status: str = "open"


@pytest.mark.asyncio
async def test_in_memory_repository_and_service() -> None:
    repo = InMemoryRepository(Task)
    service = AuditedService(repo, current_user="tester")

    created = await service.create(Task(title="one"))
    assert created.created_by == "tester"

    updated = await service.update(created.id, {"status": "done"})
    assert updated is not None
    assert updated.status == "done"
    assert updated.updated_by == "tester"

    rows = await service.list(
        filters=[FilterSpec(field="status", op="eq", value="done")],
        sort=[SortSpec(field="title")],
    )
    assert len(rows) == 1
    assert rows[0].title == "one"

