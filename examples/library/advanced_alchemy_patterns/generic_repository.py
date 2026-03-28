# requires: advanced-alchemy sqlalchemy aiosqlite
"""Advanced Alchemy generic repository with filtering and pagination.

Demonstrates:
- SQLAlchemyAsyncRepository
- CollectionFilter, SearchFilter
- Pagination
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column


def demo_repository():
    """Show the Advanced Alchemy repository pattern."""
    try:
        from advanced_alchemy.base import UUIDAuditBase
        from advanced_alchemy.repository import SQLAlchemyAsyncRepository

        class User(UUIDAuditBase):
            __tablename__ = "users"
            username: Mapped[str] = mapped_column(String(100), unique=True)
            email: Mapped[str] = mapped_column(String(255), unique=True)
            bio: Mapped[Optional[str]] = mapped_column(Text, default=None)
            is_active: Mapped[bool] = mapped_column(default=True)

        class UserRepository(SQLAlchemyAsyncRepository[User]):
            """Typed repository for User model."""
            model_type = User

        print("Advanced Alchemy Repository Pattern:")
        print("  UserRepository inherits full CRUD from SQLAlchemyAsyncRepository[User]")
        print()
        print("  Available methods:")
        methods = [
            "add", "add_many", "get", "get_one", "get_one_or_none",
            "list", "list_and_count", "update", "update_many",
            "delete", "delete_many", "upsert", "upsert_many",
            "count", "exists",
        ]
        for m in methods:
            print(f"    - {m}()")
        print()
        print("  Filtering example (pseudo-code):")
        print("    users = await repo.list(")
        print("        CollectionFilter(field_name='is_active', values=[True]),")
        print("        SearchFilter(field_name='username', value='john'),")
        print("        LimitOffset(limit=10, offset=0),")
        print("    )")

        print("\n--- Async SQLite CRUD via UserRepository ---")
        try:
            import asyncio

            from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

            async def _crud() -> None:
                engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
                async with engine.begin() as conn:
                    await conn.run_sync(User.metadata.create_all)

                session_factory = async_sessionmaker(engine, expire_on_commit=False)
                async with session_factory() as session:
                    repo = UserRepository(session=session)
                    alice = User(
                        username="alice",
                        email="alice@example.com",
                        bio="Hello",
                        is_active=True,
                    )
                    await repo.add(alice, auto_commit=True)

                    users = await repo.list()
                    print(f"  list: {len(users)} user(s), emails = {[u.email for u in users]}")

                    fetched = await repo.get(users[0].id)
                    print(f"  get by id: {fetched.username if fetched else None}")

                    alice.bio = "Updated bio via ORM instance"
                    updated = await repo.update(alice, auto_commit=True)
                    print(f"  update bio: {updated.bio}")

                    await repo.delete(users[0].id, auto_commit=True)
                    remaining = await repo.list()
                    print(f"  after delete: {len(remaining)} row(s)")

            asyncio.run(_crud())
        except ImportError as e:
            print(f"  Skipping CRUD demo: {e}")
        except Exception as e:
            print(f"  CRUD demo failed ({type(e).__name__}: {e})")

    except ImportError:
        print("Install: pip install advanced-alchemy sqlalchemy aiosqlite")


def main() -> None:
    """Run the generic async repository example."""
    demo_repository()


if __name__ == "__main__":
    main()
