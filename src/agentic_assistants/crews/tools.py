"""
Custom CrewAI tools for repository indexing.

This module provides tools that agents can use to interact with:
- Local filesystem (reading files, listing directories)
- Vector stores (adding/searching documents)
- Code parsing utilities

Example:
    >>> from agentic_assistants.crews.tools import FileReaderTool
    >>> 
    >>> tool = FileReaderTool()
    >>> content = tool._run(file_path="./src/main.py")
"""

import json
from pathlib import Path
from typing import Any, Optional, Type, Union

from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.telemetry import get_tracer, trace_function
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.vectordb.base import Document, VectorStore

logger = get_logger(__name__)

# Try to import crewai tools
try:
    from crewai.tools import BaseTool
except ImportError:
    # Fallback base class if crewai not installed
    class BaseTool:
        """Fallback BaseTool class."""
        name: str = ""
        description: str = ""
        
        def _run(self, *args, **kwargs) -> Any:
            raise NotImplementedError


class FileReaderInput(BaseModel):
    """Input schema for FileReaderTool."""
    
    file_path: str = Field(
        description="Path to the file to read (relative or absolute)"
    )
    encoding: str = Field(
        default="utf-8",
        description="File encoding (default: utf-8)"
    )


class FileReaderTool(BaseTool):
    """
    Tool for reading file contents.
    
    This tool allows agents to read the contents of local files,
    with support for different encodings and size limits.
    """
    
    name: str = "file_reader"
    description: str = (
        "Read the contents of a file. Provide the file path to read. "
        "Returns the file content as a string. Use this to examine code files, "
        "configuration files, documentation, etc."
    )
    args_schema: Type[BaseModel] = FileReaderInput
    
    max_file_size: int = 1024 * 1024  # 1MB default
    base_path: Optional[Path] = None
    
    def __init__(
        self,
        max_file_size: int = 1024 * 1024,
        base_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ):
        """
        Initialize the file reader tool.
        
        Args:
            max_file_size: Maximum file size to read in bytes
            base_path: Base path for relative file paths
        """
        super().__init__(**kwargs)
        self.max_file_size = max_file_size
        self.base_path = Path(base_path) if base_path else None
    
    @trace_function(attributes={"tool": "file_reader"})
    def _run(
        self,
        file_path: str,
        encoding: str = "utf-8",
    ) -> str:
        """
        Read file contents.
        
        Args:
            file_path: Path to the file
            encoding: File encoding
        
        Returns:
            File contents as string
        """
        try:
            path = Path(file_path)
            if self.base_path and not path.is_absolute():
                path = self.base_path / path
            
            path = path.resolve()
            
            if not path.exists():
                return f"Error: File not found: {file_path}"
            
            if not path.is_file():
                return f"Error: Not a file: {file_path}"
            
            # Check file size
            size = path.stat().st_size
            if size > self.max_file_size:
                return (
                    f"Error: File too large ({size} bytes). "
                    f"Maximum size: {self.max_file_size} bytes"
                )
            
            content = path.read_text(encoding=encoding)
            logger.debug(f"Read file: {path} ({len(content)} chars)")
            return content
            
        except UnicodeDecodeError:
            return f"Error: Cannot decode file with encoding {encoding}"
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return f"Error reading file: {str(e)}"


class DirectoryListInput(BaseModel):
    """Input schema for DirectoryListTool."""
    
    directory_path: str = Field(
        description="Path to the directory to list"
    )
    pattern: str = Field(
        default="*",
        description="Glob pattern to filter files (e.g., '*.py', '**/*.js')"
    )
    recursive: bool = Field(
        default=True,
        description="Whether to list files recursively"
    )


