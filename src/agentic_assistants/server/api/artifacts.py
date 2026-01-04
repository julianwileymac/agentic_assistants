"""
Artifact Management API Router.

This module provides REST endpoints for artifact management:
- Upload/download artifacts
- Tagging and grouping
- Shared artifact storage
- Linking artifacts to experiments
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


# === Request/Response Models ===


class ArtifactMetadata(BaseModel):
    """Metadata for an artifact."""
    
    id: str = Field(..., description="Artifact ID")
    name: str = Field(..., description="Artifact name")
    path: str = Field(..., description="Storage path")
    size: int = Field(0, description="File size in bytes")
    mime_type: Optional[str] = Field(None, description="MIME type")
    tags: list[str] = Field(default_factory=list, description="Tags")
    groups: list[str] = Field(default_factory=list, description="Groups")
    session_id: Optional[str] = Field(None, description="Associated session")
    experiment_id: Optional[str] = Field(None, description="Associated experiment")
    run_id: Optional[str] = Field(None, description="Associated run")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    description: Optional[str] = Field(None, description="Description")
    is_shared: bool = Field(False, description="Whether artifact is shared")


class ArtifactCreate(BaseModel):
    """Request to create artifact metadata."""
    
    name: str = Field(..., description="Artifact name")
    tags: list[str] = Field(default_factory=list, description="Tags")
    groups: list[str] = Field(default_factory=list, description="Groups")
    description: Optional[str] = Field(None, description="Description")
    session_id: Optional[str] = Field(None, description="Associated session")
    experiment_id: Optional[str] = Field(None, description="Associated experiment")
    run_id: Optional[str] = Field(None, description="Associated run")
    is_shared: bool = Field(False, description="Whether to share artifact")


class ArtifactUpdate(BaseModel):
    """Request to update artifact metadata."""
    
    name: Optional[str] = Field(None, description="New name")
    tags: Optional[list[str]] = Field(None, description="Updated tags")
    groups: Optional[list[str]] = Field(None, description="Updated groups")
    description: Optional[str] = Field(None, description="Updated description")
    is_shared: Optional[bool] = Field(None, description="Share status")


class ArtifactTagRequest(BaseModel):
    """Request to add/remove tags."""
    
    add_tags: list[str] = Field(default_factory=list, description="Tags to add")
    remove_tags: list[str] = Field(default_factory=list, description="Tags to remove")


class ArtifactGroupRequest(BaseModel):
    """Request to add/remove from groups."""
    
    add_groups: list[str] = Field(default_factory=list, description="Groups to add")
    remove_groups: list[str] = Field(default_factory=list, description="Groups to remove")


class ArtifactsListResponse(BaseModel):
    """Response containing list of artifacts."""
    
    artifacts: list[ArtifactMetadata]
    total: int


class GroupInfo(BaseModel):
    """Information about an artifact group."""
    
    name: str
    artifact_count: int
    total_size: int


class TagInfo(BaseModel):
    """Information about a tag."""
    
    name: str
    artifact_count: int


# === Storage Manager ===


class ArtifactStorage:
    """Manages artifact storage and metadata."""
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        self.config = config or AgenticConfig()
        self.base_path = Path(self.config.data_dir) / "artifacts"
        self.shared_path = self.base_path / "shared"
        self.metadata_file = self.base_path / "metadata.json"
        
        # Ensure directories exist
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.shared_path.mkdir(parents=True, exist_ok=True)
        
        # Load metadata
        self._metadata: dict[str, dict] = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """Load metadata from file."""
        import json
        
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    self._metadata = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load artifact metadata: {e}")
                self._metadata = {}
    
    def _save_metadata(self):
        """Save metadata to file."""
        import json
        
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self._metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save artifact metadata: {e}")
    
    def _get_storage_path(self, artifact_id: str, is_shared: bool = False) -> Path:
        """Get storage path for an artifact."""
        if is_shared:
            return self.shared_path / artifact_id
        return self.base_path / "user" / artifact_id
    
    def create(
        self,
        name: str,
        content: bytes,
        mime_type: Optional[str] = None,
        **kwargs
    ) -> ArtifactMetadata:
        """Create a new artifact."""
        artifact_id = str(uuid4())
        is_shared = kwargs.get("is_shared", False)
        
        storage_path = self._get_storage_path(artifact_id, is_shared)
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        with open(storage_path, "wb") as f:
            f.write(content)
        
        # Create metadata
        now = datetime.now()
        metadata = {
            "id": artifact_id,
            "name": name,
            "path": str(storage_path),
            "size": len(content),
            "mime_type": mime_type,
            "tags": kwargs.get("tags", []),
            "groups": kwargs.get("groups", []),
            "session_id": kwargs.get("session_id"),
            "experiment_id": kwargs.get("experiment_id"),
            "run_id": kwargs.get("run_id"),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "description": kwargs.get("description"),
            "is_shared": is_shared,
        }
        
        self._metadata[artifact_id] = metadata
        self._save_metadata()
        
        return ArtifactMetadata(**metadata)
    
    def get(self, artifact_id: str) -> Optional[ArtifactMetadata]:
        """Get artifact metadata by ID."""
        if artifact_id in self._metadata:
            return ArtifactMetadata(**self._metadata[artifact_id])
        return None
    
    def update(self, artifact_id: str, updates: dict) -> Optional[ArtifactMetadata]:
        """Update artifact metadata."""
        if artifact_id not in self._metadata:
            return None
        
        self._metadata[artifact_id].update(updates)
        self._metadata[artifact_id]["updated_at"] = datetime.now().isoformat()
        self._save_metadata()
        
        return ArtifactMetadata(**self._metadata[artifact_id])
    
    def delete(self, artifact_id: str) -> bool:
        """Delete an artifact."""
        if artifact_id not in self._metadata:
            return False
        
        # Remove file
        path = Path(self._metadata[artifact_id]["path"])
        if path.exists():
            path.unlink()
        
        # Remove metadata
        del self._metadata[artifact_id]
        self._save_metadata()
        
        return True
    
    def list_all(
        self,
        tags: Optional[list[str]] = None,
        groups: Optional[list[str]] = None,
        session_id: Optional[str] = None,
        experiment_id: Optional[str] = None,
        is_shared: Optional[bool] = None,
    ) -> list[ArtifactMetadata]:
        """List artifacts with optional filtering."""
        results = []
        
        for artifact_id, meta in self._metadata.items():
            # Apply filters
            if tags and not any(t in meta.get("tags", []) for t in tags):
                continue
            if groups and not any(g in meta.get("groups", []) for g in groups):
                continue
            if session_id and meta.get("session_id") != session_id:
                continue
            if experiment_id and meta.get("experiment_id") != experiment_id:
                continue
            if is_shared is not None and meta.get("is_shared") != is_shared:
                continue
            
            results.append(ArtifactMetadata(**meta))
        
        return results
    
    def get_content(self, artifact_id: str) -> Optional[bytes]:
        """Get artifact content."""
        if artifact_id not in self._metadata:
            return None
        
        path = Path(self._metadata[artifact_id]["path"])
        if path.exists():
            return path.read_bytes()
        return None
    
    def get_groups(self) -> list[GroupInfo]:
        """Get all groups with artifact counts."""
        group_counts: dict[str, dict] = {}
        
        for meta in self._metadata.values():
            for group in meta.get("groups", []):
                if group not in group_counts:
                    group_counts[group] = {"count": 0, "size": 0}
                group_counts[group]["count"] += 1
                group_counts[group]["size"] += meta.get("size", 0)
        
        return [
            GroupInfo(name=name, artifact_count=info["count"], total_size=info["size"])
            for name, info in group_counts.items()
        ]
    
    def get_tags(self) -> list[TagInfo]:
        """Get all tags with artifact counts."""
        tag_counts: dict[str, int] = {}
        
        for meta in self._metadata.values():
            for tag in meta.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return [
            TagInfo(name=name, artifact_count=count)
            for name, count in tag_counts.items()
        ]
    
    def copy_to_shared(self, artifact_id: str) -> Optional[ArtifactMetadata]:
        """Copy an artifact to shared storage."""
        if artifact_id not in self._metadata:
            return None
        
        meta = self._metadata[artifact_id]
        if meta.get("is_shared"):
            return ArtifactMetadata(**meta)
        
        # Copy file
        src_path = Path(meta["path"])
        dst_path = self.shared_path / artifact_id
        
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
        
        # Update metadata
        meta["is_shared"] = True
        meta["path"] = str(dst_path)
        meta["updated_at"] = datetime.now().isoformat()
        self._save_metadata()
        
        return ArtifactMetadata(**meta)


# Global storage instance
_storage: Optional[ArtifactStorage] = None


def get_storage() -> ArtifactStorage:
    """Get the artifact storage instance."""
    global _storage
    if _storage is None:
        _storage = ArtifactStorage()
    return _storage


# === Endpoints ===


@router.get("", response_model=ArtifactsListResponse)
async def list_artifacts(
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter"),
    groups: Optional[str] = Query(None, description="Comma-separated groups to filter"),
    session_id: Optional[str] = Query(None, description="Filter by session"),
    experiment_id: Optional[str] = Query(None, description="Filter by experiment"),
    shared_only: bool = Query(False, description="Only show shared artifacts"),
) -> ArtifactsListResponse:
    """List all artifacts with optional filtering."""
    logger.debug("Listing artifacts")
    
    storage = get_storage()
    
    tag_list = tags.split(",") if tags else None
    group_list = groups.split(",") if groups else None
    
    artifacts = storage.list_all(
        tags=tag_list,
        groups=group_list,
        session_id=session_id,
        experiment_id=experiment_id,
        is_shared=True if shared_only else None,
    )
    
    return ArtifactsListResponse(artifacts=artifacts, total=len(artifacts))


@router.post("", response_model=ArtifactMetadata)
async def upload_artifact(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    groups: Optional[str] = Query(None, description="Comma-separated groups"),
    description: Optional[str] = None,
    session_id: Optional[str] = None,
    experiment_id: Optional[str] = None,
    run_id: Optional[str] = None,
    is_shared: bool = False,
) -> ArtifactMetadata:
    """Upload a new artifact."""
    logger.info(f"Uploading artifact: {file.filename}")
    
    storage = get_storage()
    
    content = await file.read()
    artifact = storage.create(
        name=name or file.filename,
        content=content,
        mime_type=file.content_type,
        tags=tags.split(",") if tags else [],
        groups=groups.split(",") if groups else [],
        description=description,
        session_id=session_id,
        experiment_id=experiment_id,
        run_id=run_id,
        is_shared=is_shared,
    )
    
    return artifact


@router.get("/{artifact_id}", response_model=ArtifactMetadata)
async def get_artifact(artifact_id: str) -> ArtifactMetadata:
    """Get artifact metadata by ID."""
    logger.debug(f"Getting artifact: {artifact_id}")
    
    storage = get_storage()
    artifact = storage.get(artifact_id)
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return artifact


@router.get("/{artifact_id}/download")
async def download_artifact(artifact_id: str) -> FileResponse:
    """Download artifact content."""
    logger.debug(f"Downloading artifact: {artifact_id}")
    
    storage = get_storage()
    artifact = storage.get(artifact_id)
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    path = Path(artifact.path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact file not found")
    
    return FileResponse(
        path=path,
        filename=artifact.name,
        media_type=artifact.mime_type,
    )


@router.patch("/{artifact_id}", response_model=ArtifactMetadata)
async def update_artifact(artifact_id: str, request: ArtifactUpdate) -> ArtifactMetadata:
    """Update artifact metadata."""
    logger.info(f"Updating artifact: {artifact_id}")
    
    storage = get_storage()
    
    updates = request.model_dump(exclude_none=True)
    artifact = storage.update(artifact_id, updates)
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return artifact


@router.delete("/{artifact_id}")
async def delete_artifact(artifact_id: str) -> dict[str, str]:
    """Delete an artifact."""
    logger.info(f"Deleting artifact: {artifact_id}")
    
    storage = get_storage()
    
    if not storage.delete(artifact_id):
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return {"status": "deleted", "artifact_id": artifact_id}


@router.post("/{artifact_id}/tags", response_model=ArtifactMetadata)
async def update_artifact_tags(artifact_id: str, request: ArtifactTagRequest) -> ArtifactMetadata:
    """Add or remove tags from an artifact."""
    logger.info(f"Updating tags for artifact: {artifact_id}")
    
    storage = get_storage()
    artifact = storage.get(artifact_id)
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    current_tags = set(artifact.tags)
    current_tags.update(request.add_tags)
    current_tags -= set(request.remove_tags)
    
    updated = storage.update(artifact_id, {"tags": list(current_tags)})
    return updated


@router.post("/{artifact_id}/groups", response_model=ArtifactMetadata)
async def update_artifact_groups(artifact_id: str, request: ArtifactGroupRequest) -> ArtifactMetadata:
    """Add or remove groups from an artifact."""
    logger.info(f"Updating groups for artifact: {artifact_id}")
    
    storage = get_storage()
    artifact = storage.get(artifact_id)
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    current_groups = set(artifact.groups)
    current_groups.update(request.add_groups)
    current_groups -= set(request.remove_groups)
    
    updated = storage.update(artifact_id, {"groups": list(current_groups)})
    return updated


@router.post("/{artifact_id}/share", response_model=ArtifactMetadata)
async def share_artifact(artifact_id: str) -> ArtifactMetadata:
    """Copy an artifact to shared storage."""
    logger.info(f"Sharing artifact: {artifact_id}")
    
    storage = get_storage()
    artifact = storage.copy_to_shared(artifact_id)
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return artifact


@router.get("/groups/list", response_model=list[GroupInfo])
async def list_groups() -> list[GroupInfo]:
    """List all artifact groups."""
    logger.debug("Listing artifact groups")
    
    storage = get_storage()
    return storage.get_groups()


@router.get("/tags/list", response_model=list[TagInfo])
async def list_tags() -> list[TagInfo]:
    """List all artifact tags."""
    logger.debug("Listing artifact tags")
    
    storage = get_storage()
    return storage.get_tags()


@router.get("/shared/list", response_model=ArtifactsListResponse)
async def list_shared_artifacts() -> ArtifactsListResponse:
    """List all shared artifacts."""
    logger.debug("Listing shared artifacts")
    
    storage = get_storage()
    artifacts = storage.list_all(is_shared=True)
    
    return ArtifactsListResponse(artifacts=artifacts, total=len(artifacts))

