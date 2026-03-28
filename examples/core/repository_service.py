from __future__ import annotations

import asyncio

from agentic_assistants.core.foundation import AgenticAuditEntity, AuditedService, InMemoryRepository


class Task(AgenticAuditEntity):
    title: str
    status: str = "open"


async def main() -> None:
    repo = InMemoryRepository(Task)
    service = AuditedService(repo, current_user="julian")

    created = await service.create(Task(title="Implement foundation layer"))
    updated = await service.update(created.id, {"status": "done"})
    items = await service.list()

    print("Created:", created)
    print("Updated:", updated)
    print("Count:", len(items))


if __name__ == "__main__":
    asyncio.run(main())

