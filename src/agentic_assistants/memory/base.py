"""
Base classes and interfaces for agent memory storage.

This module defines the abstract interface that all memory stores
must implement, providing a consistent API for storing and retrieving
agent memories.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class MemoryScope(str, Enum):
    """Scope of memory visibility and persistence."""
    
    GLOBAL = "global"       # Shared across all users/sessions
    USER = "user"           # Scoped to a specific user
    SESSION = "session"     # Scoped to a specific session
    PROJECT = "project"     # Scoped to a specific project
    AGENT = "agent"         # Scoped to a specific agent instance


class MemoryType(str, Enum):
    """Type of memory content."""
    
    FACTUAL = "factual"         # Facts and information
    PROCEDURAL = "procedural"   # How to do things
    EPISODIC = "episodic"       # Past events/interactions
    SEMANTIC = "semantic"       # Concepts and relationships
    PREFERENCE = "preference"   # User/agent preferences


@dataclass
class Memory:
    """
    A single memory entry.
    
    Attributes:
        id: Unique memory identifier
        content: Memory content (text)
        metadata: Additional metadata
        memory_type: Type of memory
        scope: Memory scope
        user_id: Associated user ID
        session_id: Associated session ID
        agent_id: Associated agent ID
        created_at: Creation timestamp
        updated_at: Last update timestamp
        embedding: Optional embedding vector
        score: Relevance score (when returned from search)
    """
    
    id: str = field(default_factory=lambda: str(uuid4()))
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    memory_type: MemoryType = MemoryType.FACTUAL
    scope: MemoryScope = MemoryScope.USER
    
    # Scoping identifiers
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    project_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Vector representation
    embedding: Optional[List[float]] = None
    
    # Search relevance
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "memory_type": self.memory_type.value,
            "scope": self.scope.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "score": self.score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create memory from dictionary."""
        memory_type = data.get("memory_type", "factual")
        if isinstance(memory_type, str):
            memory_type = MemoryType(memory_type)
        
        scope = data.get("scope", "user")
        if isinstance(scope, str):
            scope = MemoryScope(scope)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.utcnow()
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif updated_at is None:
            updated_at = datetime.utcnow()
        
        return cls(
            id=data.get("id", str(uuid4())),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            memory_type=memory_type,
            scope=scope,
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            agent_id=data.get("agent_id"),
            project_id=data.get("project_id"),
            created_at=created_at,
            updated_at=updated_at,
            embedding=data.get("embedding"),
            score=data.get("score", 0.0),
        )


@dataclass
class MemorySearchResult:
    """Result from a memory search operation."""
    
    memories: List[Memory] = field(default_factory=list)
    total: int = 0
    query: str = ""
    search_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "memories": [m.to_dict() for m in self.memories],
            "total": self.total,
            "query": self.query,
            "search_time_ms": self.search_time_ms,
        }


class MemoryConfig(BaseModel):
    """Configuration for memory stores."""
    
    # Backend settings
    backend: str = Field(
        default="mem0",
        description="Memory backend (mem0, local, redis)",
    )
    
    # mem0 specific settings
    mem0_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="mem0-specific configuration",
    )
    
    # Vector settings
    embedding_model: str = Field(
        default="nomic-embed-text",
        description="Embedding model for memory vectors",
    )
    embedding_dimension: int = Field(
        default=768,
        description="Embedding vector dimension",
    )
    
    # Storage settings
    persist_to_disk: bool = Field(
        default=True,
        description="Persist memories to disk",
    )
    storage_path: str = Field(
        default="./data/memories",
        description="Path for memory storage",
    )
    
    # Search settings
    default_top_k: int = Field(
        default=10,
        description="Default number of results to return",
    )
    similarity_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score for results",
    )
    
    # Context settings
    max_context_memories: int = Field(
        default=5,
        description="Maximum memories to include in context",
    )
    max_context_length: int = Field(
        default=4000,
        description="Maximum character length for context",
    )
    
    # Retention settings
    memory_ttl_days: Optional[int] = Field(
        default=None,
        description="Days to retain memories (None = forever)",
    )
    max_memories_per_user: int = Field(
        default=10000,
        description="Maximum memories per user",
    )


