"""
Lineage API Router.

This module provides REST endpoints for document lineage tracking,
including provenance queries, tag management, and statistics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/lineage", tags=["lineage"])


# ============================================================================
# Request/Response Models
# ============================================================================

class RecordIngestionRequest(BaseModel):
    """Request to record document ingestion."""
    document_id: str = Field(..., description="Document ID")
    source_uri: str = Field(..., description="Source URI")
    source_type: str = Field(default="file", description="Source type")
    collection: str = Field(default="default", description="Collection name")
    pipeline: Optional[str] = Field(default=None, description="Pipeline name")
    run_id: Optional[str] = Field(default=None, description="Pipeline run ID")
    tags: List[str] = Field(default_factory=list, description="Tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")
    project_id: Optional[str] = Field(default=None, description="Project ID")
    user_id: Optional[str] = Field(default=None, description="User ID")


class RecordStepRequest(BaseModel):
    """Request to record a processing step."""
    document_id: str = Field(..., description="Document ID")
    step_type: str = Field(..., description="Step type")
    step_name: Optional[str] = Field(default=None, description="Step name")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Metrics")
    duration_ms: float = Field(default=0.0, description="Duration in ms")
    error: Optional[str] = Field(default=None, description="Error message")


class ProcessingStepResponse(BaseModel):
    """Response with a processing step."""
    step_id: str
    step_type: str
    step_name: str
    timestamp: str
    duration_ms: float
    config: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class DocumentLineageResponse(BaseModel):
    """Response with document lineage."""
    document_id: str
    source_uri: str
    source_type: str
    collection: str
    ingestion_pipeline: str
    ingestion_timestamp: str
    processing_steps: List[ProcessingStepResponse] = Field(default_factory=list)
    parent_documents: List[str] = Field(default_factory=list)
    child_documents: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    version: int = 1
    is_deleted: bool = False


class LineageQueryRequest(BaseModel):
    """Request for lineage query."""
    document_ids: Optional[List[str]] = Field(default=None, description="Document IDs")
    collection: Optional[str] = Field(default=None, description="Collection filter")
    source_type: Optional[str] = Field(default=None, description="Source type filter")
    source_uri_pattern: Optional[str] = Field(default=None, description="URI pattern filter")
    pipeline: Optional[str] = Field(default=None, description="Pipeline filter")
    tags: Optional[List[str]] = Field(default=None, description="Tags filter")
    project_id: Optional[str] = Field(default=None, description="Project ID filter")
    from_timestamp: Optional[str] = Field(default=None, description="From timestamp")
    to_timestamp: Optional[str] = Field(default=None, description="To timestamp")
    include_deleted: bool = Field(default=False, description="Include deleted")
    limit: int = Field(default=100, ge=1, le=500, description="Limit")
    offset: int = Field(default=0, ge=0, description="Offset")


class TagsRequest(BaseModel):
    """Request for tag operations."""
    document_ids: List[str] = Field(..., description="Document IDs")
    tags: List[str] = Field(..., description="Tags")


class TagHierarchyRequest(BaseModel):
    """Request to set tag hierarchy."""
    child_tag: str = Field(..., description="Child tag")
    parent_tag: str = Field(..., description="Parent tag")


class TagStatsResponse(BaseModel):
    """Response with tag statistics."""
    tag: str
    document_count: int
    parent_tag: Optional[str] = None


class CollectionStatsResponse(BaseModel):
    """Response with collection statistics."""
    collection: str
    document_count: int
    source_distribution: Dict[str, int] = Field(default_factory=dict)
    processing_steps: Dict[str, int] = Field(default_factory=dict)
    last_ingestion: Optional[str] = None


# ============================================================================
# Helper Functions
# ============================================================================

def _get_tracker():
    """Get lineage tracker instance."""
    from agentic_assistants.lineage import get_lineage_tracker
    return get_lineage_tracker()


def _get_tag_manager():
    """Get tag manager instance."""
    from agentic_assistants.lineage import get_tag_manager
    return get_tag_manager()


def _lineage_to_response(lineage) -> DocumentLineageResponse:
    """Convert DocumentLineage to response model."""
    return DocumentLineageResponse(
        document_id=lineage.document_id,
        source_uri=lineage.source_uri,
        source_type=lineage.source_type.value if hasattr(lineage.source_type, 'value') else str(lineage.source_type),
        collection=lineage.collection,
        ingestion_pipeline=lineage.ingestion_pipeline,
        ingestion_timestamp=lineage.ingestion_timestamp.isoformat(),
        processing_steps=[
            ProcessingStepResponse(
                step_id=s.step_id,
                step_type=s.step_type.value if hasattr(s.step_type, 'value') else str(s.step_type),
                step_name=s.step_name,
                timestamp=s.timestamp.isoformat(),
                duration_ms=s.duration_ms,
                config=s.config,
                metrics=s.metrics,
                error=s.error,
            )
            for s in lineage.processing_steps
        ],
        parent_documents=lineage.parent_documents,
        child_documents=lineage.child_documents,
        tags=lineage.tags,
        metadata=lineage.metadata,
        project_id=lineage.project_id,
        user_id=lineage.user_id,
        version=lineage.version,
        is_deleted=lineage.is_deleted,
    )


# ============================================================================
# Lineage Endpoints
# ============================================================================

@router.post("/record", response_model=DocumentLineageResponse)
async def record_ingestion(request: RecordIngestionRequest) -> DocumentLineageResponse:
    """Record a document ingestion."""
    try:
        tracker = _get_tracker()
        
        lineage = tracker.record_ingestion(
            document_id=request.document_id,
            source_uri=request.source_uri,
            source_type=request.source_type,
            collection=request.collection,
            pipeline=request.pipeline,
            run_id=request.run_id,
            tags=request.tags,
            metadata=request.metadata,
            project_id=request.project_id,
            user_id=request.user_id,
        )
        
        return _lineage_to_response(lineage)
        
    except Exception as e:
        logger.error(f"Error recording ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/step", response_model=ProcessingStepResponse)
async def record_step(request: RecordStepRequest) -> ProcessingStepResponse:
    """Record a processing step."""
    try:
        tracker = _get_tracker()
        
        step = tracker.record_step(
            document_id=request.document_id,
            step_type=request.step_type,
            step_name=request.step_name,
            config=request.config,
            metrics=request.metrics,
            duration_ms=request.duration_ms,
            error=request.error,
        )
        
        if not step:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return ProcessingStepResponse(
            step_id=step.step_id,
            step_type=step.step_type.value if hasattr(step.step_type, 'value') else str(step.step_type),
            step_name=step.step_name,
            timestamp=step.timestamp.isoformat(),
            duration_ms=step.duration_ms,
            config=step.config,
            metrics=step.metrics,
            error=step.error,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording step: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{document_id}", response_model=DocumentLineageResponse)
async def get_document_lineage(document_id: str) -> DocumentLineageResponse:
    """Get lineage for a document."""
    try:
        tracker = _get_tracker()
        lineage = tracker.get_document_lineage(document_id)
        
        if not lineage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return _lineage_to_response(lineage)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lineage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=List[DocumentLineageResponse])
async def query_lineage(request: LineageQueryRequest) -> List[DocumentLineageResponse]:
    """Query lineage records."""
    try:
        from agentic_assistants.lineage.models import LineageQuery, SourceType
        
        tracker = _get_tracker()
        
        # Parse source type
        source_type = None
        if request.source_type:
            try:
                source_type = SourceType(request.source_type)
            except ValueError:
                pass
        
        # Parse timestamps
        from_ts = None
        if request.from_timestamp:
            from_ts = datetime.fromisoformat(request.from_timestamp)
        
        to_ts = None
        if request.to_timestamp:
            to_ts = datetime.fromisoformat(request.to_timestamp)
        
        query = LineageQuery(
            document_ids=request.document_ids,
            collection=request.collection,
            source_type=source_type,
            source_uri_pattern=request.source_uri_pattern,
            pipeline=request.pipeline,
            tags=request.tags,
            project_id=request.project_id,
            from_timestamp=from_ts,
            to_timestamp=to_ts,
            include_deleted=request.include_deleted,
            limit=request.limit,
            offset=request.offset,
        )
        
        results = tracker.query_lineage(query)
        
        return [_lineage_to_response(r) for r in results if r]
        
    except Exception as e:
        logger.error(f"Error querying lineage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/document/{document_id}")
async def mark_document_deleted(
    document_id: str,
    user_id: Optional[str] = Query(None, description="User ID"),
) -> Dict[str, Any]:
    """Mark a document as deleted."""
    try:
        tracker = _get_tracker()
        success = tracker.mark_deleted(document_id, user_id)
        
        return {
            "success": success,
            "document_id": document_id,
        }
        
    except Exception as e:
        logger.error(f"Error marking document deleted: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collection/{collection}/stats", response_model=CollectionStatsResponse)
async def get_collection_stats(collection: str) -> CollectionStatsResponse:
    """Get statistics for a collection."""
    try:
        tracker = _get_tracker()
        stats = tracker.get_collection_stats(collection)
        
        return CollectionStatsResponse(
            collection=stats["collection"],
            document_count=stats["document_count"],
            source_distribution=stats["source_distribution"],
            processing_steps=stats["processing_steps"],
            last_ingestion=stats.get("last_ingestion"),
        )
        
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Tag Endpoints
# ============================================================================

@router.post("/tags/add")
async def add_tags(request: TagsRequest) -> Dict[str, Any]:
    """Add tags to documents."""
    try:
        tag_manager = _get_tag_manager()
        count = tag_manager.add_tags(request.document_ids, request.tags)
        
        return {
            "success": True,
            "tags_added": count,
            "document_count": len(request.document_ids),
        }
        
    except Exception as e:
        logger.error(f"Error adding tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tags/remove")
async def remove_tags(request: TagsRequest) -> Dict[str, Any]:
    """Remove tags from documents."""
    try:
        tag_manager = _get_tag_manager()
        count = tag_manager.remove_tags(request.document_ids, request.tags)
        
        return {
            "success": True,
            "tags_removed": count,
        }
        
    except Exception as e:
        logger.error(f"Error removing tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags/document/{document_id}")
async def get_document_tags(document_id: str) -> Dict[str, Any]:
    """Get tags for a document."""
    try:
        tag_manager = _get_tag_manager()
        tags = tag_manager.get_document_tags(document_id)
        
        return {
            "document_id": document_id,
            "tags": tags,
        }
        
    except Exception as e:
        logger.error(f"Error getting document tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags/search")
async def search_by_tags(
    tags: List[str] = Query(..., description="Tags to search for"),
    operator: str = Query("AND", description="AND or OR"),
    include_children: bool = Query(True, description="Include child tags"),
    collection: Optional[str] = Query(None, description="Collection filter"),
    project_id: Optional[str] = Query(None, description="Project ID filter"),
    limit: int = Query(100, ge=1, le=500, description="Limit"),
) -> Dict[str, Any]:
    """Search documents by tags."""
    try:
        tag_manager = _get_tag_manager()
        document_ids = tag_manager.search_by_tags(
            tags=tags,
            operator=operator,
            include_children=include_children,
            collection=collection,
            project_id=project_id,
            limit=limit,
        )
        
        return {
            "tags": tags,
            "operator": operator,
            "document_ids": document_ids,
            "count": len(document_ids),
        }
        
    except Exception as e:
        logger.error(f"Error searching by tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tags/hierarchy")
async def set_tag_hierarchy(request: TagHierarchyRequest) -> Dict[str, Any]:
    """Set parent-child relationship between tags."""
    try:
        tag_manager = _get_tag_manager()
        success = tag_manager.set_parent_tag(request.child_tag, request.parent_tag)
        
        return {
            "success": success,
            "child_tag": request.child_tag,
            "parent_tag": request.parent_tag,
        }
        
    except Exception as e:
        logger.error(f"Error setting tag hierarchy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tags/hierarchy")
async def remove_tag_hierarchy(
    child_tag: str = Query(..., description="Child tag"),
    parent_tag: str = Query(..., description="Parent tag"),
) -> Dict[str, Any]:
    """Remove parent-child relationship between tags."""
    try:
        tag_manager = _get_tag_manager()
        success = tag_manager.remove_parent_tag(child_tag, parent_tag)
        
        return {
            "success": success,
            "child_tag": child_tag,
            "parent_tag": parent_tag,
        }
        
    except Exception as e:
        logger.error(f"Error removing tag hierarchy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags/hierarchy")
async def get_tag_hierarchy() -> Dict[str, Any]:
    """Get the complete tag hierarchy."""
    try:
        tag_manager = _get_tag_manager()
        hierarchy = tag_manager.get_tag_hierarchy()
        
        return {
            "hierarchy": hierarchy,
        }
        
    except Exception as e:
        logger.error(f"Error getting tag hierarchy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags")
async def get_all_tags() -> Dict[str, Any]:
    """Get all tags."""
    try:
        tag_manager = _get_tag_manager()
        tags = tag_manager.get_all_tags()
        
        return {
            "tags": tags,
            "count": len(tags),
        }
        
    except Exception as e:
        logger.error(f"Error getting tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags/stats", response_model=List[TagStatsResponse])
async def get_tag_stats() -> List[TagStatsResponse]:
    """Get tag statistics."""
    try:
        tag_manager = _get_tag_manager()
        stats = tag_manager.get_tag_stats()
        
        return [
            TagStatsResponse(
                tag=s["tag"],
                document_count=s["document_count"],
                parent_tag=s.get("parent_tag"),
            )
            for s in stats
        ]
        
    except Exception as e:
        logger.error(f"Error getting tag stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
