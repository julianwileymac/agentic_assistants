# requires: piccolo
"""Piccolo ORM table definitions.

Demonstrates:
- Table class, column types
- ForeignKey relationships
- Table creation
"""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path


def demo_tables():
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

        db_path = Path(tempfile.gettempdir()) / "piccolo_library_table_definitions.sqlite"
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

        print("Piccolo Table Definitions:")
        print(f"  SQLite engine: {db_path}")
        print(f"  Author columns: {[col._meta.name for col in Author._meta.columns]}")
        print(f"  Book columns: {[col._meta.name for col in Book._meta.columns]}")
        print()
        print("  # Create tables")
        print("  await Author.create_table(if_not_exists=True).run()")
        print("  await Book.create_table(if_not_exists=True).run()")

        async def _run_sqlite() -> None:
            await Author.create_table(if_not_exists=True).run()
            await Book.create_table(if_not_exists=True).run()
            await Author.insert(
                Author(name="Jane", email="jane@example.com", bio="Writes books", is_active=True)
            ).run()
            author_rows = (
                await Author.select(Author.id)
                .where(Author.email == "jane@example.com")
                .limit(1)
                .run()
            )
            aid = author_rows[0]["id"]
            now = datetime.utcnow()
            await Book.insert(
                Book(
                    title="Python Notes",
                    author=aid,
                    isbn="9780000000001",
                    price=29.99,
                    published_year=2024,
                    tags=["python", "orm"],
                    metadata={"shelf": "A1"},
                    created_at=now,
                )
            ).run()
            books = await Book.select().run()
            print()
            print(f"SQLite demo: inserted 1 author, {len(books)} book row(s). Sample: {books[:1]}")
            await Book.update({Book.price: 24.99}).where(Book.isbn == "9780000000001").run()
            updated = await Book.select(Book.title, Book.price).where(Book.isbn == "9780000000001").run()
            print(f"  after UPDATE price: {updated}")
            await Book.delete().where(Book.isbn == "9780000000001").run()
            await Author.delete().where(Author.email == "jane@example.com").run()
            remaining = await Book.select().run()
            print(f"  after DELETE: {len(remaining)} book row(s) remain")

        try:
            asyncio.run(_run_sqlite())
        except Exception as exc:
            print(f"SQLite demo error: {type(exc).__name__}: {exc}")

    except ImportError:
        print("Install: pip install piccolo")


if __name__ == "__main__":
    demo_tables()
