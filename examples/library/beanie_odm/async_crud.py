# requires: beanie motor pydantic
"""Beanie async CRUD operations.

Demonstrates:
- insert, insert_many
- find_one, find_all
- replace, update with operators
- delete
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from pydantic import Field


def demo_crud():
    try:
        from beanie import Document, Indexed, init_beanie

        class Task(Document):
            class Settings:
                name = "tasks"

            title: Indexed(str)
            completed: bool = False
            priority: int = Field(ge=1, le=5, default=3)
            created_at: datetime = Field(default_factory=datetime.utcnow)

        print("Beanie CRUD — init_beanie wiring (production):")
        print("  client = AsyncIOMotorClient('mongodb://localhost:27017')")
        print("  await init_beanie(database=client.mydb, document_models=[Task])")
        print()

        async def _run() -> None:
            client = None
            db_name = "beanie_async_crud_demo"
            try:
                from mongomock_motor import AsyncMongoMockClient

                client = AsyncMongoMockClient()
                print("Driver: mongomock-motor (in-memory).")
            except ImportError:
                try:
                    from motor.motor_asyncio import AsyncIOMotorClient

                    client = AsyncIOMotorClient(
                        "mongodb://localhost:27017",
                        serverSelectionTimeoutMS=2500,
                    )
                    await client.admin.command("ping")
                    print("Driver: Motor connected to localhost.")
                except Exception as conn_exc:
                    print("Skipping live CRUD (no mongomock-motor and no MongoDB).")
                    print("  pip install mongomock-motor   # recommended for local examples")
                    print("  # Create")
                    print("  task = Task(title='Review PR', priority=5)")
                    print("  await task.insert()")
                    print("  # Read")
                    print("  task = await Task.find_one(Task.title == 'Review PR')")
                    print("  high = await Task.find(Task.priority >= 4).to_list()")
                    print("  # Update / delete")
                    print("  await task.set({Task.completed: True})  # or task.completed=True; await task.save()")
                    print("  await task.delete()")
                    print(f"  (connection error was: {conn_exc})")
                    return

            try:
                await init_beanie(
                    database=client[db_name],
                    document_models=[Task],
                )
                t = Task(title="Review PR", priority=5)
                await t.insert()
                one = await Task.find_one(Task.title == "Review PR")
                print(f"  find_one: {one.title!r} priority={one.priority}")
                high = await Task.find(Task.priority >= 4).to_list()
                print(f"  priority >= 4: {len(high)} task(s)")
                one.completed = True
                one.priority = 1
                await one.save()
                refreshed = await Task.find_one(Task.id == one.id)
                print(f"  after save: completed={refreshed.completed} priority={refreshed.priority}")
                await refreshed.delete()
                remaining = await Task.find_all().to_list()
                print(f"  after delete: {len(remaining)} task(s) left")
            finally:
                if client is not None:
                    client.close()

        try:
            asyncio.run(_run())
        except Exception as exc:
            print(f"CRUD demo error: {type(exc).__name__}: {exc}")

    except ImportError:
        print("Install: pip install beanie motor")


if __name__ == "__main__":
    demo_crud()
