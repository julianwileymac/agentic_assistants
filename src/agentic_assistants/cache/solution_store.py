"""
Solution cache for storing and retrieving reusable agent solutions.

This module provides a specialized cache for agent solutions,
workflow states, and reusable code patterns.

Example:
    >>> from agentic_assistants.cache import SolutionCache, Solution
    >>> 
    >>> cache = SolutionCache()
    >>> 
    >>> # Store a solution
    >>> solution = Solution(
    ...     name="parse-json",
    ...     description="Parse JSON with error handling",
    ...     code="def parse_json(text): ...",
    ...     tags=["json", "parsing"],
    ... )
    >>> cache.store(solution)
    >>> 
    >>> # Retrieve
    >>> cached = cache.get("parse-json")
    >>> 
    >>> # Search by tags
    >>> results = cache.search_by_tags(["json"])
"""

import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from agentic_assistants.cache.redis_cache import RedisCache, CacheConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class SolutionType(str, Enum):
    """Types of cached solutions."""
    
    CODE = "code"              # Code snippet or function
    WORKFLOW = "workflow"      # Multi-step workflow
    PATTERN = "pattern"        # Design pattern
    PROMPT = "prompt"          # Prompt template
    TOOL = "tool"              # Tool definition
    AGENT = "agent"            # Agent configuration
    PIPELINE = "pipeline"      # Data pipeline


