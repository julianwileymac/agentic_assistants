"""
Lineage tracker for document provenance.

This module provides the LineageTracker class for recording and
querying document lineage information.

Example:
    >>> from agentic_assistants.lineage import LineageTracker
    >>> 
    >>> tracker = LineageTracker()
    >>> 
    >>> # Record ingestion
    >>> lineage = tracker.record_ingestion(
    ...     document_id="doc-123",
    ...     source_uri="/path/to/file.pdf",
    ...     source_type="file",
    ...     collection="documents",
    ... )
    >>> 
    >>> # Add processing step
    >>> tracker.record_step(
    ...     document_id="doc-123",
    ...     step_type="embed",
    ...     metrics={"dimension": 768},
    ... )
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.lineage.models import (
    DocumentLineage,
    LineageEvent,
    LineageQuery,
    ProcessingStep,
    ProcessingType,
    SourceType,
)
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class LineageTracker:
    """
    Tracker for document lineage and provenance.
    
    Provides methods for recording document ingestion, processing steps,
    and querying lineage history.
    
    The tracker uses SQLite for persistent storage by default.
    
    Example:
        >>> tracker = LineageTracker()
        >>> 
        >>> # Record document ingestion
        >>> lineage = tracker.record_ingestion(
        ...     document_id="doc-123",
        ...     source_uri="https://example.com/doc.pdf",
        ...     source_type="url",
        ...     collection="documents",
        ...     pipeline="document_ingestion",
        ... )
        >>> 
        >>> # Record processing step
        >>> tracker.record_step(
        ...     document_id="doc-123",
        ...     step_type="chunk",
        ...     metrics={"chunk_count": 15},
        ... )
        >>> 
        >>> # Query lineage
        >>> history = tracker.get_document_lineage("doc-123")
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        db_path: Optional[Path] = None,
    ):
        """
        Initialize lineage tracker.
        
        Args:
            config: Application configuration
            db_path: Override path for lineage database
        """
        self.config = config or AgenticConfig()
        self.db_path = db_path or self.config.data_dir / "lineage.db"
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS document_lineage (
                    document_id TEXT PRIMARY KEY,
                    source_uri TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    collection TEXT NOT NULL,
                    ingestion_pipeline TEXT,
                    ingestion_run_id TEXT,
                    ingestion_timestamp TEXT NOT NULL,
                    tags TEXT,  -- JSON array
                    metadata TEXT,  -- JSON object
                    project_id TEXT,
                    user_id TEXT,
                    version INTEGER DEFAULT 1,
                    previous_version_id TEXT,
                    is_deleted INTEGER DEFAULT 0,
                    deleted_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS processing_steps (
                    step_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    step_type TEXT NOT NULL,
                    step_name TEXT,
                    timestamp TEXT NOT NULL,
                    duration_ms REAL DEFAULT 0,
                    config TEXT,  -- JSON object
                    metrics TEXT,  -- JSON object
                    error TEXT,
                    parent_step_id TEXT,
                    FOREIGN KEY (document_id) REFERENCES document_lineage(document_id)
                );
                
                CREATE TABLE IF NOT EXISTS document_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_document_id TEXT NOT NULL,
                    child_document_id TEXT NOT NULL,
                    relationship_type TEXT DEFAULT 'chunk',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_document_id) REFERENCES document_lineage(document_id),
                    FOREIGN KEY (child_document_id) REFERENCES document_lineage(document_id)
                );
                
                CREATE TABLE IF NOT EXISTS lineage_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    details TEXT,  -- JSON object
                    FOREIGN KEY (document_id) REFERENCES document_lineage(document_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_lineage_collection ON document_lineage(collection);
                CREATE INDEX IF NOT EXISTS idx_lineage_project ON document_lineage(project_id);
                CREATE INDEX IF NOT EXISTS idx_lineage_source_type ON document_lineage(source_type);
                CREATE INDEX IF NOT EXISTS idx_steps_document ON processing_steps(document_id);
                CREATE INDEX IF NOT EXISTS idx_relationships_parent ON document_relationships(parent_document_id);
                CREATE INDEX IF NOT EXISTS idx_relationships_child ON document_relationships(child_document_id);
                CREATE INDEX IF NOT EXISTS idx_events_document ON lineage_events(document_id);
            """)
    
    def record_ingestion(
        self,
        document_id: str,
        source_uri: str,
        source_type: str = "file",
        collection: str = "default",
        pipeline: Optional[str] = None,
        run_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> DocumentLineage:
        """
        Record a document ingestion.
        
        Args:
            document_id: Unique document identifier
            source_uri: Source URI (path, URL, etc.)
            source_type: Type of source (file, url, github, etc.)
            collection: Target collection
            pipeline: Pipeline name
            run_id: Pipeline run ID
            tags: Document tags
            metadata: Additional metadata
            project_id: Project ID
            user_id: User ID
            
        Returns:
            DocumentLineage record
        """
        try:
            src_type = SourceType(source_type)
        except ValueError:
            src_type = SourceType.FILE
        
        lineage = DocumentLineage(
            document_id=document_id,
            source_uri=source_uri,
            source_type=src_type,
            collection=collection,
            ingestion_pipeline=pipeline or "",
            ingestion_run_id=run_id,
            tags=tags or [],
            metadata=metadata or {},
            project_id=project_id,
            user_id=user_id,
        )
        
        # Add initial ingestion step
        lineage.add_processing_step(
            step_type=ProcessingType.INGEST,
            step_name="Document Ingestion",
            config={"source_uri": source_uri, "source_type": source_type},
        )
        
        # Save to database
        self._save_lineage(lineage)
        
        # Record event
        self._record_event(
            event_type="created",
            document_id=document_id,
            user_id=user_id,
            details={"source_uri": source_uri, "collection": collection},
        )
        
        logger.debug(f"Recorded ingestion for document: {document_id}")
        
        return lineage
    
    def record_step(
        self,
        document_id: str,
        step_type: str,
        step_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        duration_ms: float = 0.0,
        error: Optional[str] = None,
    ) -> Optional[ProcessingStep]:
        """
        Record a processing step.
        
        Args:
            document_id: Document identifier
            step_type: Type of processing step
            step_name: Human-readable name
            config: Configuration used
            metrics: Metrics from the step
            duration_ms: Duration in milliseconds
            error: Error message if failed
            
        Returns:
            ProcessingStep or None if document not found
        """
        lineage = self.get_document_lineage(document_id)
        if not lineage:
            logger.warning(f"Document not found: {document_id}")
            return None
        
        try:
            proc_type = ProcessingType(step_type)
        except ValueError:
            proc_type = ProcessingType.TRANSFORM
        
        step = lineage.add_processing_step(
            step_type=proc_type,
            step_name=step_name or step_type,
            config=config,
            metrics=metrics,
            duration_ms=duration_ms,
        )
        
        if error:
            step.error = error
        
        # Save step to database
        self._save_step(step, document_id)
        
        return step
    
    def record_chunk_relationship(
        self,
        parent_document_id: str,
        child_document_ids: List[str],
    ):
        """
        Record parent-child relationships for chunks.
        
        Args:
            parent_document_id: Parent document ID
            child_document_ids: List of child document IDs
        """
        with sqlite3.connect(self.db_path) as conn:
            for child_id in child_document_ids:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO document_relationships
                    (parent_document_id, child_document_id, relationship_type)
                    VALUES (?, ?, 'chunk')
                    """,
                    (parent_document_id, child_id),
                )
            conn.commit()
    
    def get_document_lineage(self, document_id: str) -> Optional[DocumentLineage]:
        """
        Get lineage record for a document.
        
        Args:
            document_id: Document identifier
            
        Returns:
            DocumentLineage or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get document
            cursor = conn.execute(
                "SELECT * FROM document_lineage WHERE document_id = ?",
                (document_id,),
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Get processing steps
            steps_cursor = conn.execute(
                "SELECT * FROM processing_steps WHERE document_id = ? ORDER BY timestamp",
                (document_id,),
            )
            steps = []
            for step_row in steps_cursor:
                steps.append(ProcessingStep(
                    step_id=step_row["step_id"],
                    step_type=ProcessingType(step_row["step_type"]),
                    step_name=step_row["step_name"] or "",
                    timestamp=datetime.fromisoformat(step_row["timestamp"]),
                    duration_ms=step_row["duration_ms"] or 0,
                    config=json.loads(step_row["config"] or "{}"),
                    metrics=json.loads(step_row["metrics"] or "{}"),
                    error=step_row["error"],
                    parent_step_id=step_row["parent_step_id"],
                ))
            
            # Get relationships
            parent_cursor = conn.execute(
                "SELECT parent_document_id FROM document_relationships WHERE child_document_id = ?",
                (document_id,),
            )
            parent_documents = [r[0] for r in parent_cursor]
            
            child_cursor = conn.execute(
                "SELECT child_document_id FROM document_relationships WHERE parent_document_id = ?",
                (document_id,),
            )
            child_documents = [r[0] for r in child_cursor]
            
            # Build lineage object
            try:
                source_type = SourceType(row["source_type"])
            except ValueError:
                source_type = SourceType.FILE
            
            deleted_at = None
            if row["deleted_at"]:
                deleted_at = datetime.fromisoformat(row["deleted_at"])
            
            return DocumentLineage(
                document_id=row["document_id"],
                source_uri=row["source_uri"],
                source_type=source_type,
                collection=row["collection"],
                ingestion_pipeline=row["ingestion_pipeline"] or "",
                ingestion_run_id=row["ingestion_run_id"],
                ingestion_timestamp=datetime.fromisoformat(row["ingestion_timestamp"]),
                processing_steps=steps,
                parent_documents=parent_documents,
                child_documents=child_documents,
                tags=json.loads(row["tags"] or "[]"),
                metadata=json.loads(row["metadata"] or "{}"),
                project_id=row["project_id"],
                user_id=row["user_id"],
                version=row["version"],
                previous_version_id=row["previous_version_id"],
                is_deleted=bool(row["is_deleted"]),
                deleted_at=deleted_at,
            )
    
    def query_lineage(self, query: LineageQuery) -> List[DocumentLineage]:
        """
        Query lineage records.
        
        Args:
            query: Query parameters
            
        Returns:
            List of matching DocumentLineage records
        """
        conditions = []
        params = []
        
        if query.document_ids:
            placeholders = ",".join("?" * len(query.document_ids))
            conditions.append(f"document_id IN ({placeholders})")
            params.extend(query.document_ids)
        
        if query.collection:
            conditions.append("collection = ?")
            params.append(query.collection)
        
        if query.source_type:
            conditions.append("source_type = ?")
            params.append(query.source_type.value)
        
        if query.source_uri_pattern:
            conditions.append("source_uri LIKE ?")
            params.append(f"%{query.source_uri_pattern}%")
        
        if query.pipeline:
            conditions.append("ingestion_pipeline = ?")
            params.append(query.pipeline)
        
        if query.project_id:
            conditions.append("project_id = ?")
            params.append(query.project_id)
        
        if query.user_id:
            conditions.append("user_id = ?")
            params.append(query.user_id)
        
        if query.from_timestamp:
            conditions.append("ingestion_timestamp >= ?")
            params.append(query.from_timestamp.isoformat())
        
        if query.to_timestamp:
            conditions.append("ingestion_timestamp <= ?")
            params.append(query.to_timestamp.isoformat())
        
        if not query.include_deleted:
            conditions.append("is_deleted = 0")
        
        # Build query
        sql = "SELECT document_id FROM document_lineage"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += f" ORDER BY ingestion_timestamp DESC LIMIT ? OFFSET ?"
        params.extend([query.limit, query.offset])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(sql, params)
            document_ids = [row[0] for row in cursor]
        
        # Fetch full lineage for each document
        return [self.get_document_lineage(doc_id) for doc_id in document_ids if doc_id]
    
    def mark_deleted(self, document_id: str, user_id: Optional[str] = None) -> bool:
        """
        Mark a document as deleted.
        
        Args:
            document_id: Document identifier
            user_id: User performing deletion
            
        Returns:
            True if marked deleted
        """
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                """
                UPDATE document_lineage
                SET is_deleted = 1, deleted_at = ?, updated_at = ?
                WHERE document_id = ?
                """,
                (datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), document_id),
            )
            conn.commit()
            
            if result.rowcount > 0:
                self._record_event(
                    event_type="deleted",
                    document_id=document_id,
                    user_id=user_id,
                )
                return True
            
            return False
    
    def update_tags(
        self,
        document_id: str,
        tags: List[str],
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Update document tags.
        
        Args:
            document_id: Document identifier
            tags: New tags
            user_id: User performing update
            
        Returns:
            True if updated
        """
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                """
                UPDATE document_lineage
                SET tags = ?, updated_at = ?
                WHERE document_id = ?
                """,
                (json.dumps(tags), datetime.utcnow().isoformat(), document_id),
            )
            conn.commit()
            
            if result.rowcount > 0:
                self._record_event(
                    event_type="updated",
                    document_id=document_id,
                    user_id=user_id,
                    details={"tags": tags},
                )
                return True
            
            return False
    
    def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """
        Get statistics for a collection.
        
        Args:
            collection: Collection name
            
        Returns:
            Statistics dictionary
        """
        with sqlite3.connect(self.db_path) as conn:
            # Document count
            doc_count = conn.execute(
                "SELECT COUNT(*) FROM document_lineage WHERE collection = ? AND is_deleted = 0",
                (collection,),
            ).fetchone()[0]
            
            # Source type distribution
            source_dist = {}
            for row in conn.execute(
                """
                SELECT source_type, COUNT(*) as count
                FROM document_lineage
                WHERE collection = ? AND is_deleted = 0
                GROUP BY source_type
                """,
                (collection,),
            ):
                source_dist[row[0]] = row[1]
            
            # Processing step counts
            step_counts = {}
            for row in conn.execute(
                """
                SELECT ps.step_type, COUNT(*) as count
                FROM processing_steps ps
                JOIN document_lineage dl ON ps.document_id = dl.document_id
                WHERE dl.collection = ? AND dl.is_deleted = 0
                GROUP BY ps.step_type
                """,
                (collection,),
            ):
                step_counts[row[0]] = row[1]
            
            # Recent activity
            recent = conn.execute(
                """
                SELECT ingestion_timestamp FROM document_lineage
                WHERE collection = ? AND is_deleted = 0
                ORDER BY ingestion_timestamp DESC LIMIT 1
                """,
                (collection,),
            ).fetchone()
            
            return {
                "collection": collection,
                "document_count": doc_count,
                "source_distribution": source_dist,
                "processing_steps": step_counts,
                "last_ingestion": recent[0] if recent else None,
            }
    
    def _save_lineage(self, lineage: DocumentLineage):
        """Save lineage record to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO document_lineage
                (document_id, source_uri, source_type, collection,
                 ingestion_pipeline, ingestion_run_id, ingestion_timestamp,
                 tags, metadata, project_id, user_id, version,
                 previous_version_id, is_deleted, deleted_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lineage.document_id,
                    lineage.source_uri,
                    lineage.source_type.value,
                    lineage.collection,
                    lineage.ingestion_pipeline,
                    lineage.ingestion_run_id,
                    lineage.ingestion_timestamp.isoformat(),
                    json.dumps(lineage.tags),
                    json.dumps(lineage.metadata),
                    lineage.project_id,
                    lineage.user_id,
                    lineage.version,
                    lineage.previous_version_id,
                    1 if lineage.is_deleted else 0,
                    lineage.deleted_at.isoformat() if lineage.deleted_at else None,
                    datetime.utcnow().isoformat(),
                ),
            )
            
            # Save processing steps
            for step in lineage.processing_steps:
                self._save_step(step, lineage.document_id, conn)
            
            conn.commit()
    
    def _save_step(
        self,
        step: ProcessingStep,
        document_id: str,
        conn: Optional[sqlite3.Connection] = None,
    ):
        """Save processing step to database."""
        should_close = False
        if conn is None:
            conn = sqlite3.connect(self.db_path)
            should_close = True
        
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO processing_steps
                (step_id, document_id, step_type, step_name, timestamp,
                 duration_ms, config, metrics, error, parent_step_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    step.step_id,
                    document_id,
                    step.step_type.value,
                    step.step_name,
                    step.timestamp.isoformat(),
                    step.duration_ms,
                    json.dumps(step.config),
                    json.dumps(step.metrics),
                    step.error,
                    step.parent_step_id,
                ),
            )
            
            if should_close:
                conn.commit()
        finally:
            if should_close:
                conn.close()
    
    def _record_event(
        self,
        event_type: str,
        document_id: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Record a lineage event."""
        event = LineageEvent(
            event_type=event_type,
            document_id=document_id,
            user_id=user_id,
            details=details or {},
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO lineage_events
                (event_id, event_type, document_id, timestamp, user_id, details)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.event_type,
                    event.document_id,
                    event.timestamp.isoformat(),
                    event.user_id,
                    json.dumps(event.details),
                ),
            )
            conn.commit()


# Global tracker instance
_tracker: Optional[LineageTracker] = None


def get_lineage_tracker(config: Optional[AgenticConfig] = None) -> LineageTracker:
    """
    Get the global lineage tracker instance.
    
    Args:
        config: Optional configuration
        
    Returns:
        LineageTracker instance
    """
    global _tracker
    if _tracker is None:
        _tracker = LineageTracker(config=config)
    return _tracker
