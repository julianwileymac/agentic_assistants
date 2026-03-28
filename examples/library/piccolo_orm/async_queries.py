# requires: piccolo
"""Piccolo async query patterns.

Demonstrates:
- Select, insert, update, delete
- Filtering, ordering, output formats
"""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path


def demo_async_queries():
    print("Piccolo Async Query Patterns (reference snippets):")
    print()
    print("  await Author.insert(Author(name='Jane', email='jane@example.com')).run()")
    print("  authors = await Author.select().run()")
    print("  active = await Author.select().where(Author.is_active == True).run()")
    print("  names = await Author.select(Author.name, Author.email).run()")
    print("  name_list = await Author.select(Author.name).output(as_list=True).run()")
    print("  await Author.update({Author.is_active: False}).where(...).run()")
    print("  await Author.delete().where(Author.is_active == False).run()")
    print()

    try:
        from piccolo.engine.sqlite import SQLiteEngine
        from piccolo.table import Table
        from piccolo.columns import (
            Varchar,
            Text,
            Integer,
            Float,
            Boolean,
            Timestamp,
            ForeignKey,
            JSON,
            Array,
        )

        db_path = Path(tempfile.gettempdir()) / "piccolo_library_async_queries.sqlite"
        DB = SQLiteEngine(path=str(db_path))

        class Author(Table, db=DB):
            name = Varchar(length=255)
            email = Varchar(length=255, unique=True)
            bio = Text(default="")
            is_active = Boolean(default=True)

        class Book(Table, db=DB):
            title = Varchar(length=500)
            author = ForeignKey(references=Author)
            isbn = Varchar(length=13, unique=True)
            price = Float(default=0.0)
            published_year = Integer(default=2024)
            tags = Array(base_column=Varchar(length=50))
            metadata = JSON(default={})
            created_at = Timestamp()

        async def _run() -> None:
            await Author.create_table(if_not_exists=True).run()
            await Book.create_table(if_not_exists=True).run()
            await Author.insert(
                Author(name="Jane", email="jane@queries.example", bio="", is_active=True),
                Author(name="Inactive", email="old@queries.example", bio="", is_active=False),
            ).run()
            all_authors = await Author.select().run()
            print(f"select(): {len(all_authors)} author row(s)")
            active = await Author.select().where(Author.is_active == True).run()  # noqa: E712
            print(f"where(is_active==True): {len(active)} row(s)")
            pairs = await Author.select(Author.name, Author.email).run()
            print(f"select(name, email) sample: {pairs[:1]}")
            name_list = await Author.select(Author.name).output(as_list=True).run()
            print(f"output(as_list=True) names: {name_list[:3]}")
            author_id = (
                await Author.select(Author.id)
                .where(Author.email == "jane@queries.example")
                .limit(1)
                .run()
            )[0]["id"]
            await Book.insert(
                Book(
                    title="Query Guide",
                    author=author_id,
                    isbn="9780000000002",
                    price=15.0,
                    tags=["sql"],
                    metadata={},
                    created_at=datetime.utcnow(),
                )
            ).run()
            recent = (
                await Book.select()
                .order_by(Book.created_at, ascending=False)
                .limit(10)
                .run()
            )
            print(f"Book order_by created_at desc, limit 10: {len(recent)} row(s)")
            await Author.update({Author.is_active: False}).where(
                Author.email == "jane@queries.example"
            ).run()
            await Author.delete().where(Author.email == "old@queries.example").run()
            after = await Author.select(Author.name, Author.is_active).run()
            print(f"After update+delete: {after}")
            try:
                like = await Author.raw(
                    "SELECT * FROM author WHERE name LIKE {}",
                    "%Jane%",
                ).run()
                print(f"raw SQL LIKE %Jane%: {len(like)} row(s)")
            except Exception as raw_exc:
                print(f"(raw() example skipped: {raw_exc})")

        try:
            asyncio.run(_run())
        except Exception as exc:
            print(f"SQLite query demo error: {type(exc).__name__}: {exc}")

    except ImportError:
        print("Install: pip install piccolo")


if __name__ == "__main__":
    demo_async_queries()
