"""
File loading utilities for the indexing module.

This module provides utilities for loading files from disk
with support for various file types.

Example:
    >>> from agentic_assistants.indexing.loader import FileLoader
    >>> 
    >>> loader = FileLoader()
    >>> files = loader.load_directory("./src", patterns=["*.py"])
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

import pathspec

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class LoadedFile:
    """
    A loaded file with its content and metadata.
    
    Attributes:
        path: Path to the file
        content: File content as string
        language: Detected programming language
        size_bytes: File size in bytes
        metadata: Additional metadata
    """
    
    path: Path
    content: str
    language: Optional[str] = None
    size_bytes: int = 0
    metadata: dict = field(default_factory=dict)

    @property
    def extension(self) -> str:
        """Get file extension."""
        return self.path.suffix.lower()

    @property
    def name(self) -> str:
        """Get file name."""
        return self.path.name

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "path": str(self.path),
            "content": self.content,
            "language": self.language,
            "size_bytes": self.size_bytes,
            "metadata": self.metadata,
        }


class FileLoader:
    """
    Load files from disk with filtering and metadata extraction.
    
    This class provides:
    - File loading with encoding detection
    - Directory traversal with pattern matching
    - .gitignore support
    - Language detection
    
    Attributes:
        max_file_size: Maximum file size to load in bytes
    """

    # Common programming language extensions
    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".r": "r",
        ".sql": "sql",
        ".sh": "shell",
        ".bash": "shell",
        ".zsh": "shell",
        ".ps1": "powershell",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".xml": "xml",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".md": "markdown",
        ".rst": "restructuredtext",
        ".toml": "toml",
        ".ini": "ini",
        ".cfg": "ini",
    }

    # Default patterns to ignore
    DEFAULT_IGNORE = [
        "__pycache__",
        "*.pyc",
        ".git",
        ".svn",
        ".hg",
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
        "dist",
        "build",
        "*.egg-info",
        ".tox",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "*.min.js",
        "*.min.css",
        "*.map",
        "*.lock",
        "package-lock.json",
        "yarn.lock",
        "poetry.lock",
    ]

    def __init__(
        self,
        max_file_size: int = 1024 * 1024,  # 1MB default
        respect_gitignore: bool = True,
        additional_ignores: Optional[list[str]] = None,
    ):
        """
        Initialize the file loader.
        
        Args:
            max_file_size: Maximum file size to load in bytes
            respect_gitignore: Whether to respect .gitignore files
            additional_ignores: Additional patterns to ignore
        """
        self.max_file_size = max_file_size
        self.respect_gitignore = respect_gitignore
        self.additional_ignores = additional_ignores or []

    def _detect_language(self, path: Path) -> Optional[str]:
        """Detect the programming language from file extension."""
        return self.LANGUAGE_MAP.get(path.suffix.lower())

    def _load_gitignore(self, directory: Path) -> Optional[pathspec.PathSpec]:
        """Load .gitignore patterns from a directory."""
        gitignore_path = directory / ".gitignore"
        
        if not gitignore_path.exists():
            return None
        
        try:
            patterns = gitignore_path.read_text().splitlines()
            return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
        except Exception as e:
            logger.warning(f"Failed to load .gitignore: {e}")
            return None

    def _should_ignore(
        self,
        path: Path,
        base_dir: Path,
        gitignore_spec: Optional[pathspec.PathSpec],
    ) -> bool:
        """Check if a path should be ignored."""
        relative_path = path.relative_to(base_dir)
        path_str = str(relative_path)
        
        # Check default ignores
        for pattern in self.DEFAULT_IGNORE:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", [pattern])
            if spec.match_file(path_str):
                return True
        
        # Check additional ignores
        for pattern in self.additional_ignores:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", [pattern])
            if spec.match_file(path_str):
                return True
        
        # Check gitignore
        if gitignore_spec and gitignore_spec.match_file(path_str):
            return True
        
        return False

    def load_file(self, path: Union[str, Path]) -> Optional[LoadedFile]:
        """
        Load a single file.
        
        Args:
            path: Path to the file
        
        Returns:
            LoadedFile or None if file can't be loaded
        """
        path = Path(path)
        
        if not path.exists():
            logger.warning(f"File not found: {path}")
            return None
        
        if not path.is_file():
            logger.warning(f"Not a file: {path}")
            return None
        
        # Check file size
        size = path.stat().st_size
        if size > self.max_file_size:
            logger.warning(f"File too large ({size} bytes): {path}")
            return None
        
        # Try to read file
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding="latin-1")
            except Exception as e:
                logger.warning(f"Failed to read file: {path} - {e}")
                return None
        except Exception as e:
            logger.warning(f"Failed to read file: {path} - {e}")
            return None
        
        return LoadedFile(
            path=path.resolve(),
            content=content,
            language=self._detect_language(path),
            size_bytes=size,
            metadata={
                "extension": path.suffix,
                "name": path.name,
            },
        )

    def load_directory(
        self,
        directory: Union[str, Path],
        patterns: Optional[list[str]] = None,
        recursive: bool = True,
    ) -> list[LoadedFile]:
        """
        Load files from a directory.
        
        Args:
            directory: Directory path
            patterns: File patterns to include (e.g., ["*.py", "*.js"])
            recursive: Whether to recurse into subdirectories
        
        Returns:
            List of LoadedFile objects
        """
        directory = Path(directory).resolve()
        
        if not directory.exists():
            logger.warning(f"Directory not found: {directory}")
            return []
        
        if not directory.is_dir():
            logger.warning(f"Not a directory: {directory}")
            return []
        
        # Load gitignore
        gitignore_spec = None
        if self.respect_gitignore:
            gitignore_spec = self._load_gitignore(directory)
        
        # Build pattern spec for includes
        include_spec = None
        if patterns:
            include_spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
        
        # Collect files
        files = []
        
        if recursive:
            file_iterator = directory.rglob("*")
        else:
            file_iterator = directory.glob("*")
        
        for path in file_iterator:
            if not path.is_file():
                continue
            
            # Check if ignored
            if self._should_ignore(path, directory, gitignore_spec):
                continue
            
            # Check if matches patterns
            if include_spec:
                relative = path.relative_to(directory)
                if not include_spec.match_file(str(relative)):
                    continue
            
            # Load file
            loaded = self.load_file(path)
            if loaded:
                files.append(loaded)
        
        logger.info(f"Loaded {len(files)} files from {directory}")
        return files

    def get_file_stats(
        self,
        directory: Union[str, Path],
        patterns: Optional[list[str]] = None,
    ) -> dict:
        """
        Get statistics about files in a directory.
        
        Args:
            directory: Directory path
            patterns: File patterns to include
        
        Returns:
            Dictionary with file statistics
        """
        files = self.load_directory(directory, patterns)
        
        languages = {}
        total_size = 0
        total_lines = 0
        
        for f in files:
            lang = f.language or "unknown"
            if lang not in languages:
                languages[lang] = {"count": 0, "size": 0, "lines": 0}
            
            languages[lang]["count"] += 1
            languages[lang]["size"] += f.size_bytes
            languages[lang]["lines"] += f.content.count("\n") + 1
            
            total_size += f.size_bytes
            total_lines += f.content.count("\n") + 1
        
        return {
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_lines": total_lines,
            "by_language": languages,
        }

