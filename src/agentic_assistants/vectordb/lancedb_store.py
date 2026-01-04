"""
LanceDB implementation of the vector store interface.

LanceDB is an embedded vector database that stores data locally,
making it ideal for local development and Continue framework integration.

Example:
    >>> from agentic_assistants.vectordb import LanceDBStore
    >>> 
    >>> store = LanceDBStore(path="./data/vectors")
    >>> store.add(documents, collection="codebase")
    >>> results = store.search("authentication", top_k=5)
"""

from pathlib import Path
from typing import Optional, Union

import lancedb
import pyarrow as pa

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import (
    Document,
    SearchResult,
    VectorStore,
)

logger = get_logger(__name__)


class LanceDBStore(VectorStore):
    """
    LanceDB implementation of the vector store.
    
    LanceDB is an embedded vector database that:
    - Stores data locally in Lance format
    - Supports fast vector similarity search
    - Works without a separate server process
    - Is compatible with Continue framework
    
    Attributes:
        db: LanceDB database instance
    """

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        path: Optional[Union[str, Path]] = None,
        embedding_model: Optional[str] = None,
        embedding_dimension: Optional[int] = None,
    ):
        """
        Initialize LanceDB store.
        
        Args:
            config: Configuration instance
            path: Path for database storage
            embedding_model: Embedding model name
            embedding_dimension: Embedding vector dimension
        """
        super().__init__(
            config=config,
            path=path,
            embedding_model=embedding_model,
            embedding_dimension=embedding_dimension,
        )
        
        # Connect to LanceDB
        self.db = lancedb.connect(self.path)
        logger.info(f"Connected to LanceDB at {self.path}")

    def _get_table_name(self, collection: str) -> str:
        """Get the table name for a collection."""
        return f"collection_{collection}"

    def _get_schema(self) -> pa.Schema:
        """Get the PyArrow schema for documents."""
        return pa.schema([
            pa.field("id", pa.string()),
            pa.field("content", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), self.embedding_dimension)),
            pa.field("metadata", pa.string()),  # JSON string
        ])

    def _add_documents(
        self,
        documents: list[Document],
        collection: str,
    ) -> list[str]:
        """Add documents to a collection."""
        table_name = self._get_table_name(collection)
        
        # Prepare data
        import json
        data = []
        ids = []
        
        for doc in documents:
            if doc.embedding is None:
                logger.warning(f"Document {doc.id} has no embedding, skipping")
                continue
            
            data.append({
                "id": doc.id,
                "content": doc.content,
                "vector": doc.embedding,
                "metadata": json.dumps(doc.metadata),
            })
            ids.append(doc.id)
        
        if not data:
            return []
        
        try:
            # Get or create table
            if table_name in self.db.table_names():
                table = self.db.open_table(table_name)
                table.add(data)
            else:
                self.db.create_table(table_name, data)
            
            logger.debug(f"Added {len(ids)} documents to collection '{collection}'")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def _search(
        self,
        query_embedding: list[float],
        collection: str,
        top_k: int,
        filter_metadata: Optional[dict],
    ) -> list[SearchResult]:
        """Search for similar documents."""
        table_name = self._get_table_name(collection)
        
        if table_name not in self.db.table_names():
            logger.warning(f"Collection '{collection}' does not exist")
            return []
        
        import json
        
        try:
            table = self.db.open_table(table_name)
            
            # Build query
            query = table.search(query_embedding).limit(top_k)
            
            # Apply metadata filters if provided
            if filter_metadata:
                # LanceDB uses SQL-like where clauses
                # We'll filter in post-processing for flexibility
                pass
            
            # Execute search
            results = query.to_list()
            
            # Convert to SearchResult objects
            search_results = []
            for row in results:
                # Parse metadata
                metadata = json.loads(row.get("metadata", "{}"))
                
                # Apply metadata filter
                if filter_metadata:
                    match = all(
                        metadata.get(k) == v
                        for k, v in filter_metadata.items()
                    )
                    if not match:
                        continue
                
                doc = Document(
                    id=row["id"],
                    content=row["content"],
                    embedding=row.get("vector"),
                    metadata=metadata,
                )
                
                # LanceDB returns _distance (lower is better)
                distance = row.get("_distance", 0.0)
                score = 1.0 / (1.0 + distance)  # Convert to similarity score
                
                search_results.append(SearchResult(
                    document=doc,
                    score=score,
                    distance=distance,
                ))
            
            return search_results[:top_k]  # Ensure top_k after filtering
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _delete_documents(
        self,
        document_ids: list[str],
        collection: str,
    ) -> int:
        """Delete documents by ID."""
        table_name = self._get_table_name(collection)
        
        if table_name not in self.db.table_names():
            return 0
        
        try:
            table = self.db.open_table(table_name)
            
            # Delete by ID using SQL-like predicate
            deleted = 0
            for doc_id in document_ids:
                try:
                    table.delete(f'id = "{doc_id}"')
                    deleted += 1
                except Exception:
                    pass
            
            logger.debug(f"Deleted {deleted} documents from collection '{collection}'")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return 0

    def _get_document(
        self,
        document_id: str,
        collection: str,
    ) -> Optional[Document]:
        """Get a document by ID."""
        table_name = self._get_table_name(collection)
        
        if table_name not in self.db.table_names():
            return None
        
        import json
        
        try:
            table = self.db.open_table(table_name)
            
            # Search by ID
            results = table.search().where(f'id = "{document_id}"').limit(1).to_list()
            
            if not results:
                return None
            
            row = results[0]
            return Document(
                id=row["id"],
                content=row["content"],
                embedding=row.get("vector"),
                metadata=json.loads(row.get("metadata", "{}")),
            )
            
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            return None

    def _list_collections(self) -> list[str]:
        """List all collections."""
        prefix = "collection_"
        return [
            name[len(prefix):]
            for name in self.db.table_names()
            if name.startswith(prefix)
        ]

    def _create_collection(
        self,
        name: str,
        metadata: Optional[dict],
    ) -> bool:
        """Create a collection."""
        table_name = self._get_table_name(name)
        
        if table_name in self.db.table_names():
            return False
        
        try:
            # Create empty table with schema
            # LanceDB requires at least one record, so we'll create on first add
            # For now, mark it as "pending creation"
            logger.debug(f"Collection '{name}' will be created on first document add")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False

    def _delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        table_name = self._get_table_name(name)
        
        if table_name not in self.db.table_names():
            return False
        
        try:
            self.db.drop_table(table_name)
            logger.info(f"Deleted collection '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False

    def _count(self, collection: str) -> int:
        """Count documents in a collection."""
        table_name = self._get_table_name(collection)
        
        if table_name not in self.db.table_names():
            return 0
        
        try:
            table = self.db.open_table(table_name)
            return table.count_rows()
            
        except Exception as e:
            logger.error(f"Failed to count documents: {e}")
            return 0

    def compact(self, collection: Optional[str] = None) -> None:
        """
        Compact the database to optimize storage and query performance.
        
        Args:
            collection: Specific collection to compact, or all if None
        """
        if collection:
            table_name = self._get_table_name(collection)
            if table_name in self.db.table_names():
                table = self.db.open_table(table_name)
                table.compact_files()
                logger.info(f"Compacted collection '{collection}'")
        else:
            for name in self._list_collections():
                self.compact(name)


# Register this backend
VectorStore.register_backend("lancedb", LanceDBStore)

