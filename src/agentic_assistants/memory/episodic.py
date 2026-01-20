"""
Episodic memory management for agents.

This module provides specialized handling for episodic memories,
which represent past events, interactions, and experiences.

Example:
    >>> from agentic_assistants.memory import EpisodicMemory, Episode
    >>> 
    >>> episodic = EpisodicMemory(user_id="user-123")
    >>> 
    >>> # Record an episode
    >>> episode = episodic.record_episode(
    ...     content="User asked about Python data structures",
    ...     outcome="Explained lists, dicts, and sets",
    ...     success=True,
    ... )
    >>> 
    >>> # Get similar past episodes
    >>> similar = episodic.get_similar_episodes("data structures")
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
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


class EpisodeType(str, Enum):
    """Types of episodes that can be recorded."""
    
    CONVERSATION = "conversation"  # Chat interaction
    TASK = "task"                  # Task execution
    DECISION = "decision"          # Decision made
    LEARNING = "learning"          # Something learned
    ERROR = "error"                # Error encountered
    SUCCESS = "success"            # Successful outcome
    FEEDBACK = "feedback"          # User feedback received


@dataclass
class Episode:
    """
    Represents a single episodic memory.
    
    An episode captures a specific event or interaction with context
    about what happened, what was learned, and the outcome.
    
    Attributes:
        id: Unique episode identifier
        content: Description of what happened
        episode_type: Type of episode
        context: Context in which the episode occurred
        action: Action taken (if applicable)
        outcome: Result or outcome
        success: Whether the outcome was successful
        learning: What was learned from this episode
        emotions: Emotional context (if applicable)
        participants: Who was involved
        metadata: Additional metadata
        timestamp: When the episode occurred
        duration_seconds: How long the episode lasted
    """
    
    id: str = field(default_factory=lambda: str(uuid4()))
    content: str = ""
    episode_type: EpisodeType = EpisodeType.CONVERSATION
    
    # Context
    context: str = ""
    action: str = ""
    outcome: str = ""
    success: Optional[bool] = None
    learning: str = ""
    
    # Emotional/social context
    emotions: List[str] = field(default_factory=list)
    participants: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_seconds: Optional[float] = None
    
    # Scoping
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    project_id: Optional[str] = None
    
    # Importance and recall
    importance: float = 0.5  # 0-1 scale
    recall_count: int = 0
    last_recalled: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert episode to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "episode_type": self.episode_type.value,
            "context": self.context,
            "action": self.action,
            "outcome": self.outcome,
            "success": self.success,
            "learning": self.learning,
            "emotions": self.emotions,
            "participants": self.participants,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "duration_seconds": self.duration_seconds,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "project_id": self.project_id,
            "importance": self.importance,
            "recall_count": self.recall_count,
            "last_recalled": self.last_recalled.isoformat() if self.last_recalled else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Episode":
        """Create episode from dictionary."""
        episode_type = data.get("episode_type", "conversation")
        if isinstance(episode_type, str):
            episode_type = EpisodeType(episode_type)
        
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.utcnow()
        
        last_recalled = data.get("last_recalled")
        if isinstance(last_recalled, str):
            last_recalled = datetime.fromisoformat(last_recalled)
        
        return cls(
            id=data.get("id", str(uuid4())),
            content=data.get("content", ""),
            episode_type=episode_type,
            context=data.get("context", ""),
            action=data.get("action", ""),
            outcome=data.get("outcome", ""),
            success=data.get("success"),
            learning=data.get("learning", ""),
            emotions=data.get("emotions", []),
            participants=data.get("participants", []),
            metadata=data.get("metadata", {}),
            timestamp=timestamp,
            duration_seconds=data.get("duration_seconds"),
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            project_id=data.get("project_id"),
            importance=data.get("importance", 0.5),
            recall_count=data.get("recall_count", 0),
            last_recalled=last_recalled,
        )
    
    def to_memory(self) -> Memory:
        """Convert episode to a Memory object for storage."""
        # Build comprehensive content string
        content_parts = [self.content]
        
        if self.context:
            content_parts.append(f"Context: {self.context}")
        if self.action:
            content_parts.append(f"Action: {self.action}")
        if self.outcome:
            content_parts.append(f"Outcome: {self.outcome}")
        if self.learning:
            content_parts.append(f"Learning: {self.learning}")
        
        content = "\n".join(content_parts)
        
        return Memory(
            id=self.id,
            content=content,
            metadata={
                **self.metadata,
                "episode_type": self.episode_type.value,
                "context": self.context,
                "action": self.action,
                "outcome": self.outcome,
                "success": self.success,
                "learning": self.learning,
                "emotions": self.emotions,
                "participants": self.participants,
                "importance": self.importance,
            },
            memory_type=MemoryType.EPISODIC,
            scope=MemoryScope.USER,
            user_id=self.user_id,
            session_id=self.session_id,
            project_id=self.project_id,
            created_at=self.timestamp,
        )
    
    @classmethod
    def from_memory(cls, memory: Memory) -> "Episode":
        """Create episode from a Memory object."""
        metadata = memory.metadata
        
        episode_type_str = metadata.get("episode_type", "conversation")
        try:
            episode_type = EpisodeType(episode_type_str)
        except ValueError:
            episode_type = EpisodeType.CONVERSATION
        
        return cls(
            id=memory.id,
            content=memory.content,
            episode_type=episode_type,
            context=metadata.get("context", ""),
            action=metadata.get("action", ""),
            outcome=metadata.get("outcome", ""),
            success=metadata.get("success"),
            learning=metadata.get("learning", ""),
            emotions=metadata.get("emotions", []),
            participants=metadata.get("participants", []),
            metadata={k: v for k, v in metadata.items() if k not in [
                "episode_type", "context", "action", "outcome", 
                "success", "learning", "emotions", "participants", "importance"
            ]},
            timestamp=memory.created_at,
            user_id=memory.user_id,
            session_id=memory.session_id,
            project_id=memory.project_id,
            importance=metadata.get("importance", 0.5),
        )


class EpisodicMemory:
    """
    Episodic memory manager for agents.
    
    Provides specialized methods for recording and retrieving
    episodic memories (past events and interactions).
    
    Example:
        >>> episodic = EpisodicMemory(user_id="user-123")
        >>> 
        >>> # Record an episode
        >>> episode = episodic.record_episode(
        ...     content="Helped user with Python syntax",
        ...     episode_type=EpisodeType.TASK,
        ...     outcome="User understood the concept",
        ...     success=True,
        ...     learning="Examples work better than explanations",
        ... )
        >>> 
        >>> # Get similar past episodes
        >>> similar = episodic.get_similar_episodes("Python help")
    """
    
    def __init__(
        self,
        memory_store: Optional[AgentMemory] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        config: Optional[MemoryConfig] = None,
    ):
        """
        Initialize episodic memory manager.
        
        Args:
            memory_store: Underlying memory store (creates one if None)
            user_id: User identifier
            session_id: Session identifier
            config: Memory configuration
        """
        self.user_id = user_id
        self.session_id = session_id
        self.config = config or MemoryConfig()
        
        # Initialize or use provided memory store
        if memory_store:
            self._store = memory_store
        else:
            from agentic_assistants.memory import get_memory_store
            self._store = get_memory_store(
                backend=self.config.backend,
                user_id=user_id,
                session_id=session_id,
                config=config,
            )
    
    def record_episode(
        self,
        content: str,
        episode_type: EpisodeType = EpisodeType.CONVERSATION,
        context: str = "",
        action: str = "",
        outcome: str = "",
        success: Optional[bool] = None,
        learning: str = "",
        emotions: Optional[List[str]] = None,
        participants: Optional[List[str]] = None,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Episode:
        """
        Record a new episode.
        
        Args:
            content: Description of what happened
            episode_type: Type of episode
            context: Context in which it occurred
            action: Action taken
            outcome: Result or outcome
            success: Whether successful
            learning: What was learned
            emotions: Emotional context
            participants: Who was involved
            importance: Importance score (0-1)
            metadata: Additional metadata
            
        Returns:
            Created Episode object
        """
        episode = Episode(
            content=content,
            episode_type=episode_type,
            context=context,
            action=action,
            outcome=outcome,
            success=success,
            learning=learning,
            emotions=emotions or [],
            participants=participants or [],
            metadata=metadata or {},
            importance=importance,
            user_id=self.user_id,
            session_id=self.session_id,
        )
        
        # Store as memory
        memory = episode.to_memory()
        self._store.add_memory(
            content=memory.content,
            metadata=memory.metadata,
            memory_type=MemoryType.EPISODIC,
            scope=MemoryScope.USER,
        )
        
        logger.debug(f"Recorded episode: {episode.id} ({episode_type.value})")
        
        return episode
    
    def record_conversation(
        self,
        user_message: str,
        assistant_response: str,
        context: str = "",
        success: Optional[bool] = None,
        learning: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Episode:
        """
        Record a conversation episode.
        
        Args:
            user_message: User's message
            assistant_response: Assistant's response
            context: Additional context
            success: Whether the interaction was successful
            learning: What was learned
            metadata: Additional metadata
            
        Returns:
            Created Episode object
        """
        content = f"User: {user_message}\nAssistant: {assistant_response}"
        
        episode_metadata = metadata or {}
        episode_metadata.update({
            "user_message": user_message,
            "assistant_response": assistant_response,
        })
        
        return self.record_episode(
            content=content,
            episode_type=EpisodeType.CONVERSATION,
            context=context,
            action=assistant_response,
            outcome="Response delivered",
            success=success,
            learning=learning,
            metadata=episode_metadata,
        )
    
    def record_task(
        self,
        task_description: str,
        actions: List[str],
        result: str,
        success: bool,
        learning: str = "",
        duration_seconds: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Episode:
        """
        Record a task execution episode.
        
        Args:
            task_description: Description of the task
            actions: Actions taken to complete the task
            result: Task result
            success: Whether the task succeeded
            learning: What was learned
            duration_seconds: How long it took
            metadata: Additional metadata
            
        Returns:
            Created Episode object
        """
        content = f"Task: {task_description}"
        action_str = "\n".join(f"- {a}" for a in actions)
        
        episode = self.record_episode(
            content=content,
            episode_type=EpisodeType.TASK,
            context=task_description,
            action=action_str,
            outcome=result,
            success=success,
            learning=learning,
            metadata=metadata,
        )
        episode.duration_seconds = duration_seconds
        
        return episode
    
    def record_error(
        self,
        error_description: str,
        context: str = "",
        attempted_action: str = "",
        resolution: str = "",
        learning: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Episode:
        """
        Record an error episode.
        
        Args:
            error_description: Description of the error
            context: Context when error occurred
            attempted_action: What was being attempted
            resolution: How it was resolved (if at all)
            learning: What was learned
            metadata: Additional metadata
            
        Returns:
            Created Episode object
        """
        return self.record_episode(
            content=f"Error: {error_description}",
            episode_type=EpisodeType.ERROR,
            context=context,
            action=attempted_action,
            outcome=resolution or "Unresolved",
            success=bool(resolution),
            learning=learning,
            importance=0.8,  # Errors are generally important
            metadata=metadata,
        )
    
    def record_learning(
        self,
        learning: str,
        context: str = "",
        source: str = "",
        confidence: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Episode:
        """
        Record a learning episode.
        
        Args:
            learning: What was learned
            context: Context of the learning
            source: Source of the learning
            confidence: Confidence in the learning (0-1)
            metadata: Additional metadata
            
        Returns:
            Created Episode object
        """
        episode_metadata = metadata or {}
        episode_metadata.update({
            "source": source,
            "confidence": confidence,
        })
        
        return self.record_episode(
            content=learning,
            episode_type=EpisodeType.LEARNING,
            context=context,
            learning=learning,
            importance=confidence,
            metadata=episode_metadata,
        )
    
    def get_similar_episodes(
        self,
        query: str,
        limit: int = 5,
        episode_types: Optional[List[EpisodeType]] = None,
        min_importance: float = 0.0,
    ) -> List[Episode]:
        """
        Get episodes similar to a query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            episode_types: Filter by episode types
            min_importance: Minimum importance threshold
            
        Returns:
            List of similar Episode objects
        """
        # Convert episode types to memory types filter
        memory_types = [MemoryType.EPISODIC]
        
        results = self._store.search_memories(
            query=query,
            limit=limit * 2,  # Get extra to filter
            memory_types=memory_types,
        )
        
        episodes = []
        for memory in results.memories:
            episode = Episode.from_memory(memory)
            
            # Filter by episode type
            if episode_types and episode.episode_type not in episode_types:
                continue
            
            # Filter by importance
            if episode.importance < min_importance:
                continue
            
            # Update recall stats
            episode.recall_count += 1
            episode.last_recalled = datetime.utcnow()
            
            episodes.append(episode)
            
            if len(episodes) >= limit:
                break
        
        return episodes
    
    def get_recent_episodes(
        self,
        limit: int = 10,
        episode_types: Optional[List[EpisodeType]] = None,
    ) -> List[Episode]:
        """
        Get the most recent episodes.
        
        Args:
            limit: Maximum number of results
            episode_types: Filter by episode types
            
        Returns:
            List of recent Episode objects
        """
        # Search with generic query to get recent items
        results = self._store.search_memories(
            query="recent interaction",
            limit=limit * 2,
            memory_types=[MemoryType.EPISODIC],
        )
        
        episodes = []
        for memory in results.memories:
            episode = Episode.from_memory(memory)
            
            if episode_types and episode.episode_type not in episode_types:
                continue
            
            episodes.append(episode)
            
            if len(episodes) >= limit:
                break
        
        # Sort by timestamp (most recent first)
        episodes.sort(key=lambda e: e.timestamp, reverse=True)
        
        return episodes[:limit]
    
    def get_learnings(self, topic: str = "", limit: int = 10) -> List[Episode]:
        """
        Get learning episodes, optionally filtered by topic.
        
        Args:
            topic: Topic to filter by (empty = all)
            limit: Maximum number of results
            
        Returns:
            List of learning Episode objects
        """
        query = topic if topic else "learning insight pattern"
        
        return self.get_similar_episodes(
            query=query,
            limit=limit,
            episode_types=[EpisodeType.LEARNING],
        )
    
    def get_errors(self, context: str = "", limit: int = 10) -> List[Episode]:
        """
        Get error episodes, optionally filtered by context.
        
        Args:
            context: Context to filter by (empty = all)
            limit: Maximum number of results
            
        Returns:
            List of error Episode objects
        """
        query = context if context else "error problem issue"
        
        return self.get_similar_episodes(
            query=query,
            limit=limit,
            episode_types=[EpisodeType.ERROR],
        )
    
    def get_context_for_task(
        self,
        task_description: str,
        max_episodes: int = 3,
    ) -> str:
        """
        Get relevant episodic context for a task.
        
        Searches for similar past tasks and learnings to provide
        context for approaching a new task.
        
        Args:
            task_description: Description of the task
            max_episodes: Maximum episodes to include
            
        Returns:
            Formatted context string
        """
        # Get similar past tasks
        similar_tasks = self.get_similar_episodes(
            query=task_description,
            limit=max_episodes,
            episode_types=[EpisodeType.TASK],
        )
        
        # Get relevant learnings
        learnings = self.get_learnings(topic=task_description, limit=max_episodes)
        
        context_parts = []
        
        if similar_tasks:
            context_parts.append("Relevant past experiences:")
            for episode in similar_tasks:
                status = "succeeded" if episode.success else "failed"
                context_parts.append(
                    f"- {episode.content} ({status})"
                )
                if episode.learning:
                    context_parts.append(f"  Learning: {episode.learning}")
        
        if learnings:
            context_parts.append("\nRelevant learnings:")
            for episode in learnings:
                context_parts.append(f"- {episode.learning}")
        
        return "\n".join(context_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get episodic memory statistics."""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "store_stats": self._store.get_stats(),
        }
