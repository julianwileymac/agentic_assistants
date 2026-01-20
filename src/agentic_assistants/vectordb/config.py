"""
Vector store configuration with multi-level scoping.

This module provides scope-aware configuration for vector stores,
supporting global, user, project, and experiment-level collections.

Example:
    >>> from agentic_assistants.vectordb.config import (
    ...     VectorStoreScope,
    ...     ScopedVectorConfig,
    ...     get_collection_name,
    ... )
    >>> 
    >>> # Get a project-scoped collection name
    >>> name = get_collection_name("my-docs", VectorStoreScope.PROJECT, project_id="proj-123")
    >>> print(name)  # "project_proj-123_my-docs"
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class VectorStoreScope(str, Enum):
    """
    Vector store scope hierarchy.
    
    Scopes determine the visibility and isolation of vector collections:
    - GLOBAL: Shared across all projects and users (e.g., framework docs)
    - USER: User-specific collections, isolated per user
    - PROJECT: Project-specific collections
    - EXPERIMENT: MLflow experiment-linked collections for ML workflows
    """
    
    GLOBAL = "global"
    USER = "user"
    PROJECT = "project"
    EXPERIMENT = "experiment"


class CollectionConfig(BaseModel):
    """Configuration for a vector store collection."""
    
    name: str = Field(..., description="Collection name")
    scope: VectorStoreScope = Field(
        default=VectorStoreScope.PROJECT,
        description="Collection scope",
    )
    embedding_model: Optional[str] = Field(
        default=None,
        description="Embedding model override for this collection",
    )
    embedding_dimension: Optional[int] = Field(
        default=None,
        description="Embedding dimension override",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Collection metadata",
    )
    description: str = Field(default="", description="Collection description")
    
    # Lineage tracking
    track_lineage: bool = Field(
        default=True,
        description="Track document lineage for this collection",
    )
    
    # Access control
    read_only: bool = Field(
        default=False,
        description="Whether this collection is read-only",
    )


class ScopedVectorConfig(BaseModel):
    """
    Configuration for scoped vector store operations.
    
    This configuration determines how collections are named and organized
    based on their scope (global, user, project, experiment).
    """
    
    # Backend configuration
    default_backend: str = Field(
        default="lancedb",
        description="Default vector store backend",
    )
    
    # Default embedding settings
    default_embedding_model: str = Field(
        default="nomic-embed-text",
        description="Default embedding model",
    )
    default_embedding_dimension: int = Field(
        default=768,
        description="Default embedding dimension",
    )
    
    # Namespace templates for different scopes
    global_namespace: str = Field(
        default="global",
        description="Namespace prefix for global collections",
    )
    user_namespace_template: str = Field(
        default="user_{user_id}",
        description="Template for user-scoped collection namespaces",
    )
    project_namespace_template: str = Field(
        default="project_{project_id}",
        description="Template for project-scoped collection namespaces",
    )
    experiment_namespace_template: str = Field(
        default="exp_{experiment_id}",
        description="Template for experiment-scoped collection namespaces",
    )
    
    # Pre-configured global collections
    global_collections: List[CollectionConfig] = Field(
        default_factory=list,
        description="Pre-configured global collections",
    )
    
    # Storage paths per scope
    global_path: Optional[Path] = Field(
        default=None,
        description="Path for global vector storage",
    )
    user_path_template: str = Field(
        default="./users/{user_id}/vectors",
        description="Path template for user vector storage",
    )
    project_path_template: str = Field(
        default="./data/projects/{project_id}/vectors",
        description="Path template for project vector storage",
    )
    
    # Feature flags
    enable_cross_scope_search: bool = Field(
        default=False,
        description="Allow searching across multiple scopes",
    )
    enable_scope_inheritance: bool = Field(
        default=True,
        description="Project collections inherit from global collections in search",
    )
    
    def get_namespace(
        self,
        scope: VectorStoreScope,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        experiment_id: Optional[str] = None,
    ) -> str:
        """
        Get the namespace for a given scope.
        
        Args:
            scope: The vector store scope
            user_id: User ID (required for USER scope)
            project_id: Project ID (required for PROJECT scope)
            experiment_id: Experiment ID (required for EXPERIMENT scope)
            
        Returns:
            Namespace string
            
        Raises:
            ValueError: If required ID is missing for scope
        """
        if scope == VectorStoreScope.GLOBAL:
            return self.global_namespace
        
        elif scope == VectorStoreScope.USER:
            if not user_id:
                raise ValueError("user_id required for USER scope")
            return self.user_namespace_template.format(user_id=user_id)
        
        elif scope == VectorStoreScope.PROJECT:
            if not project_id:
                raise ValueError("project_id required for PROJECT scope")
            return self.project_namespace_template.format(project_id=project_id)
        
        elif scope == VectorStoreScope.EXPERIMENT:
            if not experiment_id:
                raise ValueError("experiment_id required for EXPERIMENT scope")
            return self.experiment_namespace_template.format(experiment_id=experiment_id)
        
        else:
            raise ValueError(f"Unknown scope: {scope}")
    
    def get_storage_path(
        self,
        scope: VectorStoreScope,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        base_path: Optional[Path] = None,
    ) -> Path:
        """
        Get the storage path for a given scope.
        
        Args:
            scope: The vector store scope
            user_id: User ID (for USER scope)
            project_id: Project ID (for PROJECT scope)
            base_path: Override base path
            
        Returns:
            Storage path
        """
        if scope == VectorStoreScope.GLOBAL:
            if self.global_path:
                return self.global_path
            return base_path or Path("./data/vectors/global")
        
        elif scope == VectorStoreScope.USER:
            if not user_id:
                raise ValueError("user_id required for USER scope")
            return Path(self.user_path_template.format(user_id=user_id))
        
        elif scope == VectorStoreScope.PROJECT:
            if not project_id:
                raise ValueError("project_id required for PROJECT scope")
            return Path(self.project_path_template.format(project_id=project_id))
        
        elif scope == VectorStoreScope.EXPERIMENT:
            # Experiments use project path with experiment subfolder
            if project_id:
                base = Path(self.project_path_template.format(project_id=project_id))
            else:
                base = base_path or Path("./data/vectors")
            return base / "experiments"
        
        else:
            return base_path or Path("./data/vectors")


@dataclass
class VectorStoreContext:
    """
    Context for vector store operations.
    
    This context carries scope information for vector store operations,
    allowing the store to properly namespace and isolate collections.
    """
    
    scope: VectorStoreScope = VectorStoreScope.PROJECT
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    experiment_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Additional context
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Tracking
    track_lineage: bool = True
    track_metrics: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "scope": self.scope.value,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "experiment_id": self.experiment_id,
            "session_id": self.session_id,
            "tags": self.tags,
            "metadata": self.metadata,
            "track_lineage": self.track_lineage,
            "track_metrics": self.track_metrics,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorStoreContext":
        """Create context from dictionary."""
        scope_str = data.get("scope", "project")
        scope = VectorStoreScope(scope_str) if isinstance(scope_str, str) else scope_str
        
        return cls(
            scope=scope,
            user_id=data.get("user_id"),
            project_id=data.get("project_id"),
            experiment_id=data.get("experiment_id"),
            session_id=data.get("session_id"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            track_lineage=data.get("track_lineage", True),
            track_metrics=data.get("track_metrics", True),
        )
    
    @classmethod
    def global_context(cls) -> "VectorStoreContext":
        """Create a global scope context."""
        return cls(scope=VectorStoreScope.GLOBAL)
    
    @classmethod
    def user_context(cls, user_id: str) -> "VectorStoreContext":
        """Create a user scope context."""
        return cls(scope=VectorStoreScope.USER, user_id=user_id)
    
    @classmethod
    def project_context(
        cls,
        project_id: str,
        user_id: Optional[str] = None,
    ) -> "VectorStoreContext":
        """Create a project scope context."""
        return cls(
            scope=VectorStoreScope.PROJECT,
            project_id=project_id,
            user_id=user_id,
        )
    
    @classmethod
    def experiment_context(
        cls,
        experiment_id: str,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> "VectorStoreContext":
        """Create an experiment scope context."""
        return cls(
            scope=VectorStoreScope.EXPERIMENT,
            experiment_id=experiment_id,
            project_id=project_id,
            user_id=user_id,
        )


def get_collection_name(
    base_name: str,
    scope: VectorStoreScope,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    experiment_id: Optional[str] = None,
    config: Optional[ScopedVectorConfig] = None,
) -> str:
    """
    Get a fully-qualified collection name for a given scope.
    
    Args:
        base_name: Base collection name
        scope: Vector store scope
        user_id: User ID (for USER scope)
        project_id: Project ID (for PROJECT scope)
        experiment_id: Experiment ID (for EXPERIMENT scope)
        config: Optional scoped vector config
        
    Returns:
        Fully-qualified collection name
        
    Example:
        >>> get_collection_name("docs", VectorStoreScope.PROJECT, project_id="proj-123")
        "project_proj-123_docs"
    """
    if config is None:
        config = ScopedVectorConfig()
    
    namespace = config.get_namespace(
        scope=scope,
        user_id=user_id,
        project_id=project_id,
        experiment_id=experiment_id,
    )
    
    # Sanitize base name
    safe_name = base_name.replace(" ", "_").replace("-", "_").lower()
    
    return f"{namespace}_{safe_name}"


def parse_collection_name(collection_name: str) -> Dict[str, Any]:
    """
    Parse a collection name to extract scope and identifiers.
    
    Args:
        collection_name: Fully-qualified collection name
        
    Returns:
        Dictionary with scope and identifier information
    """
    parts = collection_name.split("_")
    
    result = {
        "scope": VectorStoreScope.PROJECT,
        "user_id": None,
        "project_id": None,
        "experiment_id": None,
        "base_name": collection_name,
    }
    
    if parts[0] == "global":
        result["scope"] = VectorStoreScope.GLOBAL
        result["base_name"] = "_".join(parts[1:]) if len(parts) > 1 else ""
    
    elif parts[0] == "user" and len(parts) >= 2:
        result["scope"] = VectorStoreScope.USER
        result["user_id"] = parts[1]
        result["base_name"] = "_".join(parts[2:]) if len(parts) > 2 else ""
    
    elif parts[0] == "project" and len(parts) >= 2:
        result["scope"] = VectorStoreScope.PROJECT
        result["project_id"] = parts[1]
        result["base_name"] = "_".join(parts[2:]) if len(parts) > 2 else ""
    
    elif parts[0] == "exp" and len(parts) >= 2:
        result["scope"] = VectorStoreScope.EXPERIMENT
        result["experiment_id"] = parts[1]
        result["base_name"] = "_".join(parts[2:]) if len(parts) > 2 else ""
    
    return result
