"""
Integration tests for data synchronization.
"""

import pytest

from agentic_assistants.sync import SyncManager
from agentic_assistants.sync.sync_manager import SyncStrategy


@pytest.fixture
def sync_manager():
    """Create a sync manager instance."""
    return SyncManager()


def test_sync_manager_creation(sync_manager):
    """Test sync manager creation."""
    assert sync_manager is not None
    assert sync_manager.strategy == SyncStrategy.LAST_WRITE_WINS


def test_start_sync_session(sync_manager):
    """Test starting a sync session."""
    session_id = sync_manager.start_sync(
        source_env="local",
        target_env="kubernetes",
        entity_types=["projects", "agents"],
    )
    
    assert session_id is not None
    assert len(session_id) > 0


def test_conflict_detection(sync_manager):
    """Test conflict detection."""
    from datetime import datetime
    
    source_entities = [
        {
            "id": "test-1",
            "type": "project",
            "name": "Test",
            "updated_at": "2024-01-01T00:00:00",
        }
    ]
    
    target_entities = [
        {
            "id": "test-1",
            "type": "project",
            "name": "Test Modified",
            "updated_at": "2024-01-02T00:00:00",
        }
    ]
    
    conflicts = sync_manager._detect_conflicts(
        source_entities,
        target_entities,
        SyncStrategy.LAST_WRITE_WINS,
    )
    
    # With last-write-wins, target is newer so should have a conflict
    assert len(conflicts) > 0
    assert conflicts[0]["resolution"] == "use_target"


def test_entity_hash_computation(sync_manager):
    """Test entity hash computation."""
    entity1 = {"id": "1", "name": "Test", "value": 123}
    entity2 = {"id": "1", "name": "Test", "value": 123, "updated_at": "different"}
    
    hash1 = sync_manager._compute_hash(entity1)
    hash2 = sync_manager._compute_hash(entity2)
    
    # Hashes should be the same (updated_at is excluded)
    assert hash1 == hash2


def test_list_conflicts(sync_manager):
    """Test listing conflicts."""
    conflicts = sync_manager.get_conflicts()
    assert isinstance(conflicts, list)
