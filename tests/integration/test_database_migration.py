"""
Integration tests for database migration.
"""

import pytest
from pathlib import Path

from agentic_assistants.config import AgenticConfig
from agentic_assistants.db import get_store


@pytest.fixture
def sqlite_config():
    """Create config for SQLite."""
    config = AgenticConfig()
    config.database.type = "sqlite"
    return config


@pytest.fixture
def postgres_config():
    """Create config for PostgreSQL."""
    config = AgenticConfig()
    config.database.type = "postgres"
    config.postgresql.enabled = True
    return config


def test_sqlite_store_creation(sqlite_config):
    """Test SQLite store creation."""
    store = get_store(sqlite_config)
    assert store is not None
    
    # Create a test project
    project = store.create_project(
        name="Test Project",
        description="Test description",
    )
    
    assert project.id is not None
    assert project.name == "Test Project"
    
    # Retrieve the project
    retrieved = store.get_project(project.id)
    assert retrieved is not None
    assert retrieved.name == project.name


@pytest.mark.skipif(
    not pytest.config.getoption("--postgres"),
    reason="PostgreSQL tests require --postgres flag"
)
def test_postgres_store_creation(postgres_config):
    """Test PostgreSQL store creation."""
    try:
        from agentic_assistants.db.postgres_store import PostgreSQLStore
    except ImportError:
        pytest.skip("psycopg not available")
    
    store = get_store(postgres_config)
    assert store is not None
    assert isinstance(store, PostgreSQLStore)
    
    # Create a test project
    project = store.create_project(
        name="Test Project PG",
        description="PostgreSQL test",
    )
    
    assert project.id is not None
    assert project.name == "Test Project PG"


def test_store_factory():
    """Test store factory function."""
    # Default (SQLite)
    config = AgenticConfig()
    store = get_store(config)
    assert store is not None
    
    # Verify we can create and retrieve data
    project = store.create_project(name="Factory Test")
    assert project.id is not None
    
    retrieved = store.get_project(project.id)
    assert retrieved.name == "Factory Test"
