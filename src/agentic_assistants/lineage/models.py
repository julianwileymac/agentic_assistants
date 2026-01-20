"""
Data models for document lineage tracking.

This module defines the data structures for tracking document
provenance, processing history, and relationships.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class SourceType(str, Enum):
    """Types of document sources."""
    
    FILE = "file"           # Local file upload
    URL = "url"             # Web URL
    GITHUB = "github"       # GitHub repository
    S3 = "s3"               # S3/MinIO storage
    API = "api"             # API endpoint
    DATABASE = "database"   # Database query
    MANUAL = "manual"       # Manual entry
    GENERATED = "generated" # AI generated


class ProcessingType(str, Enum):
    """Types of processing steps."""
    
    INGEST = "ingest"       # Initial ingestion
    CHUNK = "chunk"         # Text chunking
    EMBED = "embed"         # Embedding generation
    AUGMENT = "augment"     # Content augmentation
    ANNOTATE = "annotate"   # Metadata annotation
    TRANSFORM = "transform" # Data transformation
    INDEX = "index"         # Vector indexing
    UPDATE = "update"       # Content update
    DELETE = "delete"       # Content deletion


@dataclass
class ProcessingStep:
    """
    A single processing step in document lineage.
    
    Attributes:
        step_id: Unique step identifier
        step_type: Type of processing
        step_name: Human-readable name
        timestamp: When the step occurred
        duration_ms: Processing duration in milliseconds
        config: Configuration used for this step
        metrics: Metrics from the step (e.g., chunk count)
        error: Error message if step failed
        parent_step_id: ID of parent step (for chained processing)
    """
    
    step_id: str = field(default_factory=lambda: str(uuid4()))
    step_type: ProcessingType = ProcessingType.INGEST
    step_name: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    parent_step_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "step_type": self.step_type.value,
            "step_name": self.step_name,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "config": self.config,
            "metrics": self.metrics,
            "error": self.error,
            "parent_step_id": self.parent_step_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessingStep":
        """Create from dictionary."""
        step_type = data.get("step_type", "ingest")
        if isinstance(step_type, str):
            step_type = ProcessingType(step_type)
        
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.utcnow()
        
        return cls(
            step_id=data.get("step_id", str(uuid4())),
            step_type=step_type,
            step_name=data.get("step_name", ""),
            timestamp=timestamp,
            duration_ms=data.get("duration_ms", 0.0),
            config=data.get("config", {}),
            metrics=data.get("metrics", {}),
            error=data.get("error"),
            parent_step_id=data.get("parent_step_id"),
        )


@dataclass
class DocumentLineage:
    """
    Complete lineage record for a document.
    
    Attributes:
        document_id: Unique document identifier
        source_uri: Original source URI
        source_type: Type of source
        collection: Vector store collection
        ingestion_pipeline: Pipeline that ingested the document
        ingestion_run_id: Pipeline run identifier
        ingestion_timestamp: When document was first ingested
        processing_steps: List of processing steps
        parent_documents: Parent document IDs (for chunks)
        child_documents: Child document IDs (chunks created from this)
        tags: Document tags
        metadata: Additional metadata
        project_id: Associated project
        user_id: User who ingested
        version: Document version
        is_deleted: Whether document has been deleted
    """
    
    document_id: str = field(default_factory=lambda: str(uuid4()))
    source_uri: str = ""
    source_type: SourceType = SourceType.FILE
    collection: str = "default"
    
    # Pipeline info
    ingestion_pipeline: str = ""
    ingestion_run_id: Optional[str] = None
    ingestion_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Processing history
    processing_steps: List[ProcessingStep] = field(default_factory=list)
    
    # Relationships
    parent_documents: List[str] = field(default_factory=list)
    child_documents: List[str] = field(default_factory=list)
    
    # Organization
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Scoping
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Versioning
    version: int = 1
    previous_version_id: Optional[str] = None
    
    # Status
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "source_uri": self.source_uri,
            "source_type": self.source_type.value,
            "collection": self.collection,
            "ingestion_pipeline": self.ingestion_pipeline,
            "ingestion_run_id": self.ingestion_run_id,
            "ingestion_timestamp": self.ingestion_timestamp.isoformat(),
            "processing_steps": [s.to_dict() for s in self.processing_steps],
            "parent_documents": self.parent_documents,
            "child_documents": self.child_documents,
            "tags": self.tags,
            "metadata": self.metadata,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "version": self.version,
            "previous_version_id": self.previous_version_id,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentLineage":
        """Create from dictionary."""
        source_type = data.get("source_type", "file")
        if isinstance(source_type, str):
            source_type = SourceType(source_type)
        
        ingestion_timestamp = data.get("ingestion_timestamp")
        if isinstance(ingestion_timestamp, str):
            ingestion_timestamp = datetime.fromisoformat(ingestion_timestamp)
        elif ingestion_timestamp is None:
            ingestion_timestamp = datetime.utcnow()
        
        deleted_at = data.get("deleted_at")
        if isinstance(deleted_at, str):
            deleted_at = datetime.fromisoformat(deleted_at)
        
        processing_steps = [
            ProcessingStep.from_dict(s) if isinstance(s, dict) else s
            for s in data.get("processing_steps", [])
        ]
        
        return cls(
            document_id=data.get("document_id", str(uuid4())),
            source_uri=data.get("source_uri", ""),
            source_type=source_type,
            collection=data.get("collection", "default"),
            ingestion_pipeline=data.get("ingestion_pipeline", ""),
            ingestion_run_id=data.get("ingestion_run_id"),
            ingestion_timestamp=ingestion_timestamp,
            processing_steps=processing_steps,
            parent_documents=data.get("parent_documents", []),
            child_documents=data.get("child_documents", []),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            project_id=data.get("project_id"),
            user_id=data.get("user_id"),
            version=data.get("version", 1),
            previous_version_id=data.get("previous_version_id"),
            is_deleted=data.get("is_deleted", False),
            deleted_at=deleted_at,
        )
    
    def add_processing_step(
        self,
        step_type: ProcessingType,
        step_name: str = "",
        config: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        duration_ms: float = 0.0,
    ) -> ProcessingStep:
        """Add a processing step to the lineage."""
        step = ProcessingStep(
            step_type=step_type,
            step_name=step_name or step_type.value,
            config=config or {},
            metrics=metrics or {},
            duration_ms=duration_ms,
            parent_step_id=self.processing_steps[-1].step_id if self.processing_steps else None,
        )
        self.processing_steps.append(step)
        return step
    
    def get_latest_step(self) -> Optional[ProcessingStep]:
        """Get the most recent processing step."""
        return self.processing_steps[-1] if self.processing_steps else None


@dataclass
class LineageEvent:
    """
    An event in the lineage system.
    
    Used for logging and audit trails.
    """
    
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = ""  # created, updated, deleted, accessed
    document_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "document_id": self.document_id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "details": self.details,
        }


@dataclass
class LineageQuery:
    """
    Query parameters for lineage search.
    """
    
    document_ids: Optional[List[str]] = None
    collection: Optional[str] = None
    source_type: Optional[SourceType] = None
    source_uri_pattern: Optional[str] = None
    pipeline: Optional[str] = None
    tags: Optional[List[str]] = None
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    from_timestamp: Optional[datetime] = None
    to_timestamp: Optional[datetime] = None
    include_deleted: bool = False
    limit: int = 100
    offset: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_ids": self.document_ids,
            "collection": self.collection,
            "source_type": self.source_type.value if self.source_type else None,
            "source_uri_pattern": self.source_uri_pattern,
            "pipeline": self.pipeline,
            "tags": self.tags,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "from_timestamp": self.from_timestamp.isoformat() if self.from_timestamp else None,
            "to_timestamp": self.to_timestamp.isoformat() if self.to_timestamp else None,
            "include_deleted": self.include_deleted,
            "limit": self.limit,
            "offset": self.offset,
        }
