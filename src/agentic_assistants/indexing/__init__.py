"""
Indexing module for Agentic Assistants.

This module provides:
- DocumentChunker: Chunk documents using LlamaIndex
- FileLoader: Load files from disk
- CodebaseIndexer: Index entire codebases

Example:
    >>> from agentic_assistants.indexing import DocumentChunker, CodebaseIndexer
    >>> 
    >>> chunker = DocumentChunker(strategy="code_aware")
    >>> chunks = chunker.chunk_file("src/main.py")
    >>> 
    >>> indexer = CodebaseIndexer(vector_store)
    >>> indexer.index_directory("./src")
"""

from agentic_assistants.indexing.chunker import DocumentChunker, ChunkingStrategy
from agentic_assistants.indexing.loader import FileLoader, LoadedFile
from agentic_assistants.indexing.codebase import CodebaseIndexer

__all__ = [
    "DocumentChunker",
    "ChunkingStrategy",
    "FileLoader",
    "LoadedFile",
    "CodebaseIndexer",
]

