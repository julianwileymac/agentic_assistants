# requires: sqlmodel alembic
"""Alembic migrations with SQLModel.

Demonstrates:
- Alembic setup for SQLModel
- Auto-generating migrations
- Apply/rollback patterns
"""

from __future__ import annotations


def demo_migrations():
    print("Alembic Migrations with SQLModel:")
    print()
    print("  # Initialize Alembic")
    print("  alembic init migrations")
    print()
    print("  # Edit migrations/env.py to import SQLModel metadata:")
    print("  # from sqlmodel import SQLModel")
    print("  # from your_app.models import *  # Import all models")
    print("  # target_metadata = SQLModel.metadata")
    print()
    print("  # Auto-generate migration")
    print("  alembic revision --autogenerate -m 'add items table'")
    print()
    print("  # Apply migrations")
    print("  alembic upgrade head")
    print()
    print("  # Rollback")
    print("  alembic downgrade -1")
    print()
    print("  # View current revision")
    print("  alembic current")
    print()
    print("  # View history")
    print("  alembic history")


if __name__ == "__main__":
    demo_migrations()
