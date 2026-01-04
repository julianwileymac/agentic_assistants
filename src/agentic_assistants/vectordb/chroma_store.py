"""
ChromaDB implementation of the vector store interface.

ChromaDB supports both embedded and server modes, making it flexible
for different deployment scenarios.

Example:
    >>> from agentic_assistants.vectordb import VectorStore
    >>> 
    >>> store = VectorStore.create("chroma", path="./data/vectors")
    >>> store.add(documents, collection="codebase")
    >>> results = store.search("authentication", top_k=5)
"""

from pathlib import Path
from typing import Optional, Union

import chromadb
from chromadb.config import Settings

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import (
    Document,
    SearchResult,
    VectorStore,
)

logger = get_logger(__name__)


class ChromaDBStore(VectorStore):
    """
    ChromaDB implementation of the vector store.
    
    ChromaDB provides:
    - Embedded mode for local development
    - Server mode for production deployments
    - Native embedding functions
    - Metadata filtering
    
    Attributes:
        client: ChromaDB client instance
    """

    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        path: Optional[Union[str, Path]] = None,
        embedding_model: Optional[str] = None,
        embedding_dimension: Optional[int] = None,
        server_host: Optional[str] = None,
        server_port: Optional[int] = None,
    ):
        """
        Initialize ChromaDB store.
        
        Args:
            config: Configuration instance
            path: Path for persistent storage (embedded mode)
            embedding_model: Embedding model name
            embedding_dimension: Embedding vector dimension
            server_host: ChromaDB server host (for server mode)
            server_port: ChromaDB server port (for server mode)
        """
        super().__init__(
            config=config,
            path=path,
            embedding_model=embedding_model,
            embedding_dimension=embedding_dimension,
        )
        
        # Initialize ChromaDB client
        if server_host:
            # Server mode
            self.client = chromadb.HttpClient(
                host=server_host,
                port=server_port or 8000,
            )
            logger.info(f"Connected to ChromaDB server at {server_host}:{server_port}")
        else:
            # Embedded mode with persistence
            self.client = chromadb.PersistentClient(
                path=str(self.path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
            logger.info(f"Connected to ChromaDB (embedded) at {self.path}")

    def _get_collection_name(self, collection: str) -> str:
        """Get the ChromaDB collection name."""
        # ChromaDB has naming restrictions, ensure valid name
        return f"agentic_{collection}".replace("-", "_").replace(" ", "_")

    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection."""
        collection_name = self._get_collection_name(name)
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _add_documents(
        self,
        documents: list[Document],
        collection: str,
    ) -> list[str]:
        """Add documents to a collection."""
        if not documents:
            return []
        
        try:
            chroma_collection = self._get_or_create_collection(collection)
            
            # Prepare data for ChromaDB
            ids = []
            embeddings = []
            documents_text = []
            metadatas = []
            
            for doc in documents:
                if doc.embedding is None:
                    logger.warning(f"Document {doc.id} has no embedding, skipping")
                    continue
                
                ids.append(doc.id)
                embeddings.append(doc.embedding)
                documents_text.append(doc.content)
                metadatas.append(doc.metadata)
            
            if not ids:
                return []
            
            # Upsert documents
            chroma_collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents_text,
                metadatas=metadatas,
            )
            
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
        collection_name = self._get_collection_name(collection)
        
        try:
            # Check if collection exists
            collections = [c.name for c in self.client.list_collections()]
            if collection_name not in collections:
                logger.warning(f"Collection '{collection}' does not exist")
                return []
            
            chroma_collection = self.client.get_collection(collection_name)
            
            # Build where clause for metadata filtering
            where = filter_metadata if filter_metadata else None
            
            # Execute search
            results = chroma_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
                include=["documents", "embeddings", "metadatas", "distances"],
            )
            
            # Convert to SearchResult objects
            search_results = []
            
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    content = results["documents"][0][i] if results["documents"] else ""
                    embedding = results["embeddings"][0][i] if results.get("embeddings") else None
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else 0.0
                    
                    doc = Document(
                        id=doc_id,
                        content=content,
                        embedding=embedding,
                        metadata=metadata,
                    )
                    
                    # ChromaDB returns distance (lower is better for cosine)
                    # Convert to similarity score
                    score = 1.0 - distance if distance <= 1.0 else 1.0 / (1.0 + distance)
                    
                    search_results.append(SearchResult(
                        document=doc,
                        score=score,
                        distance=distance,
                    ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _delete_documents(
        self,
        document_ids: list[str],
        collection: str,
    ) -> int:
        """Delete documents by ID."""
        collection_name = self._get_collection_name(collection)
        
        try:
            collections = [c.name for c in self.client.list_collections()]
            if collection_name not in collections:
                return 0
            
            chroma_collection = self.client.get_collection(collection_name)
            
            # Get existing IDs to count deletions
            existing = chroma_collection.get(ids=document_ids)
            existing_ids = set(existing["ids"]) if existing["ids"] else set()
            
            # Delete
            chroma_collection.delete(ids=document_ids)
            
            deleted = len(existing_ids)
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
        collection_name = self._get_collection_name(collection)
        
        try:
            collections = [c.name for c in self.client.list_collections()]
            if collection_name not in collections:
                return None
            
            chroma_collection = self.client.get_collection(collection_name)
            
            result = chroma_collection.get(
                ids=[document_id],
                include=["documents", "embeddings", "metadatas"],
            )
            
            if not result["ids"]:
                return None
            
            return Document(
                id=result["ids"][0],
                content=result["documents"][0] if result["documents"] else "",
                embedding=result["embeddings"][0] if result.get("embeddings") else None,
                metadata=result["metadatas"][0] if result["metadatas"] else {},
            )
            
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            return None

    def _list_collections(self) -> list[str]:
        """List all collections."""
        prefix = "agentic_"
        collections = self.client.list_collections()
        return [
            c.name[len(prefix):]
            for c in collections
            if c.name.startswith(prefix)
        ]

    def _create_collection(
        self,
        name: str,
        metadata: Optional[dict],
    ) -> bool:
        """Create a collection."""
        collection_name = self._get_collection_name(name)
        
        try:
            collections = [c.name for c in self.client.list_collections()]
            if collection_name in collections:
                return False
            
            collection_metadata = {"hnsw:space": "cosine"}
            if metadata:
                collection_metadata.update(metadata)
            
            self.client.create_collection(
                name=collection_name,
                metadata=collection_metadata,
            )
            
            logger.info(f"Created collection '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False

    def _delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        collection_name = self._get_collection_name(name)
        
        try:
            collections = [c.name for c in self.client.list_collections()]
            if collection_name not in collections:
                return False
            
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False

    def _count(self, collection: str) -> int:
        """Count documents in a collection."""
        collection_name = self._get_collection_name(collection)
        
        try:
            collections = [c.name for c in self.client.list_collections()]
            if collection_name not in collections:
                return 0
            
            chroma_collection = self.client.get_collection(collection_name)
            return chroma_collection.count()
            
        except Exception as e:
            logger.error(f"Failed to count documents: {e}")
            return 0

    def reset(self) -> None:
        """
        Reset the database, deleting all collections.
        
        Use with caution in production!
        """
        try:
            self.client.reset()
            logger.warning("ChromaDB database reset - all data deleted")
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")


# Register this backend
VectorStore.register_backend("chroma", ChromaDBStore)

