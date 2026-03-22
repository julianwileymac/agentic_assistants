"""
Database abstraction layer for agentic assistants.

Provides unified interface for SQLite, PostgreSQL, and Supabase.
"""

from agentic_assistants.db.base_store import BaseStore, get_store

__all__ = ["BaseStore", "get_store"]
