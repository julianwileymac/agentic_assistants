"""
Documentation API router.

Serves framework documentation stored in the local `docs/` directory so the
Web UI can surface contextual help at runtime.
"""

import re
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/docs", tags=["docs"])


class DocEntry(BaseModel):
    """A single documentation entry."""

    slug: str = Field(..., description="Slug derived from filename")
    title: str = Field(..., description="Human-friendly title")
    path: str = Field(..., description="Relative filename")
    description: str = Field(default="", description="Brief description from content")


class DocContent(BaseModel):
    """Documentation content response."""

    slug: str
    title: str
    content: str
    headings: List[str] = Field(default_factory=list, description="List of headings for TOC")
    word_count: int = Field(default=0, description="Word count for reading time estimate")


class DocSearchResult(BaseModel):
    """Search result for documentation."""

    slug: str
    title: str
    snippet: str = Field(..., description="Context around matched text")
    match_count: int = Field(default=1, description="Number of matches in document")


class DocSearchResponse(BaseModel):
    """Response containing search results."""

    query: str
    results: List[DocSearchResult]
    total: int


def _resolve_docs_dir() -> Optional[Path]:
    """Locate the docs directory relative to the project root."""
    candidates = [
        Path(__file__).resolve().parents[5] / "docs",  # repo root/docs
        Path.cwd() / "docs",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


DOCS_DIR = _resolve_docs_dir()


def _extract_title(path: Path) -> str:
    """Extract the first markdown heading as the title, if present."""
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("#"):
                    return line.lstrip("#").strip()
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.warning(f"Failed to extract title from {path}: {exc}")
    return path.stem.replace("_", " ").title()


def _extract_description(path: Path) -> str:
    """Extract a brief description from the first paragraph after the title."""
    try:
        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
            in_content = False
            desc_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("#"):
                    if in_content:
                        break  # Stop at next heading
                    in_content = True
                    continue
                if in_content and stripped:
                    desc_lines.append(stripped)
                    if len(" ".join(desc_lines)) > 150:
                        break
                elif in_content and not stripped and desc_lines:
                    break  # End of first paragraph
            desc = " ".join(desc_lines)
            if len(desc) > 150:
                desc = desc[:147] + "..."
            return desc
    except Exception:
        return ""


def _extract_headings(content: str) -> List[str]:
    """Extract all markdown headings from content."""
    headings = []
    for line in content.split("\n"):
        if line.strip().startswith("#"):
            heading = line.strip().lstrip("#").strip()
            if heading:
                headings.append(heading)
    return headings


def _list_docs() -> List[DocEntry]:
    """Return metadata for markdown files in the docs directory."""
    if not DOCS_DIR:
        logger.warning("Docs directory not found; returning empty list.")
        return []

    entries: List[DocEntry] = []
    for path in DOCS_DIR.glob("*.md"):
        entries.append(
            DocEntry(
                slug=path.stem,
                title=_extract_title(path),
                path=path.name,
                description=_extract_description(path),
            )
        )

    entries.sort(key=lambda item: item.title.lower())
    return entries


def _get_doc_path(slug: str) -> Optional[Path]:
    """Resolve a slug to a docs path from the allowlist."""
    if not DOCS_DIR:
        return None
    for entry in _list_docs():
        if entry.slug == slug:
            return DOCS_DIR / entry.path
    return None


def _search_in_content(content: str, query: str, context_chars: int = 100) -> tuple[str, int]:
    """Search for query in content and return snippet with context."""
    query_lower = query.lower()
    content_lower = content.lower()
    
    # Count matches
    match_count = content_lower.count(query_lower)
    
    if match_count == 0:
        return "", 0
    
    # Find first match and extract context
    pos = content_lower.find(query_lower)
    start = max(0, pos - context_chars)
    end = min(len(content), pos + len(query) + context_chars)
    
    snippet = content[start:end]
    
    # Clean up snippet
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
    
    # Remove newlines for cleaner display
    snippet = " ".join(snippet.split())
    
    return snippet, match_count


@router.get("", response_model=List[DocEntry])
async def list_docs() -> List[DocEntry]:
    """List available documentation entries."""
    return _list_docs()


@router.get("/search", response_model=DocSearchResponse)
async def search_docs(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
) -> DocSearchResponse:
    """Search documentation content for matching text."""
    if not DOCS_DIR:
        return DocSearchResponse(query=q, results=[], total=0)
    
    results: List[DocSearchResult] = []
    
    for path in DOCS_DIR.glob("*.md"):
        try:
            content = path.read_text(encoding="utf-8")
            snippet, match_count = _search_in_content(content, q)
            
            if match_count > 0:
                results.append(
                    DocSearchResult(
                        slug=path.stem,
                        title=_extract_title(path),
                        snippet=snippet,
                        match_count=match_count,
                    )
                )
        except Exception as exc:
            logger.warning(f"Failed to search {path}: {exc}")
    
    # Sort by match count descending
    results.sort(key=lambda r: r.match_count, reverse=True)
    
    return DocSearchResponse(
        query=q,
        results=results[:limit],
        total=len(results),
    )


@router.get("/{slug}", response_model=DocContent)
async def get_doc(slug: str) -> DocContent:
    """Return the markdown content for a specific documentation slug."""
    doc_path = _get_doc_path(slug)
    if doc_path is None or not doc_path.exists():
        raise HTTPException(status_code=404, detail="Documentation not found")

    content = doc_path.read_text(encoding="utf-8")
    headings = _extract_headings(content)
    word_count = len(content.split())
    
    return DocContent(
        slug=slug,
        title=_extract_title(doc_path),
        content=content,
        headings=headings,
        word_count=word_count,
    )

