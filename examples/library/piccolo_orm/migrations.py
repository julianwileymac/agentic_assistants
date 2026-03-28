# requires: piccolo
"""Piccolo migration patterns.

Demonstrates:
- Auto-migration generation
- Running migrations forward/backward
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path


def demo_migrations():
    print("Piccolo Migration Patterns:")
    print()
    print("  # Generate migration after model changes")
    print("  piccolo migrations new my_app --auto")
    print()
    print("  # Run all pending migrations")
    print("  piccolo migrations forwards my_app")
    print()
    print("  # Rollback last migration")
    print("  piccolo migrations backwards my_app 1")
    print()
    print("  # Check migration status")
    print("  piccolo migrations check")
    print()
    print("  # Migration file structure:")
    print("  my_app/")
    print("    piccolo_migrations/")
    print("      my_app_2024_01_15T10_30_00.py")
    print("    tables.py")
    print("    piccolo_app.py")
    print()
    print("  # piccolo_app.py example:")
    print("  APP_CONFIG = AppConfig(")
    print("      app_name='my_app',")
    print("      table_classes=[Author, Book],")
    print("      migration_module='my_app.piccolo_migrations',")
    print("  )")
    print()

    try:
        from piccolo.engine.sqlite import SQLiteEngine
        from piccolo.table import Table
        from piccolo.columns import Varchar, Boolean

        db_path = Path(tempfile.gettempdir()) / "piccolo_library_migrations.sqlite"
        DB = SQLiteEngine(path=str(db_path))

        class Author(Table, db=DB):
            name = Varchar(length=255)
            email = Varchar(length=255, unique=True)
            is_active = Boolean(default=True)

        async def _bootstrap_schema() -> None:
            """What migrations eventually materialize: tables in the target database."""
            await Author.create_table(if_not_exists=True).run()
            await Author.insert(
                Author(name="Schema Demo", email="migrations@example.local", is_active=True)
            ).run()
            rows = await Author.select().run()
            print("SQLite bootstrap (same end state as `piccolo migrations forwards` would apply):")
            print(f"  engine={db_path}")
            print(f"  author rows after insert: {len(rows)}")
            await Author.update({Author.is_active: False}).where(
                Author.email == "migrations@example.local"
            ).run()
            one = await Author.select(Author.name, Author.is_active).where(
                Author.email == "migrations@example.local"
            ).run()
            print(f"  after UPDATE is_active=False: {one}")
            await Author.delete().where(Author.email == "migrations@example.local").run()
            final = await Author.select().run()
            print(f"  after DELETE: {len(final)} author row(s)")

        try:
            asyncio.run(_bootstrap_schema())
        except Exception as exc:
            print(f"SQLite migration-demo error: {type(exc).__name__}: {exc}")

    except ImportError:
        print("(Install piccolo to run the SQLite bootstrap demo above.)")


if __name__ == "__main__":
    demo_migrations()