class DirectoryListTool(BaseTool):
    """
    Tool for listing directory contents.
    
    This tool allows agents to explore the structure of a repository
    by listing files and directories with optional filtering.
    """
    
    name: str = "directory_list"
    description: str = (
        "List files and directories at a given path. Optionally filter by pattern "
        "(e.g., '*.py' for Python files, '**/*.ts' for all TypeScript files). "
        "Returns a list of file paths with their sizes."
    )
    args_schema: Type[BaseModel] = DirectoryListInput
    
    base_path: Optional[Path] = None
    max_results: int = 1000
    
    def __init__(
        self,
        base_path: Optional[Union[str, Path]] = None,
        max_results: int = 1000,
        **kwargs,
    ):
        """
        Initialize the directory list tool.
        
        Args:
            base_path: Base path for relative paths
            max_results: Maximum number of results to return
        """
        super().__init__(**kwargs)
        self.base_path = Path(base_path) if base_path else None
        self.max_results = max_results
    
    @trace_function(attributes={"tool": "directory_list"})
    def _run(
        self,
        directory_path: str,
        pattern: str = "*",
        recursive: bool = True,
    ) -> str:
        """
        List directory contents.
        
        Args:
            directory_path: Path to the directory
            pattern: Glob pattern for filtering
            recursive: Whether to recurse into subdirectories
        
        Returns:
            JSON string with file listing
        """
        try:
            path = Path(directory_path)
            if self.base_path and not path.is_absolute():
                path = self.base_path / path
            
            path = path.resolve()
            
            if not path.exists():
                return f"Error: Directory not found: {directory_path}"
            
            if not path.is_dir():
                return f"Error: Not a directory: {directory_path}"
            
            # Collect files
            if recursive and "**" not in pattern:
                pattern = f"**/{pattern}"
            
            files = []
            for file_path in path.glob(pattern):
                if file_path.is_file():
                    try:
                        rel_path = file_path.relative_to(path)
                        size = file_path.stat().st_size
                        files.append({
                            "path": str(rel_path),
                            "size": size,
                            "extension": file_path.suffix,
                        })
                    except (OSError, ValueError):
                        continue
                
                if len(files) >= self.max_results:
                    break
            
            # Sort by path
            files.sort(key=lambda x: x["path"])
            
            result = {
                "directory": str(path),
                "pattern": pattern,
                "file_count": len(files),
                "files": files,
            }
            
            logger.debug(f"Listed directory: {path} ({len(files)} files)")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error listing directory {directory_path}: {e}")
            return f"Error listing directory: {str(e)}"


class VectorStoreInput(BaseModel):
    """Input schema for VectorStoreTool."""
    
    action: str = Field(
        description="Action to perform: 'add', 'search', or 'count'"
    )
    collection: str = Field(
        default="default",
        description="Collection name in the vector store"
    )
    content: Optional[str] = Field(
        default=None,
        description="Content to add (for 'add' action)"
    )
    query: Optional[str] = Field(
        default=None,
        description="Search query (for 'search' action)"
    )
    metadata: Optional[str] = Field(
        default=None,
        description="JSON metadata for documents (for 'add' action)"
    )
    top_k: int = Field(
        default=5,
        description="Number of results to return (for 'search' action)"
    )


