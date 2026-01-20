"""
Indexing module for Agentic Assistants.

This module provides:
- DocumentChunker: Chunk documents using LlamaIndex
- FileLoader: Load files from disk
- CodebaseIndexer: Index entire codebases
- ProjectIndexer: Extended indexer with semantic search
- INDEXING_VERSION: Current indexing schema version

Example:
    >>> from agentic_assistants.indexing import DocumentChunker, CodebaseIndexer
    >>> 
    >>> chunker = DocumentChunker(strategy="code_aware")
    >>> chunks = chunker.chunk_file("src/main.py")
    >>> 
    >>> indexer = CodebaseIndexer(vector_store)
    >>> indexer.index_directory("./src")
    >>> 
    >>> # Project-level indexing
    >>> indexer.index_project("project-123", "./src")
    >>> 
    >>> # Semantic search with ProjectIndexer
    >>> from agentic_assistants.indexing import ProjectIndexer
    >>> project_indexer = ProjectIndexer()
    >>> results = project_indexer.semantic_search("parse JSON files")
"""

from agentic_assistants.indexing.chunker import DocumentChunker, ChunkingStrategy
from agentic_assistants.indexing.loader import FileLoader, LoadedFile
from agentic_assistants.indexing.codebase import CodebaseIndexer, INDEXING_VERSION
from agentic_assistants.indexing.project_indexer import (
    ProjectIndexer,
    SearchResult,
    CodeSymbol,
    SEMANTIC_VERSION,
)

__all__ = [
    "DocumentChunker",
    "ChunkingStrategy",
    "FileLoader",
    "LoadedFile",
    "CodebaseIndexer",
    "ProjectIndexer",
    "SearchResult",
    "CodeSymbol",
    "INDEXING_VERSION",
    "SEMANTIC_VERSION",
]

