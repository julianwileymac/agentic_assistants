"""
Project Indexer with Semantic Search Capabilities.

This module extends the base CodebaseIndexer with:
- Semantic code search
- Symbol extraction and indexing
- Cross-project search
- Search result ranking

Version History:
    2.0: Initial semantic search implementation
    2.1: Added symbol extraction and multi-project search

Example:
    >>> from agentic_assistants.indexing import ProjectIndexer
    >>> 
    >>> indexer = ProjectIndexer()
    >>> indexer.index_project("project-123", "./src")
    >>> 
    >>> # Semantic search
    >>> results = indexer.semantic_search("function to parse JSON files")
    >>> for result in results:
    ...     print(f"{result.path}: {result.score}")
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.indexing.codebase import CodebaseIndexer, INDEXING_VERSION, IndexingStats
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import Document, VectorStore

logger = get_logger(__name__)

# Extended indexing version for semantic features
SEMANTIC_VERSION = "2.1"


@dataclass
class SearchResult:
    """A search result from semantic search."""
    
    id: str
    path: str
    content: str
    score: float
    language: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    project_id: Optional[str] = None
    symbols: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "path": self.path,
            "content": self.content,
            "score": self.score,
            "language": self.language,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "project_id": self.project_id,
            "symbols": self.symbols,
            "metadata": self.metadata,
        }


@dataclass
class CodeSymbol:
    """A code symbol (function, class, variable)."""
    
    name: str
    symbol_type: str  # function, class, method, variable, constant
    path: str
    line_number: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    language: Optional[str] = None
    parent: Optional[str] = None  # For nested symbols (methods in classes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "symbol_type": self.symbol_type,
            "path": self.path,
            "line_number": self.line_number,
            "signature": self.signature,
            "docstring": self.docstring,
            "language": self.language,
            "parent": self.parent,
        }


class ProjectIndexer(CodebaseIndexer):
    """
    Extended codebase indexer with semantic search capabilities.
    
    This class adds:
    - Semantic code search using natural language queries
    - Symbol extraction (functions, classes, methods)
    - Cross-project search
    - Search result ranking and filtering
    
    Attributes:
        symbol_index: Dictionary of indexed symbols
        project_metadata: Metadata for indexed projects
    """
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        config: Optional[AgenticConfig] = None,
        **kwargs,
    ):
        """
        Initialize the project indexer.
        
        Args:
            vector_store: Vector store to use (creates default if None)
            config: Configuration instance
            **kwargs: Additional arguments for CodebaseIndexer
        """
        self.config = config or AgenticConfig()
        
        # Create vector store if not provided
        if vector_store is None:
            from agentic_assistants.vectordb import VectorStore as VS
            vector_store = VS.create(
                provider=self.config.vectordb.provider,
                config=self.config,
            )
        
        super().__init__(
            vector_store=vector_store,
            config=self.config,
            **kwargs,
        )
        
        # Symbol index (path -> list of symbols)
        self._symbol_index: Dict[str, List[CodeSymbol]] = {}
        
        # Project metadata cache
        self._project_metadata: Dict[str, Dict[str, Any]] = {}
    
    # =========================================================================
    # Semantic Search
    # =========================================================================
    
    def semantic_search(
        self,
        query: str,
        project_id: Optional[str] = None,
        limit: int = 10,
        threshold: float = 0.5,
        file_patterns: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """
        Search for code using natural language.
        
        This performs semantic search over indexed code chunks,
        returning results ranked by relevance.
        
        Args:
            query: Natural language search query
            project_id: Optional project to search within
            limit: Maximum results to return
            threshold: Minimum similarity score (0-1)
            file_patterns: Optional file patterns to filter
            languages: Optional languages to filter
            
        Returns:
            List of SearchResult objects ranked by relevance
        """
        # Determine collection
        if project_id:
            collection = self._get_project_collection(project_id)
        else:
            collection = "default"
        
        # Build filter conditions
        filter_dict = {}
        if file_patterns:
            # Will be applied post-query
            pass
        if languages:
            filter_dict["language"] = {"$in": languages}
        
        # Search vector store
        try:
            results = self.vector_store.search(
                query=query,
                collection=collection,
                limit=limit * 2,  # Over-fetch for filtering
                filter=filter_dict if filter_dict else None,
            )
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
        
        # Convert to SearchResult and filter
        search_results = []
        for doc, score in results:
            # Skip low scores
            if score < threshold:
                continue
            
            # Apply file pattern filter
            if file_patterns:
                path = doc.metadata.get("path", doc.metadata.get("source", ""))
                if not any(self._matches_pattern(path, p) for p in file_patterns):
                    continue
            
            result = SearchResult(
                id=doc.id,
                path=doc.metadata.get("path", doc.metadata.get("source", "")),
                content=doc.content,
                score=score,
                language=doc.metadata.get("language"),
                line_start=doc.metadata.get("line_start"),
                line_end=doc.metadata.get("line_end"),
                project_id=doc.metadata.get("project_id"),
                symbols=doc.metadata.get("symbols", []),
                metadata=doc.metadata,
            )
            search_results.append(result)
            
            if len(search_results) >= limit:
                break
        
        return search_results
    
    def search_across_projects(
        self,
        query: str,
        project_ids: List[str],
        limit_per_project: int = 5,
        threshold: float = 0.5,
    ) -> Dict[str, List[SearchResult]]:
        """
        Search across multiple projects.
        
        Args:
            query: Natural language search query
            project_ids: List of project IDs to search
            limit_per_project: Maximum results per project
            threshold: Minimum similarity score
            
        Returns:
            Dictionary mapping project_id to search results
        """
        results = {}
        
        for project_id in project_ids:
            try:
                project_results = self.semantic_search(
                    query=query,
                    project_id=project_id,
                    limit=limit_per_project,
                    threshold=threshold,
                )
                results[project_id] = project_results
            except Exception as e:
                logger.error(f"Search failed for project {project_id}: {e}")
                results[project_id] = []
        
        return results
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if a path matches a glob pattern."""
        from pathlib import PurePath
        import fnmatch
        
        # Normalize pattern
        if not pattern.startswith("*"):
            pattern = "**/" + pattern
        
        return fnmatch.fnmatch(path.lower(), pattern.lower())
    
    # =========================================================================
    # Symbol Extraction
    # =========================================================================
    
    def extract_symbols(
        self,
        path: Union[str, Path],
        content: str,
        language: Optional[str] = None,
    ) -> List[CodeSymbol]:
        """
        Extract code symbols from a file.
        
        This extracts:
        - Functions/methods
        - Classes
        - Constants
        - Type definitions
        
        Args:
            path: File path
            content: File content
            language: Programming language (auto-detected if None)
            
        Returns:
            List of CodeSymbol objects
        """
        path_str = str(path)
        
        # Auto-detect language
        if language is None:
            language = self._detect_language(path_str)
        
        symbols = []
        
        if language == "python":
            symbols = self._extract_python_symbols(path_str, content)
        elif language in ("javascript", "typescript", "jsx", "tsx"):
            symbols = self._extract_js_symbols(path_str, content)
        elif language == "java":
            symbols = self._extract_java_symbols(path_str, content)
        elif language == "go":
            symbols = self._extract_go_symbols(path_str, content)
        
        return symbols
    
    def _detect_language(self, path: str) -> Optional[str]:
        """Detect language from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "jsx",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
        }
        
        ext = Path(path).suffix.lower()
        return ext_map.get(ext)
    
    def _extract_python_symbols(self, path: str, content: str) -> List[CodeSymbol]:
        """Extract symbols from Python code."""
        symbols = []
        lines = content.split("\n")
        
        # Regex patterns
        func_pattern = re.compile(r'^(\s*)def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*[^:]+)?:')
        class_pattern = re.compile(r'^class\s+(\w+)(?:\([^)]*\))?\s*:')
        const_pattern = re.compile(r'^([A-Z][A-Z0-9_]+)\s*=')
        
        current_class = None
        current_indent = 0
        
        for i, line in enumerate(lines, 1):
            # Class definition
            class_match = class_pattern.match(line)
            if class_match:
                current_class = class_match.group(1)
                current_indent = 0
                
                # Get docstring
                docstring = self._get_python_docstring(lines, i)
                
                symbols.append(CodeSymbol(
                    name=current_class,
                    symbol_type="class",
                    path=path,
                    line_number=i,
                    signature=line.strip(),
                    docstring=docstring,
                    language="python",
                ))
                continue
            
            # Function/method definition
            func_match = func_pattern.match(line)
            if func_match:
                indent = len(func_match.group(1))
                name = func_match.group(2)
                params = func_match.group(3)
                
                # Check if it's a method
                parent = None
                if indent > 0 and current_class:
                    parent = current_class
                    symbol_type = "method"
                else:
                    symbol_type = "function"
                    current_class = None
                
                # Get docstring
                docstring = self._get_python_docstring(lines, i)
                
                symbols.append(CodeSymbol(
                    name=name,
                    symbol_type=symbol_type,
                    path=path,
                    line_number=i,
                    signature=f"def {name}({params})",
                    docstring=docstring,
                    language="python",
                    parent=parent,
                ))
                continue
            
            # Constant
            const_match = const_pattern.match(line)
            if const_match:
                symbols.append(CodeSymbol(
                    name=const_match.group(1),
                    symbol_type="constant",
                    path=path,
                    line_number=i,
                    language="python",
                ))
        
        return symbols
    
    def _get_python_docstring(self, lines: List[str], start_line: int) -> Optional[str]:
        """Extract docstring following a definition."""
        if start_line >= len(lines):
            return None
        
        # Look for docstring in next few lines
        for i in range(start_line, min(start_line + 3, len(lines))):
            line = lines[i].strip()
            
            if line.startswith('"""') or line.startswith("'''"):
                quote = line[:3]
                
                # Single line docstring
                if line.count(quote) >= 2:
                    return line[3:-3].strip()
                
                # Multi-line docstring
                docstring_lines = [line[3:]]
                for j in range(i + 1, min(i + 20, len(lines))):
                    next_line = lines[j]
                    if quote in next_line:
                        docstring_lines.append(next_line.split(quote)[0])
                        break
                    docstring_lines.append(next_line)
                
                return "\n".join(docstring_lines).strip()
        
        return None
    
    def _extract_js_symbols(self, path: str, content: str) -> List[CodeSymbol]:
        """Extract symbols from JavaScript/TypeScript code."""
        symbols = []
        lines = content.split("\n")
        
        # Regex patterns
        func_pattern = re.compile(
            r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*(?:<[^>]*>)?\s*\(([^)]*)\)'
        )
        arrow_pattern = re.compile(
            r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=])\s*=>'
        )
        class_pattern = re.compile(
            r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?\s*\{'
        )
        interface_pattern = re.compile(
            r'(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+[\w,\s]+)?\s*\{'
        )
        
        for i, line in enumerate(lines, 1):
            # Class
            class_match = class_pattern.search(line)
            if class_match:
                symbols.append(CodeSymbol(
                    name=class_match.group(1),
                    symbol_type="class",
                    path=path,
                    line_number=i,
                    signature=line.strip(),
                    language="javascript",
                ))
                continue
            
            # Interface (TypeScript)
            interface_match = interface_pattern.search(line)
            if interface_match:
                symbols.append(CodeSymbol(
                    name=interface_match.group(1),
                    symbol_type="interface",
                    path=path,
                    line_number=i,
                    signature=line.strip(),
                    language="typescript",
                ))
                continue
            
            # Function
            func_match = func_pattern.search(line)
            if func_match:
                symbols.append(CodeSymbol(
                    name=func_match.group(1),
                    symbol_type="function",
                    path=path,
                    line_number=i,
                    signature=f"function {func_match.group(1)}({func_match.group(2)})",
                    language="javascript",
                ))
                continue
            
            # Arrow function
            arrow_match = arrow_pattern.search(line)
            if arrow_match:
                symbols.append(CodeSymbol(
                    name=arrow_match.group(1),
                    symbol_type="function",
                    path=path,
                    line_number=i,
                    signature=line.strip()[:80],
                    language="javascript",
                ))
        
        return symbols
    
    def _extract_java_symbols(self, path: str, content: str) -> List[CodeSymbol]:
        """Extract symbols from Java code."""
        symbols = []
        lines = content.split("\n")
        
        class_pattern = re.compile(
            r'(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*class\s+(\w+)'
        )
        method_pattern = re.compile(
            r'(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\('
        )
        
        current_class = None
        
        for i, line in enumerate(lines, 1):
            class_match = class_pattern.search(line)
            if class_match:
                current_class = class_match.group(1)
                symbols.append(CodeSymbol(
                    name=current_class,
                    symbol_type="class",
                    path=path,
                    line_number=i,
                    signature=line.strip(),
                    language="java",
                ))
                continue
            
            method_match = method_pattern.search(line)
            if method_match and not any(kw in line for kw in ['if(', 'while(', 'for(']):
                symbols.append(CodeSymbol(
                    name=method_match.group(1),
                    symbol_type="method",
                    path=path,
                    line_number=i,
                    signature=line.strip()[:100],
                    language="java",
                    parent=current_class,
                ))
        
        return symbols
    
    def _extract_go_symbols(self, path: str, content: str) -> List[CodeSymbol]:
        """Extract symbols from Go code."""
        symbols = []
        lines = content.split("\n")
        
        func_pattern = re.compile(r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(')
        type_pattern = re.compile(r'type\s+(\w+)\s+(?:struct|interface)')
        
        for i, line in enumerate(lines, 1):
            type_match = type_pattern.search(line)
            if type_match:
                symbol_type = "struct" if "struct" in line else "interface"
                symbols.append(CodeSymbol(
                    name=type_match.group(1),
                    symbol_type=symbol_type,
                    path=path,
                    line_number=i,
                    signature=line.strip(),
                    language="go",
                ))
                continue
            
            func_match = func_pattern.search(line)
            if func_match:
                symbols.append(CodeSymbol(
                    name=func_match.group(1),
                    symbol_type="function",
                    path=path,
                    line_number=i,
                    signature=line.strip()[:100],
                    language="go",
                ))
        
        return symbols
    
    # =========================================================================
    # Enhanced Indexing
    # =========================================================================
    
    def index_project_with_symbols(
        self,
        project_id: str,
        directory: Union[str, Path],
        force: bool = False,
        patterns: Optional[List[str]] = None,
        extract_symbols: bool = True,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Index a project with symbol extraction.
        
        This enhances the standard indexing with:
        - Symbol extraction for code navigation
        - Enhanced metadata for search
        
        Args:
            project_id: Project ID
            directory: Directory to index
            force: Force re-indexing
            patterns: File patterns to include
            extract_symbols: Whether to extract symbols
            progress_callback: Callback for progress updates
            
        Returns:
            Indexing results with symbol counts
        """
        # Perform base indexing
        result = self.index_project(
            project_id=project_id,
            directory=directory,
            force=force,
            patterns=patterns,
            progress_callback=progress_callback,
        )
        
        if result.get("status") != "completed":
            return result
        
        # Extract symbols if requested
        if extract_symbols:
            symbol_count = self._index_symbols(project_id, Path(directory))
            result["symbols_extracted"] = symbol_count
        
        return result
    
    def _index_symbols(
        self,
        project_id: str,
        directory: Path,
    ) -> int:
        """Extract and index symbols for a project."""
        total_symbols = 0
        
        # Load files
        files = self.file_loader.load_directory(
            directory,
            patterns=self.DEFAULT_CODE_PATTERNS,
            recursive=True,
        )
        
        for loaded_file in files:
            try:
                symbols = self.extract_symbols(
                    path=loaded_file.path,
                    content=loaded_file.content,
                    language=loaded_file.language,
                )
                
                path_str = str(loaded_file.path)
                self._symbol_index[path_str] = symbols
                total_symbols += len(symbols)
                
            except Exception as e:
                logger.debug(f"Symbol extraction failed for {loaded_file.path}: {e}")
        
        logger.info(f"Extracted {total_symbols} symbols for project {project_id}")
        return total_symbols
    
    def search_symbols(
        self,
        query: str,
        project_id: Optional[str] = None,
        symbol_types: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[CodeSymbol]:
        """
        Search for symbols by name.
        
        Args:
            query: Symbol name or partial match
            project_id: Optional project to search within
            symbol_types: Filter by symbol types (function, class, method)
            limit: Maximum results
            
        Returns:
            List of matching symbols
        """
        results = []
        query_lower = query.lower()
        
        for path, symbols in self._symbol_index.items():
            for symbol in symbols:
                # Filter by type
                if symbol_types and symbol.symbol_type not in symbol_types:
                    continue
                
                # Match by name
                if query_lower in symbol.name.lower():
                    results.append(symbol)
                    
                    if len(results) >= limit:
                        break
            
            if len(results) >= limit:
                break
        
        # Sort by relevance (exact matches first)
        results.sort(key=lambda s: (
            0 if s.name.lower() == query_lower else 1,
            0 if s.name.lower().startswith(query_lower) else 1,
            s.name.lower(),
        ))
        
        return results[:limit]
    
    def get_symbols_for_file(self, path: Union[str, Path]) -> List[CodeSymbol]:
        """
        Get all symbols for a file.
        
        Args:
            path: File path
            
        Returns:
            List of symbols in the file
        """
        path_str = str(Path(path).resolve())
        return self._symbol_index.get(path_str, [])
    
    # =========================================================================
    # Project Management
    # =========================================================================
    
    def get_project_symbols_summary(self, project_id: str) -> Dict[str, Any]:
        """
        Get a summary of symbols in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Summary with counts by type, language, etc.
        """
        summary = {
            "project_id": project_id,
            "total_symbols": 0,
            "by_type": {},
            "by_language": {},
            "files_with_symbols": 0,
        }
        
        for symbols in self._symbol_index.values():
            if not symbols:
                continue
            
            # Check if symbols belong to this project
            # (simplified - in production, filter by project directory)
            summary["files_with_symbols"] += 1
            
            for symbol in symbols:
                summary["total_symbols"] += 1
                
                # By type
                symbol_type = symbol.symbol_type
                summary["by_type"][symbol_type] = summary["by_type"].get(symbol_type, 0) + 1
                
                # By language
                lang = symbol.language or "unknown"
                summary["by_language"][lang] = summary["by_language"].get(lang, 0) + 1
        
        return summary
