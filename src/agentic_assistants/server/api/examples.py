"""
Examples API Router.

This module provides REST endpoints for listing and importing example projects
from the examples directory. Users can bootstrap new projects from bundled
example templates.
"""

import shutil
from pathlib import Path
from typing import List, Optional

import yaml
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/examples", tags=["examples"])


# === Request/Response Models ===


class ExampleFile(BaseModel):
    """A file in an example project."""

    name: str
    path: str
    is_directory: bool = False


class ExampleEntry(BaseModel):
    """An example project entry."""

    slug: str = Field(..., description="Example directory name")
    name: str = Field(..., description="Human-friendly name")
    description: str = Field(default="", description="Description from README")
    files: List[ExampleFile] = Field(default_factory=list, description="List of files")
    config_preview: str = Field(default="", description="First 500 chars of config.yaml")
    has_readme: bool = Field(default=False)
    has_config: bool = Field(default=False)
    tags: List[str] = Field(default_factory=list, description="Tags extracted from config")


class ExampleListResponse(BaseModel):
    """Response containing list of examples."""

    items: List[ExampleEntry]
    total: int


class ImportRequest(BaseModel):
    """Request to import an example as a new project."""

    example_slug: str = Field(..., description="Example to import")
    project_name: str = Field(..., description="Name for the new project")
    description: Optional[str] = Field(default=None, description="Override description")
    tags: Optional[List[str]] = Field(default=None, description="Override tags")
    copy_files: bool = Field(default=False, description="Copy example files to project directory")


class ImportResponse(BaseModel):
    """Response from import operation."""

    project_id: str
    project_name: str
    example_slug: str
    files_copied: int = 0
    message: str


# === Helper Functions ===


def _resolve_examples_dir() -> Optional[Path]:
    """Locate the examples directory relative to the project root."""
    # Path from examples.py: src/agentic_assistants/server/api/examples.py
    # Need to go up 4 levels to reach repo root: api -> server -> agentic_assistants -> src -> repo_root
    repo_root = Path(__file__).resolve().parents[4]
    
    candidates = [
        repo_root / "examples",  # repo root/examples
        Path.cwd() / "examples",  # current working directory
        Path.cwd().parent / "examples",  # one level up from cwd
    ]
    
    logger.debug(f"Looking for examples directory. Candidates: {candidates}")
    
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            logger.info(f"Found examples directory at: {candidate}")
            return candidate
    
    logger.warning(f"Examples directory not found. Checked: {candidates}")
    return None


# Resolve at module load - will be rechecked at runtime for reliability
_EXAMPLES_DIR_CACHE = None


def get_examples_dir() -> Optional[Path]:
    """Get the examples directory, resolving it if not cached."""
    global _EXAMPLES_DIR_CACHE
    if _EXAMPLES_DIR_CACHE is None:
        _EXAMPLES_DIR_CACHE = _resolve_examples_dir()
    return _EXAMPLES_DIR_CACHE


# For backwards compatibility
EXAMPLES_DIR = _resolve_examples_dir()


def _extract_readme_description(readme_path: Path, max_length: int = 300) -> str:
    """Extract a description from README.md."""
    try:
        content = readme_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Skip title and separators
        desc_lines = []
        started = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if started and desc_lines:
                    break
                continue
            if stripped.startswith("#") or stripped.startswith("=") or stripped.startswith("-"):
                if desc_lines:
                    break
                started = True
                continue
            if started:
                desc_lines.append(stripped)
                if len(" ".join(desc_lines)) > max_length:
                    break

        desc = " ".join(desc_lines)
        if len(desc) > max_length:
            desc = desc[:max_length - 3] + "..."
        return desc
    except Exception:
        return ""


def _extract_config_tags(config_path: Path) -> List[str]:
    """Extract tags from config.yaml if present."""
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        if isinstance(config, dict):
            tags = config.get("ingestion", {}).get("tags", [])
            if isinstance(tags, list):
                return tags
    except Exception:
        pass
    return []


