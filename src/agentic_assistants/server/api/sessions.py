"""
Session Management API Router.

This module provides REST endpoints for session management:
- Session lifecycle (create, get, delete)
- Session persistence and state management
- Memory configuration
- Interaction logging
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


# === Request/Response Models ===


class SessionCreate(BaseModel):
    """Request to create a new session."""
    
    name: str = Field(..., description="Session name")
    description: Optional[str] = Field(None, description="Session description")
    memory_limit_mb: int = Field(1024, description="Memory limit in MB")
    persist_interactions: bool = Field(True, description="Whether to persist interactions")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata")


class SessionUpdate(BaseModel):
    """Request to update a session."""
    
    name: Optional[str] = Field(None, description="New session name")
    description: Optional[str] = Field(None, description="New description")
    memory_limit_mb: Optional[int] = Field(None, description="New memory limit")
    persist_interactions: Optional[bool] = Field(None, description="Persistence setting")
    metadata: Optional[dict[str, Any]] = Field(None, description="Updated metadata")


class SessionConfig(BaseModel):
    """Session configuration settings."""
    
    memory_limit_mb: int = Field(1024, description="Memory limit in MB")
    persist_interactions: bool = Field(True, description="Whether to persist interactions")
    artifact_path: Optional[str] = Field(None, description="Artifact storage path")
    active_experiment_id: Optional[str] = Field(None, description="Active experiment")


class InteractionLog(BaseModel):
    """A single interaction log entry."""
    
    id: str = Field(..., description="Interaction ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")
    interaction_type: str = Field(..., description="Type: chat, search, index, etc.")
    input_data: dict[str, Any] = Field(default_factory=dict, description="Input data")
    output_data: dict[str, Any] = Field(default_factory=dict, description="Output data")
    duration_ms: Optional[int] = Field(None, description="Duration in milliseconds")
    status: str = Field("success", description="Status: success, error")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    model: Optional[str] = Field(None, description="Model used")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SessionResponse(BaseModel):
    """Response containing session details."""
    
    id: str = Field(..., description="Session ID")
    name: str = Field(..., description="Session name")
    description: Optional[str] = Field(None, description="Description")
    user_id: str = Field("default_user", description="User ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update")
    config: SessionConfig = Field(default_factory=SessionConfig, description="Configuration")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    interaction_count: int = Field(0, description="Number of interactions")
    artifact_count: int = Field(0, description="Number of artifacts")
    is_active: bool = Field(False, description="Whether this is the active session")


class SessionsListResponse(BaseModel):
    """Response containing list of sessions."""
    
    sessions: list[SessionResponse]
    active_session_id: Optional[str] = None
    total: int


class InteractionsListResponse(BaseModel):
    """Response containing list of interactions."""
    
    interactions: list[InteractionLog]
    total: int
    session_id: str


class ContextEntry(BaseModel):
    """A context entry stored in the session."""
    
    id: str
    name: str
    data_type: str
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


# === Session Storage ===


class SessionStorage:
    """Manages session storage and state."""
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        self.config = config or AgenticConfig()
        self.base_path = Path(self.config.data_dir) / "sessions"
        self.metadata_file = self.base_path / "sessions.json"
        
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self._sessions: dict[str, dict] = {}
        self._active_session_id: Optional[str] = None
        self._load_sessions()
    
    def _load_sessions(self):
        """Load sessions from file."""
        import json
        
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    data = json.load(f)
                    self._sessions = data.get("sessions", {})
                    self._active_session_id = data.get("active_session_id")
            except Exception as e:
                logger.error(f"Failed to load sessions: {e}")
    
    def _save_sessions(self):
        """Save sessions to file."""
        import json
        
        try:
            with open(self.metadata_file, "w") as f:
                json.dump({
                    "sessions": self._sessions,
                    "active_session_id": self._active_session_id,
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
    
    def _get_session_dir(self, session_id: str) -> Path:
        """Get directory for a session."""
        return self.base_path / session_id
    
    def _get_interactions_file(self, session_id: str) -> Path:
        """Get interactions log file for a session."""
        return self._get_session_dir(session_id) / "interactions.jsonl"
    
    def create(self, request: SessionCreate) -> SessionResponse:
        """Create a new session."""
        session_id = str(uuid4())
        now = datetime.now()
        
        session_dir = self._get_session_dir(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "artifacts").mkdir(exist_ok=True)
        (session_dir / "context").mkdir(exist_ok=True)
        
        session = {
            "id": session_id,
            "name": request.name,
            "description": request.description,
            "user_id": "default_user",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "config": {
                "memory_limit_mb": request.memory_limit_mb,
                "persist_interactions": request.persist_interactions,
                "artifact_path": str(session_dir / "artifacts"),
            },
            "metadata": request.metadata,
            "interaction_count": 0,
            "artifact_count": 0,
        }
        
        self._sessions[session_id] = session
        self._save_sessions()
        
        return self._to_response(session)
    
    def get(self, session_id: str) -> Optional[SessionResponse]:
        """Get a session by ID."""
        if session_id not in self._sessions:
            return None
        return self._to_response(self._sessions[session_id])
    
    def get_by_name(self, name: str) -> Optional[SessionResponse]:
        """Get a session by name."""
        for session in self._sessions.values():
            if session["name"] == name:
                return self._to_response(session)
        return None
    
    def update(self, session_id: str, request: SessionUpdate) -> Optional[SessionResponse]:
        """Update a session."""
        if session_id not in self._sessions:
            return None
        
        session = self._sessions[session_id]
        
        if request.name is not None:
            session["name"] = request.name
        if request.description is not None:
            session["description"] = request.description
        if request.memory_limit_mb is not None:
            session["config"]["memory_limit_mb"] = request.memory_limit_mb
        if request.persist_interactions is not None:
            session["config"]["persist_interactions"] = request.persist_interactions
        if request.metadata is not None:
            session["metadata"].update(request.metadata)
        
        session["updated_at"] = datetime.now().isoformat()
        self._save_sessions()
        
        return self._to_response(session)
    
    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id not in self._sessions:
            return False
        
        # Remove directory
        import shutil
        session_dir = self._get_session_dir(session_id)
        if session_dir.exists():
            shutil.rmtree(session_dir)
        
        # Remove from metadata
        del self._sessions[session_id]
        if self._active_session_id == session_id:
            self._active_session_id = None
        self._save_sessions()
        
        return True
    
    def list_all(self) -> list[SessionResponse]:
        """List all sessions."""
        return [self._to_response(s) for s in self._sessions.values()]
    
    def set_active(self, session_id: str) -> Optional[SessionResponse]:
        """Set the active session."""
        if session_id not in self._sessions:
            return None
        
        self._active_session_id = session_id
        self._save_sessions()
        
        return self._to_response(self._sessions[session_id])
    
    def get_active(self) -> Optional[SessionResponse]:
        """Get the active session."""
        if self._active_session_id and self._active_session_id in self._sessions:
            return self._to_response(self._sessions[self._active_session_id])
        return None
    
    def log_interaction(self, session_id: str, interaction: InteractionLog) -> bool:
        """Log an interaction to a session."""
        if session_id not in self._sessions:
            return False
        
        session = self._sessions[session_id]
        if not session["config"].get("persist_interactions", True):
            return True
        
        import json
        
        interactions_file = self._get_interactions_file(session_id)
        interactions_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(interactions_file, "a") as f:
            f.write(json.dumps(interaction.model_dump(), default=str) + "\n")
        
        session["interaction_count"] = session.get("interaction_count", 0) + 1
        session["updated_at"] = datetime.now().isoformat()
        self._save_sessions()
        
        return True
    
    def get_interactions(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[InteractionLog]:
        """Get interactions for a session."""
        import json
        
        interactions_file = self._get_interactions_file(session_id)
        if not interactions_file.exists():
            return []
        
        interactions = []
        with open(interactions_file, "r") as f:
            for i, line in enumerate(f):
                if i < offset:
                    continue
                if len(interactions) >= limit:
                    break
                try:
                    data = json.loads(line.strip())
                    interactions.append(InteractionLog(**data))
                except Exception:
                    continue
        
        return interactions
    
    def save_context(
        self,
        session_id: str,
        name: str,
        data: Any,
        metadata: Optional[dict] = None,
    ) -> str:
        """Save context data to a session."""
        import json
        
        if session_id not in self._sessions:
            raise ValueError("Session not found")
        
        context_dir = self._get_session_dir(session_id) / "context"
        context_dir.mkdir(parents=True, exist_ok=True)
        
        context_id = str(uuid4())
        context_file = context_dir / f"{context_id}.json"
        
        with open(context_file, "w") as f:
            json.dump({
                "id": context_id,
                "name": name,
                "data": data,
                "data_type": type(data).__name__,
                "created_at": datetime.now().isoformat(),
                "metadata": metadata or {},
            }, f, indent=2, default=str)
        
        return context_id
    
    def get_context(self, session_id: str, context_id: str) -> Optional[dict]:
        """Get context data from a session."""
        import json
        
        context_file = self._get_session_dir(session_id) / "context" / f"{context_id}.json"
        if not context_file.exists():
            return None
        
        with open(context_file, "r") as f:
            return json.load(f)
    
    def list_contexts(self, session_id: str) -> list[ContextEntry]:
        """List all context entries for a session."""
        import json
        
        context_dir = self._get_session_dir(session_id) / "context"
        if not context_dir.exists():
            return []
        
        contexts = []
        for context_file in context_dir.glob("*.json"):
            try:
                with open(context_file, "r") as f:
                    data = json.load(f)
                    contexts.append(ContextEntry(
                        id=data["id"],
                        name=data["name"],
                        data_type=data["data_type"],
                        created_at=datetime.fromisoformat(data["created_at"]),
                        metadata=data.get("metadata", {}),
                    ))
            except Exception:
                continue
        
        return contexts
    
    def _to_response(self, session: dict) -> SessionResponse:
        """Convert session dict to response model."""
        return SessionResponse(
            id=session["id"],
            name=session["name"],
            description=session.get("description"),
            user_id=session.get("user_id", "default_user"),
            created_at=datetime.fromisoformat(session["created_at"]),
            updated_at=datetime.fromisoformat(session["updated_at"]),
            config=SessionConfig(**session.get("config", {})),
            metadata=session.get("metadata", {}),
            interaction_count=session.get("interaction_count", 0),
            artifact_count=session.get("artifact_count", 0),
            is_active=session["id"] == self._active_session_id,
        )


# Global storage instance
_storage: Optional[SessionStorage] = None


def get_storage() -> SessionStorage:
    """Get the session storage instance."""
    global _storage
    if _storage is None:
        _storage = SessionStorage()
    return _storage


# === Endpoints ===


@router.get("", response_model=SessionsListResponse)
async def list_sessions() -> SessionsListResponse:
    """List all sessions."""
    logger.debug("Listing sessions")
    
    storage = get_storage()
    sessions = storage.list_all()
    
    return SessionsListResponse(
        sessions=sessions,
        active_session_id=storage._active_session_id,
        total=len(sessions),
    )


@router.post("", response_model=SessionResponse)
async def create_session(request: SessionCreate) -> SessionResponse:
    """Create a new session."""
    logger.info(f"Creating session: {request.name}")
    
    storage = get_storage()
    
    # Check if name already exists
    existing = storage.get_by_name(request.name)
    if existing:
        raise HTTPException(status_code=400, detail="Session with this name already exists")
    
    return storage.create(request)


@router.get("/active", response_model=Optional[SessionResponse])
async def get_active_session() -> Optional[SessionResponse]:
    """Get the currently active session."""
    logger.debug("Getting active session")
    
    storage = get_storage()
    return storage.get_active()


@router.post("/{session_id}/activate", response_model=SessionResponse)
async def activate_session(session_id: str) -> SessionResponse:
    """Set a session as the active session."""
    logger.info(f"Activating session: {session_id}")
    
    storage = get_storage()
    session = storage.set_active(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """Get session by ID."""
    logger.debug(f"Getting session: {session_id}")
    
    storage = get_storage()
    session = storage.get(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, request: SessionUpdate) -> SessionResponse:
    """Update a session."""
    logger.info(f"Updating session: {session_id}")
    
    storage = get_storage()
    session = storage.update(session_id, request)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.delete("/{session_id}")
async def delete_session(session_id: str) -> dict[str, str]:
    """Delete a session."""
    logger.info(f"Deleting session: {session_id}")
    
    storage = get_storage()
    
    if not storage.delete(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "deleted", "session_id": session_id}


@router.get("/{session_id}/config", response_model=SessionConfig)
async def get_session_config(session_id: str) -> SessionConfig:
    """Get session configuration."""
    logger.debug(f"Getting config for session: {session_id}")
    
    storage = get_storage()
    session = storage.get(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.config


@router.patch("/{session_id}/config", response_model=SessionConfig)
async def update_session_config(session_id: str, config: SessionConfig) -> SessionConfig:
    """Update session configuration."""
    logger.info(f"Updating config for session: {session_id}")
    
    storage = get_storage()
    
    session = storage.update(session_id, SessionUpdate(
        memory_limit_mb=config.memory_limit_mb,
        persist_interactions=config.persist_interactions,
    ))
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.config


@router.get("/{session_id}/interactions", response_model=InteractionsListResponse)
async def get_interactions(
    session_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> InteractionsListResponse:
    """Get interactions for a session."""
    logger.debug(f"Getting interactions for session: {session_id}")
    
    storage = get_storage()
    
    if not storage.get(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    interactions = storage.get_interactions(session_id, limit, offset)
    
    return InteractionsListResponse(
        interactions=interactions,
        total=len(interactions),
        session_id=session_id,
    )


@router.post("/{session_id}/interactions")
async def log_interaction(session_id: str, interaction: InteractionLog) -> dict[str, Any]:
    """Log an interaction to a session."""
    logger.debug(f"Logging interaction to session: {session_id}")
    
    storage = get_storage()
    
    if not storage.log_interaction(session_id, interaction):
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "logged", "interaction_id": interaction.id}


@router.get("/{session_id}/contexts", response_model=list[ContextEntry])
async def list_contexts(session_id: str) -> list[ContextEntry]:
    """List all context entries for a session."""
    logger.debug(f"Listing contexts for session: {session_id}")
    
    storage = get_storage()
    
    if not storage.get(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    return storage.list_contexts(session_id)


@router.post("/{session_id}/contexts")
async def save_context(
    session_id: str,
    name: str,
    data: dict[str, Any],
    metadata: Optional[dict[str, Any]] = None,
) -> dict[str, str]:
    """Save context data to a session."""
    logger.debug(f"Saving context to session: {session_id}")
    
    storage = get_storage()
    
    try:
        context_id = storage.save_context(session_id, name, data, metadata)
        return {"status": "saved", "context_id": context_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{session_id}/contexts/{context_id}")
async def get_context(session_id: str, context_id: str) -> dict[str, Any]:
    """Get context data from a session."""
    logger.debug(f"Getting context {context_id} from session: {session_id}")
    
    storage = get_storage()
    
    context = storage.get_context(session_id, context_id)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    
    return context