class AgentMemory(ABC):
    """
    Abstract base class for agent memory stores.
    
    This class defines the interface that all memory store implementations
    must follow, providing methods for adding, searching, and managing
    agent memories.
    
    Implementations:
    - Mem0Store: mem0-backed memory store
    - LocalMemoryStore: In-memory store for development
    - RedisMemoryStore: Redis-backed store for distributed systems
    """
    
    def __init__(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        config: Optional[MemoryConfig] = None,
    ):
        """
        Initialize the memory store.
        
        Args:
            user_id: User identifier for scoping
            session_id: Session identifier for scoping
            agent_id: Agent identifier for scoping
            config: Memory configuration
        """
        self.user_id = user_id
        self.session_id = session_id
        self.agent_id = agent_id
        self.config = config or MemoryConfig()
    
    @abstractmethod
    def add_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        memory_type: MemoryType = MemoryType.FACTUAL,
        scope: MemoryScope = MemoryScope.USER,
    ) -> Memory:
        """
        Add a new memory.
        
        Args:
            content: Memory content
            metadata: Additional metadata
            memory_type: Type of memory
            scope: Memory scope
            
        Returns:
            Created Memory object
        """
        pass
    
    @abstractmethod
    def search_memories(
        self,
        query: str,
        limit: int = 10,
        memory_types: Optional[List[MemoryType]] = None,
        scope: Optional[MemoryScope] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> MemorySearchResult:
        """
        Search memories by semantic similarity.
        
        Args:
            query: Search query
            limit: Maximum results to return
            memory_types: Filter by memory types
            scope: Filter by scope
            filters: Additional metadata filters
            
        Returns:
            MemorySearchResult with matching memories
        """
        pass
    
    @abstractmethod
    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Memory object or None if not found
        """
        pass
    
    @abstractmethod
    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Memory]:
        """
        Update an existing memory.
        
        Args:
            memory_id: Memory identifier
            content: New content (if updating)
            metadata: New metadata (merged with existing)
            
        Returns:
            Updated Memory object or None if not found
        """
        pass
    
    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def clear_memories(
        self,
        scope: Optional[MemoryScope] = None,
        memory_types: Optional[List[MemoryType]] = None,
    ) -> int:
        """
        Clear memories matching criteria.
        
        Args:
            scope: Scope to clear (None = all)
            memory_types: Types to clear (None = all)
            
        Returns:
            Number of memories deleted
        """
        pass
    
    def get_relevant_context(
        self,
        query: str,
        max_memories: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> str:
        """
        Get relevant context for a query.
        
        This method searches memories and formats them into a context
        string suitable for including in an LLM prompt.
        
        Args:
            query: Query to get context for
            max_memories: Maximum memories to include
            max_length: Maximum character length
            
        Returns:
            Formatted context string
        """
        max_memories = max_memories or self.config.max_context_memories
        max_length = max_length or self.config.max_context_length
        
        result = self.search_memories(query, limit=max_memories)
        
        if not result.memories:
            return ""
        
        context_parts = []
        current_length = 0
        
        for memory in result.memories:
            memory_text = f"- {memory.content}"
            if current_length + len(memory_text) > max_length:
                break
            context_parts.append(memory_text)
            current_length += len(memory_text) + 1  # +1 for newline
        
        return "\n".join(context_parts)
    
    def add_interaction(
        self,
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        """
        Add an interaction as an episodic memory.
        
        Args:
            user_message: User's message
            assistant_response: Assistant's response
            metadata: Additional metadata
            
        Returns:
            Created Memory object
        """
        content = f"User: {user_message}\nAssistant: {assistant_response}"
        
        mem_metadata = metadata or {}
        mem_metadata.update({
            "user_message": user_message,
            "assistant_response": assistant_response,
            "interaction_type": "conversation",
        })
        
        return self.add_memory(
            content=content,
            metadata=mem_metadata,
            memory_type=MemoryType.EPISODIC,
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory store statistics."""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "config": {
                "backend": self.config.backend,
                "embedding_model": self.config.embedding_model,
            },
        }
