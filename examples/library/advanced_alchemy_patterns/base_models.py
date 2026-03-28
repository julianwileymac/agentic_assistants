# requires: advanced-alchemy sqlalchemy aiosqlite
"""Advanced Alchemy base classes and mixins.

Demonstrates:
- UUIDBase, BigIntBase, BigIntAuditBase
- SlugKey mixin
- Custom audit columns
"""

from __future__ import annotations

from typing import Optional


def demo_base_models():
    """Show Advanced Alchemy base model patterns."""
    try:
        from advanced_alchemy.base import (
            UUIDAuditBase,
            BigIntAuditBase,
            BigIntBase,
            SlugKey,
        )
        from sqlalchemy.orm import Mapped, mapped_column
        from sqlalchemy import String, Text

        class Project(UUIDAuditBase):
            """Project with UUID PK + created_at/updated_at."""

            __tablename__ = "projects"

            name: Mapped[str] = mapped_column(String(255))
            description: Mapped[Optional[str]] = mapped_column(Text, default=None)
            status: Mapped[str] = mapped_column(String(50), default="active")

        class Article(BigIntAuditBase, SlugKey):
            """Article with BigInt PK, audit timestamps, and a slug."""

            __tablename__ = "articles"

            title: Mapped[str] = mapped_column(String(500))
            body: Mapped[str] = mapped_column(Text)
            author: Mapped[str] = mapped_column(String(255))

        class Tag(BigIntBase):
            """Simple tag with BigInt PK, no audit fields."""

            __tablename__ = "tags"

            name: Mapped[str] = mapped_column(String(100), unique=True)

        print("Advanced Alchemy Base Models:")
        print(f"  Project (UUIDAuditBase): columns = {[c.name for c in Project.__table__.columns]}")
        print(f"  Article (BigIntAuditBase + SlugKey): columns = {[c.name for c in Article.__table__.columns]}")
        print(f"  Tag (BigIntBase): columns = {[c.name for c in Tag.__table__.columns]}")

        print("\n--- Async SQLite: create tables, insert, query ---")
        try:
            import asyncio

            from sqlalchemy import select
            from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

            async def _db_roundtrip() -> None:
                engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
                async with engine.begin() as conn:
                    def _create_schema(sync_conn) -> None:
                        tables = [Project.__table__, Article.__table__, Tag.__table__]
                        md = Project.__table__.metadata
                        if all(t.metadata is md for t in tables):
                            md.create_all(sync_conn, tables=tables)
                        else:
                            for t in tables:
                                t.metadata.create_all(sync_conn, tables=[t])

                    await conn.run_sync(_create_schema)

                session_factory = async_sessionmaker(engine, expire_on_commit=False)
                async with session_factory() as session:
                    session.add_all(
                        [
                            Project(name="Atlas", description="Routing study", status="active"),
                            Project(name="Beacon", description="Telemetry", status="archived"),
                            Article(
                                title="Patterns with Advanced Alchemy",
                                body="Repositories, services, and DTO-friendly models.",
                                author="Examples",
                                slug="patterns-advanced-alchemy",
                            ),
                            Tag(name="sqlalchemy"),
                            Tag(name="async"),
                        ]
                    )
                    await session.commit()

                async with session_factory() as session:
                    result = await session.execute(select(Project).where(Project.status == "active"))
                    active = result.scalars().all()
                    print(f"  Inserted projects; active count = {len(active)} -> {[p.name for p in active]}")

                    art = (await session.execute(select(Article))).scalars().first()
                    tags = (await session.execute(select(Tag).order_by(Tag.name))).scalars().all()
                    print(
                        f"  Article slug={art.slug!r} title={art.title!r} "
                        f"tags={[t.name for t in tags]}"
                    )

            asyncio.run(_db_roundtrip())
        except ImportError as e:
            print(f"  Skipping DB demo (missing driver or dependency): {e}")
        except Exception as e:
            print(f"  DB demo failed ({type(e).__name__}: {e})")

    except ImportError:
        print("Install: pip install advanced-alchemy sqlalchemy aiosqlite")


def main() -> None:
    """Run the Advanced Alchemy base model example."""
    demo_base_models()


if __name__ == "__main__":
    main()