def _get_example_name(slug: str, readme_path: Optional[Path]) -> str:
    """Get a human-friendly name from slug or README title."""
    if readme_path and readme_path.exists():
        try:
            content = readme_path.read_text(encoding="utf-8")
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped and not stripped.startswith("="):
                    if stripped.startswith("#"):
                        return stripped.lstrip("#").strip()
                    else:
                        return stripped
        except Exception:
            pass
    # Fallback: convert slug to title case
    return slug.replace("-", " ").replace("_", " ").title()


def _list_example_files(example_dir: Path) -> List[ExampleFile]:
    """List all files in an example directory."""
    files = []
    try:
        for item in example_dir.iterdir():
            if item.name.startswith("."):
                continue
            files.append(
                ExampleFile(
                    name=item.name,
                    path=str(item.relative_to(example_dir)),
                    is_directory=item.is_dir(),
                )
            )
        files.sort(key=lambda f: (f.is_directory, f.name))
    except Exception:
        pass
    return files


def _get_store() -> ControlPanelStore:
    """Get the control panel store instance."""
    return ControlPanelStore.get_instance()


# === Endpoints ===


@router.get("/debug")
async def debug_examples_dir() -> dict:
    """Debug endpoint to check examples directory resolution."""
    repo_root = Path(__file__).resolve().parents[4]
    cwd = Path.cwd()
    
    candidates = [
        repo_root / "examples",
        cwd / "examples",
        cwd.parent / "examples",
    ]
    
    results = []
    for candidate in candidates:
        results.append({
            "path": str(candidate),
            "exists": candidate.exists(),
            "is_dir": candidate.is_dir() if candidate.exists() else False,
        })
    
    examples_dir = get_examples_dir()
    
    return {
        "resolved_dir": str(examples_dir) if examples_dir else None,
        "repo_root": str(repo_root),
        "cwd": str(cwd),
        "candidates": results,
        "examples_dir_contents": [
            item.name for item in examples_dir.iterdir()
        ] if examples_dir and examples_dir.exists() else [],
    }


@router.get("", response_model=ExampleListResponse)
async def list_examples() -> ExampleListResponse:
    """List all available example projects."""
    # Re-resolve to handle startup timing issues
    examples_dir = get_examples_dir()
    
    if not examples_dir or not examples_dir.exists():
        logger.warning(f"Examples directory not found. Checked: {examples_dir}")
        return ExampleListResponse(items=[], total=0)

    logger.info(f"Listing examples from: {examples_dir}")
    examples: List[ExampleEntry] = []

    for item in examples_dir.iterdir():
        # Only include directories that look like example projects
        if not item.is_dir():
            continue
        if item.name.startswith(".") or item.name.startswith("_"):
            continue

        readme_path = item / "README.md"
        config_path = item / "config.yaml"

        if not readme_path.exists() and not config_path.exists():
            # Skip directories without README or config
            continue

        config_preview = ""
        if config_path.exists():
            try:
                content = config_path.read_text(encoding="utf-8")
                config_preview = content[:500]
                if len(content) > 500:
                    config_preview += "..."
            except Exception:
                pass

        examples.append(
            ExampleEntry(
                slug=item.name,
                name=_get_example_name(item.name, readme_path if readme_path.exists() else None),
                description=_extract_readme_description(readme_path) if readme_path.exists() else "",
                files=_list_example_files(item),
                config_preview=config_preview,
                has_readme=readme_path.exists(),
                has_config=config_path.exists(),
                tags=_extract_config_tags(config_path) if config_path.exists() else [],
            )
        )

    examples.sort(key=lambda e: e.name.lower())

    return ExampleListResponse(items=examples, total=len(examples))


