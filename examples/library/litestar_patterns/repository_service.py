# requires: litestar>=2 sqlalchemy[asyncio]>=2 advanced-alchemy aiosqlite

"""
Litestar + Advanced Alchemy: async repositories with a small service façade.

Uses in-memory SQLite via ``aiosqlite`` so the demo runs without PostgreSQL.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from dataclasses import dataclass

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from litestar import Litestar, Request, get, post
from litestar.di import Provide
from litestar.testing import TestClient
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))


class TaskRepository(SQLAlchemyAsyncRepository[Task]):
    """Typed repository — Advanced Alchemy wires ``AsyncSession`` operations."""

    model_type = Task


# --- Design notes -----------------------------------------------------------
# Advanced Alchemy repositories pair well with service layers enforcing invariants.
# Swap ``sqlite+aiosqlite`` for ``postgresql+asyncpg`` without changing service code.
# Consider SQLAlchemy ``async_sessionmaker`` scopes via middleware instead of manual yields.
# ---------------------------------------------------------------------------


class TaskService:
    """Domain layer keeps route handlers thin."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = TaskRepository(session=self._session)

    async def add_task(self, title: str) -> Task:
        entity = Task(title=title)
        return await self._repo.add(entity, auto_commit=True)

    async def list_tasks(self) -> list[Task]:
        return await self._repo.list()


@dataclass
class NewTask:
    title: str


async def provide_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped session from ``app.state`` populated at startup."""
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with factory() as session:
        yield session


async def on_startup(app: Litestar) -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    app.state.engine = engine
    app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def on_shutdown(app: Litestar) -> None:
    engine: AsyncEngine = app.state.engine
    await engine.dispose()


@post("/tasks", dependencies={"session": Provide(provide_session)})
async def add_task_handler(data: NewTask, session: AsyncSession) -> dict[str, str | int]:
    svc = TaskService(session)
    task = await svc.add_task(data.title)
    return {"id": task.id, "title": task.title}


@get("/tasks", dependencies={"session": Provide(provide_session)})
async def list_tasks_handler(session: AsyncSession) -> list[dict[str, str | int]]:
    svc = TaskService(session)
    rows = await svc.list_tasks()
    return [{"id": t.id, "title": t.title} for t in rows]


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[add_task_handler, list_tasks_handler],
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
    )


def main() -> None:
    app = create_app()
    with TestClient(app=app) as client:
        created = client.post("/tasks", json={"title": "learn advanced-alchemy"})
        print("create:", created.status_code, created.json())
        listed = client.get("/tasks")
        print("list:", listed.json())


if __name__ == "__main__":
    main()
