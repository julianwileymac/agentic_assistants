# requires: sqlalchemy[asyncio]>=2 aiosqlite asyncpg

"""
Async SQLAlchemy sessions.

Async engines pair naturally with ASGI servers: each request awaits I/O without
blocking threads. Session lifecycle still matters — typically one short-lived
``AsyncSession`` per request, created from ``async_sessionmaker``.

The runnable demo uses ``sqlite+aiosqlite`` so it works without PostgreSQL. For
``asyncpg``, point ``create_async_engine`` at ``postgresql+asyncpg://user:pass@host/db``.
"""

from __future__ import annotations

from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(200))


async def seed(session: AsyncSession) -> None:
    session.add_all([Item(label="alpha"), Item(label="beta")])
    await session.commit()


async def list_labels(session: AsyncSession) -> list[str]:
    result = await session.scalars(select(Item.label).order_by(Item.id))
    return list(result)


async def update_label(session: AsyncSession, item_id: int, new_label: str) -> None:
    obj = await session.get(Item, item_id)
    if obj is None:
        raise LookupError("missing item")
    obj.label = new_label
    await session.commit()


# --- Design notes -----------------------------------------------------------
# Always ``await session.close()`` contexts via ``async with sessionmaker()``.
# Use ``expire_on_commit=False`` when returning ORM objects from service layers.
# Pool configuration matters as much as sync vs async — monitor checkout times.
# ---------------------------------------------------------------------------


async def delete_all(session: AsyncSession) -> None:
    for row in (await session.scalars(select(Item))).all():
        await session.delete(row)
    await session.commit()


async def count_items(session: AsyncSession) -> int:
    rows = await session.scalars(select(Item.id))
    return len(rows.all())


async def demo() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await seed(session)
        print("count:", await count_items(session))
        print("labels:", await list_labels(session))
        await update_label(session, 1, "alpha-prime")
        print("after update:", await list_labels(session))
        await delete_all(session)

    await engine.dispose()


def main() -> None:
    import asyncio

    asyncio.run(demo())
    print(
        "For PostgreSQL + asyncpg, use:\n"
        '  create_async_engine("postgresql+asyncpg://user:pass@localhost/dbname")\n'
        "and the same ``async_sessionmaker`` / ``AsyncSession`` patterns as above."
    )


if __name__ == "__main__":
    main()