@router.get("/{slug}", response_model=ExampleEntry)
async def get_example(slug: str) -> ExampleEntry:
    """Get details about a specific example."""
    examples_dir = get_examples_dir()
    if not examples_dir:
        raise HTTPException(status_code=404, detail="Examples directory not found")

    example_dir = examples_dir / slug
    if not example_dir.exists() or not example_dir.is_dir():
        raise HTTPException(status_code=404, detail="Example not found")

    readme_path = example_dir / "README.md"
    config_path = example_dir / "config.yaml"

    config_preview = ""
    if config_path.exists():
        try:
            content = config_path.read_text(encoding="utf-8")
            config_preview = content[:500]
            if len(content) > 500:
                config_preview += "..."
        except Exception:
            pass

    return ExampleEntry(
        slug=slug,
        name=_get_example_name(slug, readme_path if readme_path.exists() else None),
        description=_extract_readme_description(readme_path) if readme_path.exists() else "",
        files=_list_example_files(example_dir),
        config_preview=config_preview,
        has_readme=readme_path.exists(),
        has_config=config_path.exists(),
        tags=_extract_config_tags(config_path) if config_path.exists() else [],
    )


@router.get("/{slug}/readme")
async def get_example_readme(slug: str) -> dict:
    """Get the full README content for an example."""
    examples_dir = get_examples_dir()
    if not examples_dir:
        raise HTTPException(status_code=404, detail="Examples directory not found")

    readme_path = examples_dir / slug / "README.md"
    if not readme_path.exists():
        raise HTTPException(status_code=404, detail="README not found")

    try:
        content = readme_path.read_text(encoding="utf-8")
        return {"slug": slug, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read README: {e}")


@router.get("/{slug}/config")
async def get_example_config(slug: str) -> dict:
    """Get the full config.yaml content for an example."""
    examples_dir = get_examples_dir()
    if not examples_dir:
        raise HTTPException(status_code=404, detail="Examples directory not found")

    config_path = examples_dir / slug / "config.yaml"
    if not config_path.exists():
        raise HTTPException(status_code=404, detail="Config not found")

    try:
        content = config_path.read_text(encoding="utf-8")
        return {"slug": slug, "content": content, "parsed": yaml.safe_load(content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read config: {e}")


@router.post("/import", response_model=ImportResponse)
async def import_example(request: ImportRequest) -> ImportResponse:
    """Import an example as a new project."""
    examples_dir = get_examples_dir()
    if not examples_dir:
        raise HTTPException(status_code=404, detail="Examples directory not found")

    example_dir = examples_dir / request.example_slug
    if not example_dir.exists():
        raise HTTPException(status_code=404, detail="Example not found")

    # Read example config
    config_path = example_dir / "config.yaml"
    readme_path = example_dir / "README.md"

    config_yaml = ""
    if config_path.exists():
        try:
            config_yaml = config_path.read_text(encoding="utf-8")
        except Exception:
            pass

    # Get description from request or README
    description = request.description
    if not description and readme_path.exists():
        description = _extract_readme_description(readme_path, max_length=500)

    # Get tags from request or config
    tags = request.tags
    if not tags:
        tags = _extract_config_tags(config_path) if config_path.exists() else []

    # Create the project
    store = _get_store()
    try:
        project = store.create_project(
            name=request.project_name,
            description=description or f"Imported from example: {request.example_slug}",
            config_yaml=config_yaml,
            status="draft",
            tags=tags,
            metadata={
                "imported_from": request.example_slug,
                "import_source": "examples",
            },
        )
    except Exception as e:
        logger.error(f"Failed to create project from example: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create project: {e}")

    files_copied = 0

    # Optionally copy files to project directory
    if request.copy_files:
        project_data_dir = Path("./data/projects") / project.id
        project_data_dir.mkdir(parents=True, exist_ok=True)

        try:
            for item in example_dir.iterdir():
                if item.name.startswith("."):
                    continue
                dest = project_data_dir / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                    files_copied += 1
                elif item.is_dir():
                    shutil.copytree(item, dest)
                    files_copied += sum(1 for _ in dest.rglob("*") if _.is_file())
        except Exception as e:
            logger.warning(f"Failed to copy some files: {e}")

    return ImportResponse(
        project_id=project.id,
        project_name=project.name,
        example_slug=request.example_slug,
        files_copied=files_copied,
        message=f"Successfully created project '{project.name}' from example '{request.example_slug}'",
    )
