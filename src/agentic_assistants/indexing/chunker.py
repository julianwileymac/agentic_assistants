"""
Document chunking with LlamaIndex integration.

This module provides document chunking capabilities using LlamaIndex,
with support for different chunking strategies.

Example:
    >>> from agentic_assistants.indexing import DocumentChunker
    >>> 
    >>> chunker = DocumentChunker(strategy="code_aware")
    >>> chunks = chunker.chunk_file("src/main.py")
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.indexing.loader import FileLoader, LoadedFile
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import Document

logger = get_logger(__name__)


class ChunkingStrategy(str, Enum):
    """Available chunking strategies."""
    
    FIXED = "fixed"  # Fixed size chunks
    SENTENCE = "sentence"  # Sentence-based splitting
    SEMANTIC = "semantic"  # Semantic similarity based
    CODE_AWARE = "code_aware"  # Code-structure aware


@dataclass
class ChunkMetadata:
    """Metadata for a chunk."""
    
    file_path: str
    language: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    chunk_index: int = 0
    total_chunks: int = 0
    extra: dict = field(default_factory=dict)


class DocumentChunker:
    """
    Chunk documents using LlamaIndex.
    
    This class provides document chunking with support for:
    - Fixed size chunks
    - Sentence-based splitting
    - Semantic chunking
    - Code-aware chunking (respects function/class boundaries)
    
    Attributes:
        strategy: Chunking strategy to use
        chunk_size: Target chunk size in characters
        chunk_overlap: Overlap between chunks in characters
    """

    def __init__(
        self,
        strategy: Union[ChunkingStrategy, str] = ChunkingStrategy.SENTENCE,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
        config: Optional[AgenticConfig] = None,
    ):
        """
        Initialize the chunker.
        
        Args:
            strategy: Chunking strategy
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
            config: Configuration instance
        """
        if isinstance(strategy, str):
            strategy = ChunkingStrategy(strategy)
        
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.config = config or AgenticConfig()
        self.file_loader = FileLoader()
        
        # Initialize LlamaIndex components lazily
        self._splitter = None

    def _get_splitter(self, language: Optional[str] = None):
        """Get the appropriate text splitter for the strategy."""
        from llama_index.core.node_parser import (
            SentenceSplitter,
            CodeSplitter,
            SemanticSplitterNodeParser,
        )
        
        if self.strategy == ChunkingStrategy.CODE_AWARE and language:
            # Use code splitter for programming languages
            try:
                return CodeSplitter(
                    language=language,
                    chunk_lines=40,
                    chunk_lines_overlap=5,
                    max_chars=self.chunk_size,
                )
            except Exception as e:
                logger.warning(f"Code splitter not available for {language}: {e}")
                # Fall back to sentence splitter
                return SentenceSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                )
        
        elif self.strategy == ChunkingStrategy.SEMANTIC:
            # Semantic splitting requires embeddings
            try:
                from llama_index.embeddings.ollama import OllamaEmbedding
                
                embed_model = OllamaEmbedding(
                    model_name=self.config.vectordb.embedding_model,
                    base_url=self.config.ollama.host,
                )
                return SemanticSplitterNodeParser(
                    buffer_size=1,
                    breakpoint_percentile_threshold=95,
                    embed_model=embed_model,
                )
            except Exception as e:
                logger.warning(f"Semantic splitter failed, falling back to sentence: {e}")
                return SentenceSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                )
        
        else:
            # Default to sentence splitter
            return SentenceSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )

    def _create_document(
        self,
        content: str,
        metadata: ChunkMetadata,
    ) -> Document:
        """Create a Document from chunk content and metadata."""
        doc_id = str(uuid.uuid4())
        
        return Document(
            id=doc_id,
            content=content,
            metadata={
                "file_path": metadata.file_path,
                "language": metadata.language,
                "start_line": metadata.start_line,
                "end_line": metadata.end_line,
                "chunk_index": metadata.chunk_index,
                "total_chunks": metadata.total_chunks,
                **metadata.extra,
            },
        )

    def chunk_text(
        self,
        text: str,
        metadata: Optional[dict] = None,
        language: Optional[str] = None,
    ) -> list[Document]:
        """
        Chunk a text string into documents.
        
        Args:
            text: Text to chunk
            metadata: Additional metadata for chunks
            language: Programming language (for code_aware strategy)
        
        Returns:
            List of Document objects
        """
        from llama_index.core import Document as LlamaDocument
        
        splitter = self._get_splitter(language)
        
        # Create LlamaIndex document
        llama_doc = LlamaDocument(text=text, metadata=metadata or {})
        
        # Split into nodes
        nodes = splitter.get_nodes_from_documents([llama_doc])
        
        # Convert to our Document format
        documents = []
        for i, node in enumerate(nodes):
            chunk_meta = ChunkMetadata(
                file_path=metadata.get("file_path", "") if metadata else "",
                language=language,
                start_line=node.metadata.get("start_line", 0) if hasattr(node, "metadata") else 0,
                end_line=node.metadata.get("end_line", 0) if hasattr(node, "metadata") else 0,
                chunk_index=i,
                total_chunks=len(nodes),
                extra=metadata or {},
            )
            
            documents.append(self._create_document(node.text, chunk_meta))
        
        return documents

    def chunk_file(
        self,
        path: Union[str, Path],
        additional_metadata: Optional[dict] = None,
    ) -> list[Document]:
        """
        Chunk a file into documents.
        
        Args:
            path: Path to the file
            additional_metadata: Additional metadata to include
        
        Returns:
            List of Document objects
        """
        loaded = self.file_loader.load_file(path)
        if loaded is None:
            return []
        
        return self.chunk_loaded_file(loaded, additional_metadata)

    def chunk_loaded_file(
        self,
        loaded_file: LoadedFile,
        additional_metadata: Optional[dict] = None,
    ) -> list[Document]:
        """
        Chunk a LoadedFile into documents.
        
        Args:
            loaded_file: LoadedFile instance
            additional_metadata: Additional metadata to include
        
        Returns:
            List of Document objects
        """
        metadata = {
            "file_path": str(loaded_file.path),
            "file_name": loaded_file.name,
            "extension": loaded_file.extension,
            "size_bytes": loaded_file.size_bytes,
        }
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return self.chunk_text(
            loaded_file.content,
            metadata=metadata,
            language=loaded_file.language,
        )

    def chunk_directory(
        self,
        directory: Union[str, Path],
        patterns: Optional[list[str]] = None,
        recursive: bool = True,
        additional_metadata: Optional[dict] = None,
    ) -> list[Document]:
        """
        Chunk all files in a directory.
        
        Args:
            directory: Directory path
            patterns: File patterns to include (e.g., ["*.py"])
            recursive: Whether to recurse into subdirectories
            additional_metadata: Additional metadata to include
        
        Returns:
            List of Document objects
        """
        files = self.file_loader.load_directory(
            directory,
            patterns=patterns,
            recursive=recursive,
        )
        
        all_documents = []
        for loaded_file in files:
            documents = self.chunk_loaded_file(loaded_file, additional_metadata)
            all_documents.extend(documents)
        
        logger.info(f"Created {len(all_documents)} chunks from {len(files)} files")
        return all_documents

    def estimate_chunks(
        self,
        text: str,
        language: Optional[str] = None,
    ) -> int:
        """
        Estimate the number of chunks for a text.
        
        Args:
            text: Text to estimate
            language: Programming language
        
        Returns:
            Estimated number of chunks
        """
        # Simple estimation based on chunk size
        text_length = len(text)
        effective_chunk_size = self.chunk_size - self.chunk_overlap
        
        if effective_chunk_size <= 0:
            return 1
        
        return max(1, (text_length + effective_chunk_size - 1) // effective_chunk_size)


class SimpleChunker:
    """
    Simple text chunker without LlamaIndex dependency.
    
    Use this when LlamaIndex is not available or for simple use cases.
    """

    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
    ):
        """
        Initialize the simple chunker.
        
        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(
        self,
        text: str,
        metadata: Optional[dict] = None,
    ) -> list[Document]:
        """
        Chunk text using simple character-based splitting.
        
        Args:
            text: Text to chunk
            metadata: Metadata for chunks
        
        Returns:
            List of Document objects
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at a newline if possible
            if end < len(text):
                newline_pos = text.rfind("\n", start + self.chunk_size // 2, end)
                if newline_pos > start:
                    end = newline_pos + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                doc = Document(
                    id=str(uuid.uuid4()),
                    content=chunk_text,
                    metadata={
                        **(metadata or {}),
                        "chunk_index": chunk_index,
                        "start_char": start,
                        "end_char": end,
                    },
                )
                chunks.append(doc)
                chunk_index += 1
            
            start = end - self.chunk_overlap
        
        # Update total chunks
        for doc in chunks:
            doc.metadata["total_chunks"] = len(chunks)
        
        return chunks

