# Chunk: cfce99ee7b30_0

- source: `src/agentic_assistants/indexing/chunker.py`
- lines: 1-99
- chunk: 1/5

```
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
```
