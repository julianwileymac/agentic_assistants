"""
mem0-backed memory store implementation.

This module provides a memory store backed by mem0, enabling
persistent agent memory with semantic search capabilities.

Example:
    >>> from agentic_assistants.memory import Mem0Store
    >>> 
    >>> memory = Mem0Store(user_id="user-123")
    >>> memory.add_memory("User prefers Python", {"type": "preference"})
    >>> results = memory.search_memories("programming language")
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from agentic_assistants.memory.base import (
    AgentMemory,
    Memory,
    MemoryConfig,
    MemoryScope,
    MemorySearchResult,
    MemoryType,
)
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class Mem0Store(AgentMemory):
    """
    Memory store backed by mem0.
    
    mem0 provides intelligent memory management for AI agents with:
    - Automatic memory extraction from conversations
    - Semantic search over memories
    - User/session scoping
    - Integration with various LLMs
    
    Attributes:
        client: mem0 Memory client instance
        user_id: User identifier for scoping
        session_id: Session identifier for scoping
        agent_id: Agent identifier for scoping
    
    Example:
        >>> memory = Mem0Store(user_id="user-123")
        >>> 
        >>> # Add a memory
        >>> mem = memory.add_memory(
        ...     "User prefers concise responses",
        ...     metadata={"source": "conversation"},
        ...     memory_type=MemoryType.PREFERENCE,
        ... )
        >>> 
        >>> # Search memories
        >>> results = memory.search_memories("user preferences")
        >>> for mem in results.memories:
        ...     print(f"{mem.content} (score: {mem.score:.2f})")
    """
    
    def __init__(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        config: Optional[MemoryConfig] = None,
    ):
        """
        Initialize mem0 memory store.
        
        Args:
            user_id: User identifier for scoping
            session_id: Session identifier for scoping
            agent_id: Agent identifier for scoping
            config: Memory configuration
        """
        super().__init__(
            user_id=user_id,
            session_id=session_id,
            agent_id=agent_id,
            config=config,
        )
        
        self._client = None
        self._initialized = False
    
    @property
    def client(self):
        """Get or initialize mem0 client."""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def _initialize_client(self):
        """Initialize the mem0 client."""
        try:
            from mem0 import Memory
            
            # Build mem0 config from our config
            mem0_config = self.config.mem0_config.copy()
            
            # Set default vector store config if not provided
            if "vector_store" not in mem0_config:
                mem0_config["vector_store"] = {
                    "provider": "chroma",
                    "config": {
                        "collection_name": f"memories_{self.user_id or 'global'}",
                        "path": self.config.storage_path,
                    }
                }
            
            # Set default embedder if not provided
            if "embedder" not in mem0_config:
                mem0_config["embedder"] = {
                    "provider": "ollama",
                    "config": {
                        "model": self.config.embedding_model,
                    }
                }
            
            self._client = Memory.from_config(mem0_config)
            self._initialized = True
            logger.info(f"Initialized mem0 store for user={self.user_id}")
            
        except ImportError:
            raise ImportError(
                "mem0ai is required for Mem0Store. "
                "Install with: pip install mem0ai"
            )
        except Exception as e:
            logger.error(f"Failed to initialize mem0 client: {e}")
            raise
    
    def _get_mem0_user_id(self) -> str:
        """Get the user ID for mem0 API calls."""
        if self.user_id:
            return self.user_id
        if self.session_id:
            return f"session_{self.session_id}"
        if self.agent_id:
            return f"agent_{self.agent_id}"
        return "global"
    
    def add_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        memory_type: MemoryType = MemoryType.FACTUAL,
        scope: MemoryScope = MemoryScope.USER,
    ) -> Memory:
        """
        Add a new memory to the store.
        
        Args:
            content: Memory content
            metadata: Additional metadata
            memory_type: Type of memory
            scope: Memory scope
            
        Returns:
            Created Memory object
        """
        metadata = metadata or {}
        metadata.update({
            "memory_type": memory_type.value,
            "scope": scope.value,
            "created_at": datetime.utcnow().isoformat(),
        })
        
        try:
            # Add to mem0
            result = self.client.add(
                messages=[{"role": "user", "content": content}],
                user_id=self._get_mem0_user_id(),
                metadata=metadata,
            )
            
            # Extract memory ID from result
            memory_id = str(uuid4())
            if result and isinstance(result, dict):
                memory_id = result.get("id", memory_id)
            elif result and isinstance(result, list) and len(result) > 0:
                memory_id = result[0].get("id", memory_id)
            
            return Memory(
                id=memory_id,
                content=content,
                metadata=metadata,
                memory_type=memory_type,
                scope=scope,
                user_id=self.user_id,
                session_id=self.session_id,
                agent_id=self.agent_id,
            )
            
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            # Return a local memory object even if storage fails
            return Memory(
                content=content,
                metadata=metadata,
                memory_type=memory_type,
                scope=scope,
                user_id=self.user_id,
                session_id=self.session_id,
                agent_id=self.agent_id,
            )
    
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
        start_time = time.time()
        
        try:
            # Search mem0
            results = self.client.search(
                query=query,
                user_id=self._get_mem0_user_id(),
                limit=limit,
            )
            
            memories = []
            for result in results:
                # Extract memory data
                memory_data = result if isinstance(result, dict) else {}
                
                # Parse memory type
                mem_type_str = memory_data.get("metadata", {}).get("memory_type", "factual")
                try:
                    mem_type = MemoryType(mem_type_str)
                except ValueError:
                    mem_type = MemoryType.FACTUAL
                
                # Parse scope
                scope_str = memory_data.get("metadata", {}).get("scope", "user")
                try:
                    mem_scope = MemoryScope(scope_str)
                except ValueError:
                    mem_scope = MemoryScope.USER
                
                # Filter by memory types if specified
                if memory_types and mem_type not in memory_types:
                    continue
                
                # Filter by scope if specified
                if scope and mem_scope != scope:
                    continue
                
                memory = Memory(
                    id=memory_data.get("id", str(uuid4())),
                    content=memory_data.get("memory", memory_data.get("text", "")),
                    metadata=memory_data.get("metadata", {}),
                    memory_type=mem_type,
                    scope=mem_scope,
                    user_id=self.user_id,
                    session_id=self.session_id,
                    agent_id=self.agent_id,
                    score=memory_data.get("score", memory_data.get("similarity", 0.0)),
                )
                memories.append(memory)
            
            search_time_ms = (time.time() - start_time) * 1000
            
            return MemorySearchResult(
                memories=memories[:limit],
                total=len(memories),
                query=query,
                search_time_ms=search_time_ms,
            )
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return MemorySearchResult(
                memories=[],
                total=0,
                query=query,
                search_time_ms=(time.time() - start_time) * 1000,
            )
    
    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Memory object or None if not found
        """
        try:
            result = self.client.get(memory_id)
            
            if not result:
                return None
            
            memory_data = result if isinstance(result, dict) else {}
            
            return Memory(
                id=memory_data.get("id", memory_id),
                content=memory_data.get("memory", memory_data.get("text", "")),
                metadata=memory_data.get("metadata", {}),
                user_id=self.user_id,
                session_id=self.session_id,
                agent_id=self.agent_id,
            )
            
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            return None
    
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
        try:
            existing = self.get_memory(memory_id)
            if not existing:
                return None
            
            # Merge metadata
            new_metadata = existing.metadata.copy()
            if metadata:
                new_metadata.update(metadata)
            new_metadata["updated_at"] = datetime.utcnow().isoformat()
            
            # Update in mem0
            self.client.update(
                memory_id=memory_id,
                data=content or existing.content,
                metadata=new_metadata,
            )
            
            return Memory(
                id=memory_id,
                content=content or existing.content,
                metadata=new_metadata,
                memory_type=existing.memory_type,
                scope=existing.scope,
                user_id=self.user_id,
                session_id=self.session_id,
                agent_id=self.agent_id,
                updated_at=datetime.utcnow(),
            )
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            return None
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            True if deleted, False if not found
        """
        try:
            self.client.delete(memory_id)
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
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
        try:
            # mem0 delete_all clears all memories for a user
            self.client.delete_all(user_id=self._get_mem0_user_id())
            logger.info(f"Cleared all memories for user={self._get_mem0_user_id()}")
            return -1  # Count unknown
        except Exception as e:
            logger.error(f"Failed to clear memories: {e}")
            return 0
    
    def add_from_conversation(
        self,
        messages: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Memory]:
        """
        Add memories extracted from a conversation.
        
        mem0 automatically extracts relevant memories from conversations.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            metadata: Additional metadata
            
        Returns:
            List of created Memory objects
        """
        metadata = metadata or {}
        metadata["source"] = "conversation"
        metadata["timestamp"] = datetime.utcnow().isoformat()
        
        try:
            result = self.client.add(
                messages=messages,
                user_id=self._get_mem0_user_id(),
                metadata=metadata,
            )
            
            memories = []
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, dict):
                        memories.append(Memory(
                            id=item.get("id", str(uuid4())),
                            content=item.get("memory", item.get("text", "")),
                            metadata=item.get("metadata", metadata),
                            memory_type=MemoryType.EPISODIC,
                            scope=MemoryScope.USER,
                            user_id=self.user_id,
                            session_id=self.session_id,
                        ))
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to add conversation memories: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory store statistics."""
        stats = super().get_stats()
        stats.update({
            "backend": "mem0",
            "initialized": self._initialized,
            "mem0_user_id": self._get_mem0_user_id(),
        })
        
        try:
            # Get all memories to count
            all_memories = self.client.get_all(user_id=self._get_mem0_user_id())
            stats["total_memories"] = len(all_memories) if all_memories else 0
        except Exception:
            stats["total_memories"] = -1
        
        return stats
