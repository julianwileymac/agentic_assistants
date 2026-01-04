"""
Codebase indexing for vector database.

This module provides functionality to index entire codebases
into the vector database for semantic search.

Example:
    >>> from agentic_assistants.indexing import CodebaseIndexer
    >>> from agentic_assistants.vectordb import VectorStore
    >>> 
    >>> store = VectorStore.create("lancedb")
    >>> indexer = CodebaseIndexer(store)
    >>> indexer.index_directory("./src", collection="my-project")
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.indexing.chunker import DocumentChunker, ChunkingStrategy
from agentic_assistants.indexing.loader import FileLoader
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import Document, VectorStore

logger = get_logger(__name__)


@dataclass
class IndexingStats:
    """Statistics from an indexing operation."""
    
    files_processed: int = 0
    files_skipped: int = 0
    chunks_created: int = 0
    chunks_indexed: int = 0
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "files_processed": self.files_processed,
            "files_skipped": self.files_skipped,
            "chunks_created": self.chunks_created,
            "chunks_indexed": self.chunks_indexed,
            "errors": self.errors,
            "duration_seconds": self.duration_seconds,
        }


@dataclass
class IndexedFile:
    """Metadata about an indexed file."""
    
    path: str
    content_hash: str
    chunk_count: int
    indexed_at: str
    language: Optional[str] = None
    size_bytes: int = 0


class CodebaseIndexer:
    """
    Index codebases into a vector database.
    
    This class provides:
    - Full codebase indexing with chunking
    - Incremental updates (only re-index changed files)
    - .gitignore support
    - Progress tracking
    
    Attributes:
        vector_store: Vector store to index into
        chunker: Document chunker for splitting files
        file_loader: File loader for reading files
    """

    # Default file patterns for code files
    DEFAULT_CODE_PATTERNS = [
        "*.py",
        "*.js",
        "*.ts",
        "*.jsx",
        "*.tsx",
        "*.java",
        "*.go",
        "*.rs",
        "*.c",
        "*.cpp",
        "*.h",
        "*.hpp",
        "*.cs",
        "*.rb",
        "*.php",
        "*.swift",
        "*.kt",
        "*.scala",
        "*.r",
        "*.sql",
        "*.sh",
        "*.yaml",
        "*.yml",
        "*.json",
        "*.toml",
        "*.md",
        "*.rst",
    ]

    def __init__(
        self,
        vector_store: VectorStore,
        chunking_strategy: Union[ChunkingStrategy, str] = ChunkingStrategy.CODE_AWARE,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
        config: Optional[AgenticConfig] = None,
    ):
        """
        Initialize the codebase indexer.
        
        Args:
            vector_store: Vector store to index into
            chunking_strategy: Strategy for chunking documents
            chunk_size: Target chunk size
            chunk_overlap: Overlap between chunks
            config: Configuration instance
        """
        self.vector_store = vector_store
        self.config = config or AgenticConfig()
        
        self.chunker = DocumentChunker(
            strategy=chunking_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            config=self.config,
        )
        
        self.file_loader = FileLoader(
            max_file_size=1024 * 1024,  # 1MB
            respect_gitignore=True,
        )
        
        # Store for tracking indexed files
        self._index_metadata: dict[str, dict] = {}

    def _compute_hash(self, content: str) -> str:
        """Compute a hash of file content."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _get_collection_metadata_key(self, collection: str) -> str:
        """Get the metadata key for a collection."""
        return f"_index_meta_{collection}"

    def _load_index_metadata(self, collection: str) -> dict[str, IndexedFile]:
        """Load index metadata for a collection."""
        # Try to load from vector store metadata
        meta_doc = self.vector_store.get(
            self._get_collection_metadata_key(collection),
            collection=collection,
        )
        
        if meta_doc and meta_doc.content:
            try:
                data = json.loads(meta_doc.content)
                return {
                    path: IndexedFile(**file_data)
                    for path, file_data in data.items()
                }
            except (json.JSONDecodeError, TypeError):
                pass
        
        return {}

    def _save_index_metadata(
        self,
        collection: str,
        metadata: dict[str, IndexedFile],
    ) -> None:
        """Save index metadata for a collection."""
        data = {
            path: {
                "path": idx.path,
                "content_hash": idx.content_hash,
                "chunk_count": idx.chunk_count,
                "indexed_at": idx.indexed_at,
                "language": idx.language,
                "size_bytes": idx.size_bytes,
            }
            for path, idx in metadata.items()
        }
        
        meta_doc = Document(
            id=self._get_collection_metadata_key(collection),
            content=json.dumps(data),
            metadata={"type": "index_metadata"},
        )
        
        self.vector_store.add(
            meta_doc,
            collection=collection,
            generate_embeddings=False,
        )

    def index_file(
        self,
        path: Union[str, Path],
        collection: str = "default",
        force: bool = False,
        additional_metadata: Optional[dict] = None,
    ) -> IndexingStats:
        """
        Index a single file.
        
        Args:
            path: Path to the file
            collection: Collection to index into
            force: Force re-indexing even if unchanged
            additional_metadata: Additional metadata for chunks
        
        Returns:
            Indexing statistics
        """
        import time
        start_time = time.time()
        stats = IndexingStats()
        
        path = Path(path).resolve()
        path_str = str(path)
        
        # Load file
        loaded = self.file_loader.load_file(path)
        if loaded is None:
            stats.files_skipped += 1
            stats.errors.append(f"Could not load: {path}")
            return stats
        
        # Check if already indexed and unchanged
        if not force:
            index_meta = self._load_index_metadata(collection)
            content_hash = self._compute_hash(loaded.content)
            
            if path_str in index_meta:
                existing = index_meta[path_str]
                if existing.content_hash == content_hash:
                    logger.debug(f"Skipping unchanged file: {path}")
                    stats.files_skipped += 1
                    return stats
        
        # Chunk the file
        metadata = {
            "collection": collection,
            "indexed_at": datetime.utcnow().isoformat(),
        }
        if additional_metadata:
            metadata.update(additional_metadata)
        
        try:
            chunks = self.chunker.chunk_loaded_file(loaded, metadata)
            stats.chunks_created = len(chunks)
        except Exception as e:
            stats.errors.append(f"Chunking failed for {path}: {e}")
            stats.files_skipped += 1
            return stats
        
        # Delete existing chunks for this file
        existing_meta = self._load_index_metadata(collection)
        if path_str in existing_meta:
            # Find and delete old chunks
            # This is a simplification - ideally we'd track chunk IDs
            pass
        
        # Add chunks to vector store
        try:
            self.vector_store.add(chunks, collection=collection)
            stats.chunks_indexed = len(chunks)
            stats.files_processed = 1
        except Exception as e:
            stats.errors.append(f"Indexing failed for {path}: {e}")
            return stats
        
        # Update index metadata
        content_hash = self._compute_hash(loaded.content)
        existing_meta[path_str] = IndexedFile(
            path=path_str,
            content_hash=content_hash,
            chunk_count=len(chunks),
            indexed_at=datetime.utcnow().isoformat(),
            language=loaded.language,
            size_bytes=loaded.size_bytes,
        )
        self._save_index_metadata(collection, existing_meta)
        
        stats.duration_seconds = time.time() - start_time
        logger.info(f"Indexed {path}: {len(chunks)} chunks")
        
        return stats

    def index_directory(
        self,
        directory: Union[str, Path],
        collection: str = "default",
        patterns: Optional[list[str]] = None,
        recursive: bool = True,
        force: bool = False,
        additional_metadata: Optional[dict] = None,
        progress_callback: Optional[callable] = None,
    ) -> IndexingStats:
        """
        Index all files in a directory.
        
        Args:
            directory: Directory path
            collection: Collection to index into
            patterns: File patterns to include
            recursive: Whether to recurse into subdirectories
            force: Force re-indexing of all files
            additional_metadata: Additional metadata for chunks
            progress_callback: Callback for progress updates
        
        Returns:
            Indexing statistics
        """
        import time
        start_time = time.time()
        
        directory = Path(directory).resolve()
        patterns = patterns or self.DEFAULT_CODE_PATTERNS
        
        # Load files
        files = self.file_loader.load_directory(
            directory,
            patterns=patterns,
            recursive=recursive,
        )
        
        total_files = len(files)
        logger.info(f"Found {total_files} files to index in {directory}")
        
        # Aggregate stats
        total_stats = IndexingStats()
        
        # Load existing index metadata
        existing_meta = self._load_index_metadata(collection) if not force else {}
        updated_meta = dict(existing_meta)
        
        for i, loaded_file in enumerate(files):
            path_str = str(loaded_file.path)
            
            # Check if unchanged
            content_hash = self._compute_hash(loaded_file.content)
            if path_str in existing_meta and not force:
                existing = existing_meta[path_str]
                if existing.content_hash == content_hash:
                    total_stats.files_skipped += 1
                    continue
            
            # Chunk and index
            try:
                metadata = {
                    "collection": collection,
                    "base_directory": str(directory),
                    "relative_path": str(loaded_file.path.relative_to(directory)),
                    "indexed_at": datetime.utcnow().isoformat(),
                }
                if additional_metadata:
                    metadata.update(additional_metadata)
                
                chunks = self.chunker.chunk_loaded_file(loaded_file, metadata)
                total_stats.chunks_created += len(chunks)
                
                if chunks:
                    self.vector_store.add(chunks, collection=collection)
                    total_stats.chunks_indexed += len(chunks)
                
                total_stats.files_processed += 1
                
                # Update metadata
                updated_meta[path_str] = IndexedFile(
                    path=path_str,
                    content_hash=content_hash,
                    chunk_count=len(chunks),
                    indexed_at=datetime.utcnow().isoformat(),
                    language=loaded_file.language,
                    size_bytes=loaded_file.size_bytes,
                )
                
            except Exception as e:
                total_stats.files_skipped += 1
                total_stats.errors.append(f"{loaded_file.path}: {e}")
                logger.error(f"Failed to index {loaded_file.path}: {e}")
            
            # Progress callback
            if progress_callback:
                progress_callback(i + 1, total_files, loaded_file.path)
        
        # Save updated metadata
        self._save_index_metadata(collection, updated_meta)
        
        total_stats.duration_seconds = time.time() - start_time
        
        logger.info(
            f"Indexing complete: {total_stats.files_processed} files, "
            f"{total_stats.chunks_indexed} chunks in {total_stats.duration_seconds:.2f}s"
        )
        
        return total_stats

    def get_indexed_files(self, collection: str = "default") -> list[dict]:
        """
        Get list of indexed files in a collection.
        
        Args:
            collection: Collection name
        
        Returns:
            List of file metadata dictionaries
        """
        metadata = self._load_index_metadata(collection)
        return [
            {
                "path": idx.path,
                "language": idx.language,
                "chunk_count": idx.chunk_count,
                "size_bytes": idx.size_bytes,
                "indexed_at": idx.indexed_at,
            }
            for idx in metadata.values()
        ]

    def remove_file(
        self,
        path: Union[str, Path],
        collection: str = "default",
    ) -> bool:
        """
        Remove a file from the index.
        
        Args:
            path: Path to the file
            collection: Collection name
        
        Returns:
            True if removed, False if not found
        """
        path_str = str(Path(path).resolve())
        
        metadata = self._load_index_metadata(collection)
        if path_str not in metadata:
            return False
        
        # Note: We can't easily delete individual chunks without tracking IDs
        # For now, just remove from metadata
        del metadata[path_str]
        self._save_index_metadata(collection, metadata)
        
        logger.info(f"Removed {path_str} from index")
        return True

    def clear_collection(self, collection: str = "default") -> bool:
        """
        Clear all indexed data from a collection.
        
        Args:
            collection: Collection name
        
        Returns:
            True if cleared
        """
        try:
            self.vector_store.delete_collection(collection)
            logger.info(f"Cleared collection: {collection}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False

    def get_stats(self, collection: str = "default") -> dict:
        """
        Get statistics for an indexed collection.
        
        Args:
            collection: Collection name
        
        Returns:
            Statistics dictionary
        """
        metadata = self._load_index_metadata(collection)
        
        total_chunks = sum(idx.chunk_count for idx in metadata.values())
        total_size = sum(idx.size_bytes for idx in metadata.values())
        
        languages = {}
        for idx in metadata.values():
            lang = idx.language or "unknown"
            if lang not in languages:
                languages[lang] = {"files": 0, "chunks": 0}
            languages[lang]["files"] += 1
            languages[lang]["chunks"] += idx.chunk_count
        
        return {
            "collection": collection,
            "total_files": len(metadata),
            "total_chunks": total_chunks,
            "total_size_bytes": total_size,
            "by_language": languages,
            "vector_count": self.vector_store.count(collection),
        }