class VectorStoreTool(BaseTool):
    """
    Tool for interacting with vector stores.
    
    This tool allows agents to add documents to and search
    the vector database.
    """
    
    name: str = "vector_store"
    description: str = (
        "Interact with the vector database. Actions: "
        "'add' - Add content to the store with optional metadata. "
        "'search' - Search for similar content. "
        "'count' - Get document count in a collection."
    )
    args_schema: Type[BaseModel] = VectorStoreInput
    
    _vector_store: Optional[VectorStore] = None
    config: Optional[AgenticConfig] = None
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        config: Optional[AgenticConfig] = None,
        **kwargs,
    ):
        """
        Initialize the vector store tool.
        
        Args:
            vector_store: Pre-configured vector store instance
            config: Configuration for creating vector store
        """
        super().__init__(**kwargs)
        self._vector_store = vector_store
        self.config = config or AgenticConfig()
    
    @property
    def vector_store(self) -> VectorStore:
        """Get or create the vector store."""
        if self._vector_store is None:
            self._vector_store = VectorStore.create(config=self.config)
        return self._vector_store
    
    @trace_function(attributes={"tool": "vector_store"})
    def _run(
        self,
        action: str,
        collection: str = "default",
        content: Optional[str] = None,
        query: Optional[str] = None,
        metadata: Optional[str] = None,
        top_k: int = 5,
    ) -> str:
        """
        Execute vector store action.
        
        Args:
            action: Action to perform
            collection: Collection name
            content: Content to add
            query: Search query
            metadata: JSON metadata
            top_k: Number of search results
        
        Returns:
            Result as JSON string
        """
        try:
            if action == "add":
                if not content:
                    return "Error: 'content' is required for 'add' action"
                
                # Parse metadata if provided
                meta = {}
                if metadata:
                    try:
                        meta = json.loads(metadata)
                    except json.JSONDecodeError:
                        return "Error: Invalid JSON in metadata"
                
                # Create document
                import uuid
                doc = Document(
                    id=str(uuid.uuid4()),
                    content=content,
                    metadata=meta,
                )
                
                # Add to store
                ids = self.vector_store.add(doc, collection=collection)
                
                result = {
                    "action": "add",
                    "collection": collection,
                    "document_id": ids[0] if ids else None,
                    "success": len(ids) > 0,
                }
                return json.dumps(result)
            
            elif action == "search":
                if not query:
                    return "Error: 'query' is required for 'search' action"
                
                results = self.vector_store.search(
                    query=query,
                    collection=collection,
                    top_k=top_k,
                )
                
                result = {
                    "action": "search",
                    "collection": collection,
                    "query": query,
                    "results": [
                        {
                            "id": r.document.id,
                            "content": r.document.content[:500],  # Truncate
                            "score": r.score,
                            "metadata": r.document.metadata,
                        }
                        for r in results
                    ],
                }
                return json.dumps(result, indent=2)
            
            elif action == "count":
                count = self.vector_store.count(collection)
                result = {
                    "action": "count",
                    "collection": collection,
                    "count": count,
                }
                return json.dumps(result)
            
            else:
                return f"Error: Unknown action '{action}'. Use 'add', 'search', or 'count'"
                
        except Exception as e:
            logger.error(f"Vector store error: {e}")
            return f"Error: {str(e)}"


class CodeParserInput(BaseModel):
    """Input schema for CodeParserTool."""
    
    content: str = Field(
        description="Source code content to parse"
    )
    language: Optional[str] = Field(
        default=None,
        description="Programming language (auto-detected if not provided)"
    )


