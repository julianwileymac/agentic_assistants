"""
Tag management for documents and knowledge bases.

This module provides hierarchical tagging support for organizing
and querying documents in the knowledge base.

Example:
    >>> from agentic_assistants.lineage import TagManager
    >>> 
    >>> manager = TagManager()
    >>> 
    >>> # Add tags to documents
    >>> manager.add_tags(["doc-123", "doc-456"], ["python", "tutorial"])
    >>> 
    >>> # Create tag hierarchy
    >>> manager.set_parent_tag("python", "programming")
    >>> 
    >>> # Search by tags
    >>> docs = manager.search_by_tags(["python"], operator="AND")
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class TagManager:
    """
    Manager for document tags with hierarchical support.
    
    Provides methods for adding, removing, and querying tags on documents,
    as well as managing tag hierarchies for categorization.
    
    Example:
        >>> manager = TagManager()
        >>> 
        >>> # Tag documents
        >>> manager.add_tags(["doc-1", "doc-2"], ["python", "data-science"])
        >>> 
        >>> # Create hierarchy: data-science is under machine-learning
        >>> manager.set_parent_tag("data-science", "machine-learning")
        >>> 
        >>> # Search - finds all docs with "python" AND "data-science"
        >>> docs = manager.search_by_tags(["python", "data-science"])
        >>> 
        >>> # Get tag stats
        >>> stats = manager.get_tag_stats()
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        db_path: Optional[Path] = None,
    ):
        """
        Initialize tag manager.
        
        Args:
            config: Application configuration
            db_path: Override path for tag database
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
                -- Document tags table
                CREATE TABLE IF NOT EXISTS document_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    UNIQUE(document_id, tag)
                );
                
                -- Tag hierarchy for nested tags
                CREATE TABLE IF NOT EXISTS tag_hierarchy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_tag TEXT NOT NULL,
                    child_tag TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(parent_tag, child_tag)
                );
                
                -- Tag metadata
                CREATE TABLE IF NOT EXISTS tag_metadata (
                    tag TEXT PRIMARY KEY,
                    description TEXT,
                    color TEXT,
                    icon TEXT,
                    metadata TEXT,  -- JSON
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Indexes
                CREATE INDEX IF NOT EXISTS idx_doc_tags_document ON document_tags(document_id);
                CREATE INDEX IF NOT EXISTS idx_doc_tags_tag ON document_tags(tag);
                CREATE INDEX IF NOT EXISTS idx_tag_hierarchy_parent ON tag_hierarchy(parent_tag);
                CREATE INDEX IF NOT EXISTS idx_tag_hierarchy_child ON tag_hierarchy(child_tag);
            """)
    
    def add_tags(
        self,
        document_ids: List[str],
        tags: List[str],
        created_by: Optional[str] = None,
    ) -> int:
        """
        Add tags to documents.
        
        Args:
            document_ids: List of document IDs
            tags: List of tags to add
            created_by: User who added the tags
            
        Returns:
            Number of tags added
        """
        # Normalize tags
        normalized_tags = [self._normalize_tag(t) for t in tags if t]
        
        if not document_ids or not normalized_tags:
            return 0
        
        count = 0
        with sqlite3.connect(self.db_path) as conn:
            for doc_id in document_ids:
                for tag in normalized_tags:
                    try:
                        conn.execute(
                            """
                            INSERT OR IGNORE INTO document_tags
                            (document_id, tag, created_by)
                            VALUES (?, ?, ?)
                            """,
                            (doc_id, tag, created_by),
                        )
                        count += conn.total_changes
                    except Exception as e:
                        logger.error(f"Error adding tag {tag} to {doc_id}: {e}")
            conn.commit()
        
        logger.debug(f"Added {count} tags to {len(document_ids)} documents")
        return count
    
    def remove_tags(
        self,
        document_ids: List[str],
        tags: List[str],
    ) -> int:
        """
        Remove tags from documents.
        
        Args:
            document_ids: List of document IDs
            tags: List of tags to remove
            
        Returns:
            Number of tags removed
        """
        normalized_tags = [self._normalize_tag(t) for t in tags if t]
        
        if not document_ids or not normalized_tags:
            return 0
        
        with sqlite3.connect(self.db_path) as conn:
            placeholders_docs = ",".join("?" * len(document_ids))
            placeholders_tags = ",".join("?" * len(normalized_tags))
            
            result = conn.execute(
                f"""
                DELETE FROM document_tags
                WHERE document_id IN ({placeholders_docs})
                AND tag IN ({placeholders_tags})
                """,
                document_ids + normalized_tags,
            )
            conn.commit()
            
            return result.rowcount
    
    def get_document_tags(self, document_id: str) -> List[str]:
        """
        Get all tags for a document.
        
        Args:
            document_id: Document identifier
            
        Returns:
            List of tags
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT tag FROM document_tags WHERE document_id = ? ORDER BY tag",
                (document_id,),
            )
            return [row[0] for row in cursor]
    
    def search_by_tags(
        self,
        tags: List[str],
        operator: str = "AND",
        include_children: bool = True,
        collection: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[str]:
        """
        Search for documents by tags.
        
        Args:
            tags: Tags to search for
            operator: "AND" (all tags) or "OR" (any tag)
            include_children: Include child tags in search
            collection: Filter by collection
            project_id: Filter by project
            limit: Maximum results
            
        Returns:
            List of document IDs
        """
        normalized_tags = [self._normalize_tag(t) for t in tags if t]
        
        if not normalized_tags:
            return []
        
        # Expand tags to include children if requested
        search_tags = set(normalized_tags)
        if include_children:
            for tag in normalized_tags:
                children = self._get_child_tags(tag, recursive=True)
                search_tags.update(children)
        
        with sqlite3.connect(self.db_path) as conn:
            if operator.upper() == "AND":
                # Documents must have ALL tags
                placeholders = ",".join("?" * len(search_tags))
                
                # Join with lineage table if filtering by collection/project
                if collection or project_id:
                    sql = f"""
                        SELECT dt.document_id
                        FROM document_tags dt
                        JOIN document_lineage dl ON dt.document_id = dl.document_id
                        WHERE dt.tag IN ({placeholders})
                    """
                    params = list(search_tags)
                    
                    if collection:
                        sql += " AND dl.collection = ?"
                        params.append(collection)
                    if project_id:
                        sql += " AND dl.project_id = ?"
                        params.append(project_id)
                    
                    sql += f"""
                        AND dl.is_deleted = 0
                        GROUP BY dt.document_id
                        HAVING COUNT(DISTINCT dt.tag) >= ?
                        LIMIT ?
                    """
                    params.extend([len(normalized_tags), limit])
                else:
                    sql = f"""
                        SELECT document_id
                        FROM document_tags
                        WHERE tag IN ({placeholders})
                        GROUP BY document_id
                        HAVING COUNT(DISTINCT tag) >= ?
                        LIMIT ?
                    """
                    params = list(search_tags) + [len(normalized_tags), limit]
                
                cursor = conn.execute(sql, params)
                
            else:  # OR
                placeholders = ",".join("?" * len(search_tags))
                
                if collection or project_id:
                    sql = f"""
                        SELECT DISTINCT dt.document_id
                        FROM document_tags dt
                        JOIN document_lineage dl ON dt.document_id = dl.document_id
                        WHERE dt.tag IN ({placeholders})
                    """
                    params = list(search_tags)
                    
                    if collection:
                        sql += " AND dl.collection = ?"
                        params.append(collection)
                    if project_id:
                        sql += " AND dl.project_id = ?"
                        params.append(project_id)
                    
                    sql += " AND dl.is_deleted = 0 LIMIT ?"
                    params.append(limit)
                else:
                    sql = f"""
                        SELECT DISTINCT document_id
                        FROM document_tags
                        WHERE tag IN ({placeholders})
                        LIMIT ?
                    """
                    params = list(search_tags) + [limit]
                
                cursor = conn.execute(sql, params)
            
            return [row[0] for row in cursor]
    
    def set_parent_tag(self, child_tag: str, parent_tag: str) -> bool:
        """
        Set a parent-child relationship between tags.
        
        Args:
            child_tag: Child tag
            parent_tag: Parent tag
            
        Returns:
            True if relationship created
        """
        child = self._normalize_tag(child_tag)
        parent = self._normalize_tag(parent_tag)
        
        if not child or not parent or child == parent:
            return False
        
        # Check for circular reference
        if self._would_create_cycle(child, parent):
            logger.warning(f"Cannot set {parent} as parent of {child}: would create cycle")
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO tag_hierarchy (parent_tag, child_tag)
                    VALUES (?, ?)
                    """,
                    (parent, child),
                )
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error setting tag hierarchy: {e}")
                return False
    
    def remove_parent_tag(self, child_tag: str, parent_tag: str) -> bool:
        """
        Remove a parent-child relationship between tags.
        
        Args:
            child_tag: Child tag
            parent_tag: Parent tag
            
        Returns:
            True if relationship removed
        """
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "DELETE FROM tag_hierarchy WHERE parent_tag = ? AND child_tag = ?",
                (self._normalize_tag(parent_tag), self._normalize_tag(child_tag)),
            )
            conn.commit()
            return result.rowcount > 0
    
    def get_tag_hierarchy(self) -> Dict[str, List[str]]:
        """
        Get the complete tag hierarchy.
        
        Returns:
            Dictionary mapping parent tags to their children
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT parent_tag, child_tag FROM tag_hierarchy ORDER BY parent_tag"
            )
            
            hierarchy = {}
            for parent, child in cursor:
                if parent not in hierarchy:
                    hierarchy[parent] = []
                hierarchy[parent].append(child)
            
            return hierarchy
    
    def get_parent_tags(self, tag: str) -> List[str]:
        """
        Get parent tags of a tag.
        
        Args:
            tag: Tag to get parents for
            
        Returns:
            List of parent tags
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT parent_tag FROM tag_hierarchy WHERE child_tag = ?",
                (self._normalize_tag(tag),),
            )
            return [row[0] for row in cursor]
    
    def get_child_tags(self, tag: str) -> List[str]:
        """
        Get direct child tags of a tag.
        
        Args:
            tag: Tag to get children for
            
        Returns:
            List of child tags
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT child_tag FROM tag_hierarchy WHERE parent_tag = ?",
                (self._normalize_tag(tag),),
            )
            return [row[0] for row in cursor]
    
    def _get_child_tags(self, tag: str, recursive: bool = False) -> Set[str]:
        """Get child tags, optionally recursively."""
        children = set(self.get_child_tags(tag))
        
        if recursive:
            for child in list(children):
                children.update(self._get_child_tags(child, recursive=True))
        
        return children
    
    def get_all_tags(self) -> List[str]:
        """
        Get all unique tags in use.
        
        Returns:
            List of tags sorted alphabetically
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT DISTINCT tag FROM document_tags ORDER BY tag"
            )
            return [row[0] for row in cursor]
    
    def get_tag_stats(self) -> List[Dict[str, Any]]:
        """
        Get statistics for all tags.
        
        Returns:
            List of tag stats (tag, document_count, parent_tag)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    dt.tag,
                    COUNT(DISTINCT dt.document_id) as document_count,
                    th.parent_tag
                FROM document_tags dt
                LEFT JOIN tag_hierarchy th ON dt.tag = th.child_tag
                GROUP BY dt.tag
                ORDER BY document_count DESC
            """)
            
            return [
                {
                    "tag": row[0],
                    "document_count": row[1],
                    "parent_tag": row[2],
                }
                for row in cursor
            ]
    
    def set_tag_metadata(
        self,
        tag: str,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Set metadata for a tag.
        
        Args:
            tag: Tag name
            description: Tag description
            color: Tag color (hex)
            icon: Tag icon name
            metadata: Additional metadata
            
        Returns:
            True if metadata set
        """
        normalized = self._normalize_tag(tag)
        
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO tag_metadata
                    (tag, description, color, icon, metadata, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        normalized,
                        description,
                        color,
                        icon,
                        json.dumps(metadata) if metadata else None,
                        datetime.utcnow().isoformat(),
                    ),
                )
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error setting tag metadata: {e}")
                return False
    
    def get_tag_metadata(self, tag: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a tag.
        
        Args:
            tag: Tag name
            
        Returns:
            Metadata dictionary or None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM tag_metadata WHERE tag = ?",
                (self._normalize_tag(tag),),
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    "tag": row["tag"],
                    "description": row["description"],
                    "color": row["color"],
                    "icon": row["icon"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
            
            return None
    
    def rename_tag(self, old_tag: str, new_tag: str) -> int:
        """
        Rename a tag across all documents.
        
        Args:
            old_tag: Current tag name
            new_tag: New tag name
            
        Returns:
            Number of documents affected
        """
        old_normalized = self._normalize_tag(old_tag)
        new_normalized = self._normalize_tag(new_tag)
        
        if not old_normalized or not new_normalized:
            return 0
        
        with sqlite3.connect(self.db_path) as conn:
            # Update document tags
            result = conn.execute(
                "UPDATE document_tags SET tag = ? WHERE tag = ?",
                (new_normalized, old_normalized),
            )
            count = result.rowcount
            
            # Update hierarchy
            conn.execute(
                "UPDATE tag_hierarchy SET parent_tag = ? WHERE parent_tag = ?",
                (new_normalized, old_normalized),
            )
            conn.execute(
                "UPDATE tag_hierarchy SET child_tag = ? WHERE child_tag = ?",
                (new_normalized, old_normalized),
            )
            
            # Update metadata
            conn.execute(
                "UPDATE tag_metadata SET tag = ? WHERE tag = ?",
                (new_normalized, old_normalized),
            )
            
            conn.commit()
            
            logger.info(f"Renamed tag '{old_tag}' to '{new_tag}' on {count} documents")
            return count
    
    def delete_tag(self, tag: str) -> int:
        """
        Delete a tag from all documents.
        
        Args:
            tag: Tag to delete
            
        Returns:
            Number of documents affected
        """
        normalized = self._normalize_tag(tag)
        
        with sqlite3.connect(self.db_path) as conn:
            # Delete from documents
            result = conn.execute(
                "DELETE FROM document_tags WHERE tag = ?",
                (normalized,),
            )
            count = result.rowcount
            
            # Delete from hierarchy
            conn.execute(
                "DELETE FROM tag_hierarchy WHERE parent_tag = ? OR child_tag = ?",
                (normalized, normalized),
            )
            
            # Delete metadata
            conn.execute(
                "DELETE FROM tag_metadata WHERE tag = ?",
                (normalized,),
            )
            
            conn.commit()
            
            logger.info(f"Deleted tag '{tag}' from {count} documents")
            return count
    
    def merge_tags(self, source_tags: List[str], target_tag: str) -> int:
        """
        Merge multiple tags into one.
        
        Args:
            source_tags: Tags to merge from
            target_tag: Tag to merge into
            
        Returns:
            Number of documents affected
        """
        target_normalized = self._normalize_tag(target_tag)
        source_normalized = [self._normalize_tag(t) for t in source_tags if t]
        
        if not source_normalized or not target_normalized:
            return 0
        
        # Remove target from source list if present
        source_normalized = [t for t in source_normalized if t != target_normalized]
        
        if not source_normalized:
            return 0
        
        with sqlite3.connect(self.db_path) as conn:
            placeholders = ",".join("?" * len(source_normalized))
            
            # Get documents with source tags
            cursor = conn.execute(
                f"SELECT DISTINCT document_id FROM document_tags WHERE tag IN ({placeholders})",
                source_normalized,
            )
            doc_ids = [row[0] for row in cursor]
            
            # Add target tag to all these documents
            for doc_id in doc_ids:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO document_tags (document_id, tag)
                    VALUES (?, ?)
                    """,
                    (doc_id, target_normalized),
                )
            
            # Delete source tags
            conn.execute(
                f"DELETE FROM document_tags WHERE tag IN ({placeholders})",
                source_normalized,
            )
            
            # Update hierarchy
            conn.execute(
                f"UPDATE tag_hierarchy SET parent_tag = ? WHERE parent_tag IN ({placeholders})",
                [target_normalized] + source_normalized,
            )
            conn.execute(
                f"UPDATE tag_hierarchy SET child_tag = ? WHERE child_tag IN ({placeholders})",
                [target_normalized] + source_normalized,
            )
            
            conn.commit()
            
            logger.info(f"Merged {len(source_normalized)} tags into '{target_tag}'")
            return len(doc_ids)
    
    def _normalize_tag(self, tag: str) -> str:
        """Normalize a tag for storage."""
        if not tag:
            return ""
        return tag.lower().strip().replace(" ", "-")
    
    def _would_create_cycle(self, child: str, parent: str) -> bool:
        """Check if setting parent would create a cycle."""
        # Check if child is an ancestor of parent
        ancestors = set()
        to_check = [child]
        
        while to_check:
            current = to_check.pop()
            if current in ancestors:
                continue
            ancestors.add(current)
            
            parents = self.get_parent_tags(current)
            to_check.extend(parents)
        
        return parent in ancestors


# Global tag manager instance
_tag_manager: Optional[TagManager] = None


def get_tag_manager(config: Optional[AgenticConfig] = None) -> TagManager:
    """
    Get the global tag manager instance.
    
    Args:
        config: Optional configuration
        
    Returns:
        TagManager instance
    """
    global _tag_manager
    if _tag_manager is None:
        _tag_manager = TagManager(config=config)
    return _tag_manager
