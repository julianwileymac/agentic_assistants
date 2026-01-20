"""
Lineage tracking module for Agentic Assistants.

This module provides document lineage tracking for knowledge bases
and vector stores, enabling provenance tracking and audit trails.

Example:
    >>> from agentic_assistants.lineage import LineageTracker, DocumentLineage
    >>> 
    >>> tracker = LineageTracker()
    >>> 
    >>> # Record document ingestion
    >>> lineage = tracker.record_ingestion(
    ...     document_id="doc-123",
    ...     source_uri="https://example.com/doc.pdf",
    ...     pipeline="document_ingestion",
    ... )
    >>> 
    >>> # Query lineage
    >>> history = tracker.get_document_lineage("doc-123")
    >>> 
    >>> # Tag management
    >>> from agentic_assistants.lineage import TagManager
    >>> tags = TagManager()
    >>> tags.add_tags(["doc-123"], ["python", "tutorial"])
"""

from agentic_assistants.lineage.models import (
    DocumentLineage,
    ProcessingStep,
    LineageQuery,
    LineageEvent,
    SourceType,
    ProcessingType,
)
from agentic_assistants.lineage.tracker import (
    LineageTracker,
    get_lineage_tracker,
)
from agentic_assistants.lineage.tags import (
    TagManager,
    get_tag_manager,
)

__all__ = [
    # Models
    "DocumentLineage",
    "ProcessingStep",
    "LineageQuery",
    "LineageEvent",
    "SourceType",
    "ProcessingType",
    # Tracker
    "LineageTracker",
    "get_lineage_tracker",
    # Tags
    "TagManager",
    "get_tag_manager",
]