class CodeParserTool(BaseTool):
    """
    Tool for parsing and analyzing source code.
    
    This tool extracts structural information from code:
    - Functions/methods
    - Classes
    - Imports
    - Comments/docstrings
    """
    
    name: str = "code_parser"
    description: str = (
        "Parse source code to extract structural information. "
        "Returns functions, classes, imports, and documentation found in the code. "
        "Optionally specify the programming language."
    )
    args_schema: Type[BaseModel] = CodeParserInput
    
    @trace_function(attributes={"tool": "code_parser"})
    def _run(
        self,
        content: str,
        language: Optional[str] = None,
    ) -> str:
        """
        Parse source code.
        
        Args:
            content: Source code content
            language: Programming language
        
        Returns:
            JSON with parsed structure
        """
        try:
            result = self._parse_code(content, language)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Code parsing error: {e}")
            return f"Error parsing code: {str(e)}"
    
    def _parse_code(self, content: str, language: Optional[str]) -> dict:
        """Parse code and extract structure."""
        import re
        
        # Detect language if not provided
        if not language:
            language = self._detect_language(content)
        
        result = {
            "language": language,
            "line_count": len(content.splitlines()),
            "char_count": len(content),
            "functions": [],
            "classes": [],
            "imports": [],
            "comments": [],
        }
        
        if language == "python":
            result.update(self._parse_python(content))
        elif language in ("javascript", "typescript"):
            result.update(self._parse_javascript(content))
        else:
            # Generic parsing
            result.update(self._parse_generic(content))
        
        return result
    
    def _detect_language(self, content: str) -> str:
        """Detect programming language from content."""
        # Simple heuristics
        if "def " in content and "import " in content:
            return "python"
        if "function " in content or "const " in content or "=>" in content:
            return "javascript"
        if "interface " in content and ":" in content:
            return "typescript"
        if "#include" in content:
            return "c"
        if "package " in content and "func " in content:
            return "go"
        if "class " in content and "{" in content:
            return "java"
        return "unknown"
    
    def _parse_python(self, content: str) -> dict:
        """Parse Python code."""
        import re
        
        functions = []
        classes = []
        imports = []
        comments = []
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Imports
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports.append({
                    "line": i + 1,
                    "statement": stripped,
                })
            
            # Functions
            func_match = re.match(r'^def\s+(\w+)\s*\(([^)]*)\)', stripped)
            if func_match:
                functions.append({
                    "name": func_match.group(1),
                    "params": func_match.group(2),
                    "line": i + 1,
                })
            
            # Classes
            class_match = re.match(r'^class\s+(\w+)(?:\(([^)]*)\))?:', stripped)
            if class_match:
                classes.append({
                    "name": class_match.group(1),
                    "bases": class_match.group(2) or "",
                    "line": i + 1,
                })
            
            # Comments
            if stripped.startswith("#"):
                comments.append({
                    "line": i + 1,
                    "text": stripped[1:].strip(),
                })
        
        # Extract docstrings
        docstring_pattern = r'"""(.*?)"""'
        docstrings = re.findall(docstring_pattern, content, re.DOTALL)
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "comments": comments,
            "docstring_count": len(docstrings),
        }
    
    def _parse_javascript(self, content: str) -> dict:
        """Parse JavaScript/TypeScript code."""
        import re
        
        functions = []
        classes = []
        imports = []
        comments = []
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Imports
            if stripped.startswith("import ") or stripped.startswith("require("):
                imports.append({
                    "line": i + 1,
                    "statement": stripped[:100],
                })
            
            # Functions
            func_patterns = [
                r'function\s+(\w+)\s*\(([^)]*)\)',
                r'const\s+(\w+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>',
                r'(\w+)\s*:\s*(?:async\s*)?\(([^)]*)\)\s*=>',
            ]
            for pattern in func_patterns:
                match = re.search(pattern, stripped)
                if match:
                    functions.append({
                        "name": match.group(1),
                        "params": match.group(2),
                        "line": i + 1,
                    })
                    break
            
            # Classes
            class_match = re.match(r'class\s+(\w+)(?:\s+extends\s+(\w+))?', stripped)
            if class_match:
                classes.append({
                    "name": class_match.group(1),
                    "extends": class_match.group(2) or "",
                    "line": i + 1,
                })
            
            # Comments
            if stripped.startswith("//"):
                comments.append({
                    "line": i + 1,
                    "text": stripped[2:].strip(),
                })
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "comments": comments,
        }
    
    def _parse_generic(self, content: str) -> dict:
        """Generic code parsing."""
        import re
        
        lines = content.splitlines()
        
        # Count common patterns
        function_count = len(re.findall(r'\bfunction\b|\bdef\b|\bfunc\b', content))
        class_count = len(re.findall(r'\bclass\b|\bstruct\b|\binterface\b', content))
        import_count = len(re.findall(r'\bimport\b|\b#include\b|\brequire\b', content))
        
        return {
            "functions": [{"count": function_count}],
            "classes": [{"count": class_count}],
            "imports": [{"count": import_count}],
            "comments": [],
        }


# Tool factory functions for easy creation
def create_file_tools(base_path: Optional[Union[str, Path]] = None) -> list:
    """
    Create file-related tools.
    
    Args:
        base_path: Base path for file operations
    
    Returns:
        List of file tools
    """
    return [
        FileReaderTool(base_path=base_path),
        DirectoryListTool(base_path=base_path),
        CodeParserTool(),
    ]


def create_vector_tools(
    vector_store: Optional[VectorStore] = None,
    config: Optional[AgenticConfig] = None,
) -> list:
    """
    Create vector store tools.
    
    Args:
        vector_store: Pre-configured vector store
        config: Configuration for creating vector store
    
    Returns:
        List of vector store tools
    """
    return [
        VectorStoreTool(vector_store=vector_store, config=config),
    ]


def create_all_tools(
    base_path: Optional[Union[str, Path]] = None,
    vector_store: Optional[VectorStore] = None,
    config: Optional[AgenticConfig] = None,
) -> list:
    """
    Create all available tools.
    
    Args:
        base_path: Base path for file operations
        vector_store: Pre-configured vector store
        config: Configuration
    
    Returns:
        List of all tools
    """
    tools = create_file_tools(base_path)
    tools.extend(create_vector_tools(vector_store, config))
    return tools

