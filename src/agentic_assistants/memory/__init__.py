"""
Memory module for Agentic Assistants.

This module provides memory storage and retrieval for agents,
supporting various backends including mem0 for agentic memory.

Example:
    >>> from agentic_assistants.memory import AgentMemory, Mem0Store
    >>> 
    >>> # Create a memory store
    >>> memory = Mem0Store(user_id="user-123")
    >>> 
    >>> # Add a memory
    >>> memory.add_memory("User prefers Python for data analysis", {"type": "preference"})
    >>> 
    >>> # Search memories
    >>> results = memory.search_memories("programming preferences")
    >>> 
    >>> # Get context for an agent
    >>> context = memory.get_relevant_context("What language should I use?")
"""

from agentic_assistants.memory.base import (
    Memory,
    MemoryConfig,
    AgentMemory,
    MemorySearchResult,
    MemoryScope,
)
from agentic_assistants.memory.mem0_store import Mem0Store
from agentic_assistants.memory.episodic import (
    EpisodicMemory,
    Episode,
    EpisodeType,
)

__all__ = [
    # Base classes
    "Memory",
    "MemoryConfig",
    "AgentMemory",
    "MemorySearchResult",
    "MemoryScope",
    # Implementations
    "Mem0Store",
    # Episodic memory
    "EpisodicMemory",
    "Episode",
    "EpisodeType",
]


def get_memory_store(
    backend: str = "mem0",
    user_id: str = None,
    session_id: str = None,
    config: MemoryConfig = None,
) -> AgentMemory:
    """
    Factory function to create a memory store.
    
    Args:
        backend: Memory backend ('mem0', 'local', 'redis')
        user_id: User identifier for scoping
        session_id: Session identifier for scoping
        config: Memory configuration
        
    Returns:
        AgentMemory instance
    """
    if config is None:
        config = MemoryConfig()
    
    if backend == "mem0":
        return Mem0Store(
            user_id=user_id,
            session_id=session_id,
            config=config,
        )
    elif backend == "local":
        # Local in-memory store (for development/testing)
        from agentic_assistants.memory.local_store import LocalMemoryStore
        return LocalMemoryStore(config=config)
    else:
        raise ValueError(f"Unknown memory backend: {backend}")