@dataclass
class Solution:
    """
    A cached solution that can be reused.
    
    Attributes:
        id: Unique solution identifier
        name: Solution name (also used as cache key)
        description: Description of what it does
        solution_type: Type of solution
        content: The actual solution content
        code: Optional code content
        tags: Tags for categorization
        metadata: Additional metadata
        created_at: Creation timestamp
        updated_at: Last update timestamp
        use_count: Number of times used
        success_rate: Success rate (0-1)
        author: Who created it
        version: Solution version
    """
    
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    solution_type: SolutionType = SolutionType.CODE
    content: Any = None
    code: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Usage tracking
    use_count: int = 0
    success_rate: float = 1.0
    last_used: Optional[datetime] = None
    
    # Attribution
    author: str = ""
    version: str = "1.0.0"
    
    # Scoping
    project_id: Optional[str] = None
    is_global: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "solution_type": self.solution_type.value,
            "content": self.content,
            "code": self.code,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "use_count": self.use_count,
            "success_rate": self.success_rate,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "author": self.author,
            "version": self.version,
            "project_id": self.project_id,
            "is_global": self.is_global,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Solution":
        """Create from dictionary."""
        solution_type = data.get("solution_type", "code")
        if isinstance(solution_type, str):
            solution_type = SolutionType(solution_type)
        
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
        
        last_used = data.get("last_used")
        if isinstance(last_used, str):
            last_used = datetime.fromisoformat(last_used)
        
        return cls(
            id=data.get("id", str(uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            solution_type=solution_type,
            content=data.get("content"),
            code=data.get("code", ""),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            created_at=created_at,
            updated_at=updated_at,
            use_count=data.get("use_count", 0),
            success_rate=data.get("success_rate", 1.0),
            last_used=last_used,
            author=data.get("author", ""),
            version=data.get("version", "1.0.0"),
            project_id=data.get("project_id"),
            is_global=data.get("is_global", False),
        )
    
    def get_key(self) -> str:
        """Get the cache key for this solution."""
        if self.project_id and not self.is_global:
            return f"project:{self.project_id}:{self.name}"
        return f"global:{self.name}"


@dataclass
class WorkflowState:
    """
    Cached state for a workflow execution.
    
    Attributes:
        workflow_id: Unique workflow identifier
        name: Workflow name
        status: Current status
        current_step: Current step index
        steps: List of step definitions
        results: Results from completed steps
        context: Workflow context data
        error: Error message if failed
        created_at: Start timestamp
        updated_at: Last update timestamp
    """
    
    workflow_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    status: str = "pending"  # pending, running, completed, failed
    current_step: int = 0
    steps: List[Dict[str, Any]] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Scoping
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    project_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status,
            "current_step": self.current_step,
            "steps": self.steps,
            "results": self.results,
            "context": self.context,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "project_id": self.project_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """Create from dictionary."""
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
        
        completed_at = data.get("completed_at")
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)
        
        return cls(
            workflow_id=data.get("workflow_id", str(uuid4())),
            name=data.get("name", ""),
            status=data.get("status", "pending"),
            current_step=data.get("current_step", 0),
            steps=data.get("steps", []),
            results=data.get("results", {}),
            context=data.get("context", {}),
            error=data.get("error"),
            created_at=created_at,
            updated_at=updated_at,
            completed_at=completed_at,
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            project_id=data.get("project_id"),
        )


class SolutionCache:
    """
    Cache for storing and retrieving reusable solutions.
    
    Provides methods for storing, searching, and managing
    cached solutions with tag-based organization.
    
    Example:
        >>> cache = SolutionCache()
        >>> 
        >>> # Store a solution
        >>> cache.store(Solution(
        ...     name="parse-json",
        ...     description="Parse JSON safely",
        ...     code="def parse_json(s): return json.loads(s)",
        ...     tags=["json", "parsing"],
        ... ))
        >>> 
        >>> # Get by name
        >>> solution = cache.get("parse-json")
        >>> 
        >>> # Search by tags
        >>> results = cache.search_by_tags(["parsing"])
        >>> 
        >>> # Search by text
        >>> results = cache.search("json parsing")
    """
    
    SOLUTION_PREFIX = "solution:"
    WORKFLOW_PREFIX = "workflow:"
    TAG_INDEX_PREFIX = "tag:"
    
    def __init__(
        self,
        cache: Optional[RedisCache] = None,
        config: Optional[CacheConfig] = None,
    ):
        """
        Initialize solution cache.
        
        Args:
            cache: Redis cache instance (creates one if None)
            config: Cache configuration
        """
        self._cache = cache or RedisCache(config=config)
        self._config = config or CacheConfig.from_app_config()
    
    def store(
        self,
        solution: Solution,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Store a solution in the cache.
        
        Args:
            solution: Solution to store
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful
        """
        key = f"{self.SOLUTION_PREFIX}{solution.get_key()}"
        solution.updated_at = datetime.utcnow()
        
        # Get TTL from config if not specified
        if ttl is None:
            from agentic_assistants.config import AgenticConfig
            config = AgenticConfig()
            ttl = config.redis.solution_cache_ttl
        
        # Store the solution
        success = self._cache.set(key, solution.to_dict(), ttl=ttl)
        
        if success:
            # Update tag indices
            self._update_tag_indices(solution)
            logger.debug(f"Stored solution: {solution.name}")
        
        return success
    
    def get(
        self,
        name: str,
        project_id: Optional[str] = None,
    ) -> Optional[Solution]:
        """
        Get a solution by name.
        
        Args:
            name: Solution name
            project_id: Optional project ID for scoping
            
        Returns:
            Solution or None if not found
        """
        # Try project-scoped first if project_id provided
        if project_id:
            key = f"{self.SOLUTION_PREFIX}project:{project_id}:{name}"
            data = self._cache.get(key)
            if data:
                solution = Solution.from_dict(data)
                self._record_usage(solution)
                return solution
        
        # Try global
        key = f"{self.SOLUTION_PREFIX}global:{name}"
        data = self._cache.get(key)
        
        if data:
            solution = Solution.from_dict(data)
            self._record_usage(solution)
            return solution
        
        return None
    
    def delete(
        self,
        name: str,
        project_id: Optional[str] = None,
    ) -> bool:
        """
        Delete a solution.
        
        Args:
            name: Solution name
            project_id: Optional project ID
            
        Returns:
            True if deleted
        """
        if project_id:
            key = f"{self.SOLUTION_PREFIX}project:{project_id}:{name}"
        else:
            key = f"{self.SOLUTION_PREFIX}global:{name}"
        
        return self._cache.delete(key)
    
    def search_by_tags(
        self,
        tags: List[str],
        operator: str = "AND",
        limit: int = 50,
    ) -> List[Solution]:
        """
        Search solutions by tags.
        
        Args:
            tags: Tags to search for
            operator: "AND" or "OR"
            limit: Maximum results
            
        Returns:
            List of matching solutions
        """
        if not tags:
            return []
        
        # Get solution keys for each tag
        tag_results = []
        for tag in tags:
            key = f"{self.TAG_INDEX_PREFIX}{tag}"
            solution_keys = self._cache.get(key) or []
            tag_results.append(set(solution_keys))
        
        # Combine based on operator
        if operator == "AND":
            matching_keys = set.intersection(*tag_results) if tag_results else set()
        else:
            matching_keys = set.union(*tag_results) if tag_results else set()
        
        # Fetch solutions
        solutions = []
        for solution_key in list(matching_keys)[:limit]:
            data = self._cache.get(solution_key)
            if data:
                solutions.append(Solution.from_dict(data))
        
        # Sort by use count
        solutions.sort(key=lambda s: s.use_count, reverse=True)
        
        return solutions
    
    def search(
        self,
        query: str,
        solution_type: Optional[SolutionType] = None,
        project_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Solution]:
        """
        Search solutions by text query.
        
        This performs a simple text match on name and description.
        For semantic search, use the vector store integration.
        
        Args:
            query: Search query
            solution_type: Filter by type
            project_id: Filter by project
            limit: Maximum results
            
        Returns:
            List of matching solutions
        """
        query_lower = query.lower()
        
        # Get all solution keys
        pattern = f"{self.SOLUTION_PREFIX}*"
        keys = self._cache.get_keys(pattern)
        
        solutions = []
        for key in keys:
            if not key.startswith(self.SOLUTION_PREFIX):
                continue
            
            data = self._cache.get(key)
            if not data:
                continue
            
            solution = Solution.from_dict(data)
            
            # Apply filters
            if solution_type and solution.solution_type != solution_type:
                continue
            
            if project_id and solution.project_id != project_id and not solution.is_global:
                continue
            
            # Text match
            if query_lower in solution.name.lower() or \
               query_lower in solution.description.lower() or \
               any(query_lower in tag.lower() for tag in solution.tags):
                solutions.append(solution)
        
        # Sort by relevance (use_count as proxy)
        solutions.sort(key=lambda s: s.use_count, reverse=True)
        
        return solutions[:limit]
    
    def list_all(
        self,
        project_id: Optional[str] = None,
        include_global: bool = True,
        limit: int = 100,
    ) -> List[Solution]:
        """
        List all solutions.
        
        Args:
            project_id: Filter by project
            include_global: Include global solutions
            limit: Maximum results
            
        Returns:
            List of solutions
        """
        pattern = f"{self.SOLUTION_PREFIX}*"
        keys = self._cache.get_keys(pattern)
        
        solutions = []
        for key in keys:
            data = self._cache.get(key)
            if not data:
                continue
            
            solution = Solution.from_dict(data)
            
            # Apply project filter
            if project_id:
                if solution.project_id == project_id:
                    solutions.append(solution)
                elif include_global and solution.is_global:
                    solutions.append(solution)
            else:
                solutions.append(solution)
        
        # Sort by name
        solutions.sort(key=lambda s: s.name)
        
        return solutions[:limit]
    
    def get_tags(self) -> List[str]:
        """
        Get all tags in use.
        
        Returns:
            List of unique tags
        """
        pattern = f"{self.TAG_INDEX_PREFIX}*"
        keys = self._cache.get_keys(pattern)
        
        tags = []
        for key in keys:
            if key.startswith(self.TAG_INDEX_PREFIX):
                tag = key[len(self.TAG_INDEX_PREFIX):]
                tags.append(tag)
        
        return sorted(tags)
    
    def _update_tag_indices(self, solution: Solution):
        """Update tag indices for a solution."""
        solution_key = f"{self.SOLUTION_PREFIX}{solution.get_key()}"
        
        for tag in solution.tags:
            tag_key = f"{self.TAG_INDEX_PREFIX}{tag}"
            
            # Get existing solutions for this tag
            existing = self._cache.get(tag_key) or []
            
            # Add this solution if not present
            if solution_key not in existing:
                existing.append(solution_key)
                self._cache.set(tag_key, existing, ttl=0)  # No expiry for indices
    
    def _record_usage(self, solution: Solution):
        """Record usage of a solution."""
        solution.use_count += 1
        solution.last_used = datetime.utcnow()
        
        # Update in cache (without changing TTL)
        key = f"{self.SOLUTION_PREFIX}{solution.get_key()}"
        ttl = self._cache.get_ttl(key)
        if ttl > 0:
            self._cache.set(key, solution.to_dict(), ttl=ttl)
    
    def record_success(self, name: str, success: bool, project_id: Optional[str] = None):
        """
        Record success/failure for a solution.
        
        Args:
            name: Solution name
            success: Whether usage was successful
            project_id: Optional project ID
        """
        solution = self.get(name, project_id)
        if solution:
            # Update success rate (exponential moving average)
            alpha = 0.1
            solution.success_rate = alpha * (1.0 if success else 0.0) + \
                                   (1 - alpha) * solution.success_rate
            self.store(solution)
    
    # === Workflow State Management ===
    
    def save_workflow_state(
        self,
        state: WorkflowState,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Save workflow state.
        
        Args:
            state: Workflow state to save
            ttl: Time-to-live in seconds
            
        Returns:
            True if successful
        """
        key = f"{self.WORKFLOW_PREFIX}{state.workflow_id}"
        state.updated_at = datetime.utcnow()
        
        if ttl is None:
            from agentic_assistants.config import AgenticConfig
            config = AgenticConfig()
            ttl = config.redis.workflow_state_ttl
        
        return self._cache.set(key, state.to_dict(), ttl=ttl)
    
    def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """
        Get workflow state.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            WorkflowState or None if not found
        """
        key = f"{self.WORKFLOW_PREFIX}{workflow_id}"
        data = self._cache.get(key)
        
        if data:
            return WorkflowState.from_dict(data)
        return None
    
    def update_workflow_step(
        self,
        workflow_id: str,
        step_index: int,
        result: Any,
        status: str = "running",
    ) -> Optional[WorkflowState]:
        """
        Update workflow step progress.
        
        Args:
            workflow_id: Workflow identifier
            step_index: Current step index
            result: Result from the step
            status: Workflow status
            
        Returns:
            Updated WorkflowState or None
        """
        state = self.get_workflow_state(workflow_id)
        if not state:
            return None
        
        state.current_step = step_index
        state.results[f"step_{step_index}"] = result
        state.status = status
        state.updated_at = datetime.utcnow()
        
        if status == "completed":
            state.completed_at = datetime.utcnow()
        
        self.save_workflow_state(state)
        return state
    
    def fail_workflow(
        self,
        workflow_id: str,
        error: str,
    ) -> Optional[WorkflowState]:
        """
        Mark workflow as failed.
        
        Args:
            workflow_id: Workflow identifier
            error: Error message
            
        Returns:
            Updated WorkflowState or None
        """
        state = self.get_workflow_state(workflow_id)
        if not state:
            return None
        
        state.status = "failed"
        state.error = error
        state.updated_at = datetime.utcnow()
        
        self.save_workflow_state(state)
        return state
    
    def list_active_workflows(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> List[WorkflowState]:
        """
        List active workflows.
        
        Args:
            user_id: Filter by user
            session_id: Filter by session
            
        Returns:
            List of active WorkflowState objects
        """
        pattern = f"{self.WORKFLOW_PREFIX}*"
        keys = self._cache.get_keys(pattern)
        
        workflows = []
        for key in keys:
            data = self._cache.get(key)
            if not data:
                continue
            
            state = WorkflowState.from_dict(data)
            
            # Only include active workflows
            if state.status not in ["pending", "running"]:
                continue
            
            # Apply filters
            if user_id and state.user_id != user_id:
                continue
            if session_id and state.session_id != session_id:
                continue
            
            workflows.append(state)
        
        # Sort by creation time
        workflows.sort(key=lambda w: w.created_at, reverse=True)
        
        return workflows
    
    def get_stats(self) -> Dict[str, Any]:
        """Get solution cache statistics."""
        solutions = self.list_all(limit=1000)
        workflows = self.list_active_workflows()
        
        return {
            "total_solutions": len(solutions),
            "total_tags": len(self.get_tags()),
            "active_workflows": len(workflows),
            "cache_info": self._cache.get_info(),
            "by_type": {
                t.value: len([s for s in solutions if s.solution_type == t])
                for t in SolutionType
            },
        }
