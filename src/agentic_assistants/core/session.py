"""
Session management for Agentic Assistants.

This module provides session persistence with SQLite for metadata
and Parquet for large data storage. Enhanced with artifact management,
tagging, grouping, and shared storage capabilities.

Example:
    >>> from agentic_assistants.core.session import SessionManager
    >>> 
    >>> session = SessionManager.get_or_create("default")
    >>> session.save_context("research_notes", context_data)
    >>> session.log_chat(messages, summary="User asked about X")
    >>> 
    >>> # Save an artifact with tags
    >>> session.save_artifact(
    ...     name="model_output",
    ...     data=output,
    ...     tags=["evaluation", "v1"],
    ...     group="experiments"
    ... )
"""

import json
import shutil
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Any, Optional, Union

import pyarrow as pa
import pyarrow.parquet as pq

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ChatEntry:
    """A single chat interaction entry."""
    
    id: str
    session_id: str
    messages: list[dict]
    summary: Optional[str] = None
    model: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    tokens_used: Optional[int] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ContextEntry:
    """A context data entry."""
    
    id: str
    session_id: str
    name: str
    data_type: str  # "inline", "parquet_ref"
    content: Optional[str] = None  # For inline data
    parquet_path: Optional[str] = None  # For large data
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)


@dataclass
class Artifact:
    """
    An artifact with metadata, tags, and grouping.
    
    Artifacts are stored files associated with sessions, supporting
    flexible organization via tags and groups.
    """
    
    id: str
    session_id: str
    name: str
    path: str
    artifact_type: str = "file"  # "file", "directory", "reference"
    tags: list[str] = field(default_factory=list)
    group: Optional[str] = None
    description: Optional[str] = None
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)
    is_shared: bool = False

    def to_dict(self) -> dict:
        """Convert artifact to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "name": self.name,
            "path": self.path,
            "artifact_type": self.artifact_type,
            "tags": self.tags,
            "group": self.group,
            "description": self.description,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "is_shared": self.is_shared,
        }


class Session:
    """
    Represents a single session with its data.
    
    A session provides methods for:
    - Storing and retrieving context data
    - Logging chat interactions
    - Managing artifacts with tagging and grouping
    - Persisting session state
    
    Attributes:
        id: Unique session identifier
        name: Human-readable session name
        manager: Parent SessionManager
    """

    def __init__(
        self,
        session_id: str,
        name: str,
        manager: "SessionManager",
        created_at: Optional[datetime] = None,
    ):
        """
        Initialize a session.
        
        Args:
            session_id: Unique session ID
            name: Session name
            manager: Parent SessionManager instance
            created_at: Creation timestamp
        """
        self.id = session_id
        self.name = name
        self.manager = manager
        self.created_at = created_at or datetime.utcnow()
        self._lock = RLock()

    def save_context(
        self,
        name: str,
        data: Any,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Save context data to the session.
        
        Small data is stored inline in SQLite; large data is stored
        in Parquet files with references in SQLite.
        
        Args:
            name: Name/key for the context
            data: Data to store
            metadata: Optional metadata
        
        Returns:
            Context entry ID
        """
        with self._lock:
            entry_id = str(uuid.uuid4())
            
            # Determine storage strategy
            if isinstance(data, (pa.Table, list)) and (
                isinstance(data, pa.Table) or len(data) > 100
            ):
                # Store as Parquet
                parquet_path = self.manager._get_parquet_path(self.id, entry_id)
                self._write_parquet(data, parquet_path)
                
                entry = ContextEntry(
                    id=entry_id,
                    session_id=self.id,
                    name=name,
                    data_type="parquet_ref",
                    parquet_path=str(parquet_path),
                    metadata=metadata or {},
                )
            else:
                # Store inline as JSON
                content = json.dumps(data) if not isinstance(data, str) else data
                entry = ContextEntry(
                    id=entry_id,
                    session_id=self.id,
                    name=name,
                    data_type="inline",
                    content=content,
                    metadata=metadata or {},
                )
            
            self.manager._save_context_entry(entry)
            logger.debug(f"Saved context '{name}' to session '{self.name}'")
            
            return entry_id

    def get_context(self, name: str) -> Optional[Any]:
        """
        Retrieve context data by name.
        
        Args:
            name: Context name/key
        
        Returns:
            Context data or None if not found
        """
        entry = self.manager._get_context_entry(self.id, name)
        if entry is None:
            return None
        
        if entry.data_type == "inline":
            try:
                return json.loads(entry.content)
            except (json.JSONDecodeError, TypeError):
                return entry.content
        elif entry.data_type == "parquet_ref":
            path = Path(entry.parquet_path)
            if path.exists():
                return pq.read_table(path)
            logger.warning(f"Parquet file not found: {path}")
            return None
        
        return None

    def list_contexts(self) -> list[dict]:
        """
        List all context entries in this session.
        
        Returns:
            List of context metadata dictionaries
        """
        return self.manager._list_context_entries(self.id)

    def delete_context(self, name: str) -> bool:
        """
        Delete a context entry.
        
        Args:
            name: Context name to delete
        
        Returns:
            True if deleted, False if not found
        """
        return self.manager._delete_context_entry(self.id, name)

    def log_chat(
        self,
        messages: list[dict],
        summary: Optional[str] = None,
        model: Optional[str] = None,
        tokens_used: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Log a chat interaction.
        
        Args:
            messages: List of message dictionaries
            summary: Optional summary of the interaction
            model: Model used for the chat
            tokens_used: Number of tokens used
            metadata: Additional metadata
        
        Returns:
            Chat entry ID
        """
        with self._lock:
            entry_id = str(uuid.uuid4())
            
            entry = ChatEntry(
                id=entry_id,
                session_id=self.id,
                messages=messages,
                summary=summary,
                model=model,
                tokens_used=tokens_used,
                metadata=metadata or {},
            )
            
            self.manager._save_chat_entry(entry)
            logger.debug(f"Logged chat to session '{self.name}'")
            
            return entry_id

    def save_artifact(
        self,
        name: str,
        data: Union[bytes, str, Path, Any],
        tags: Optional[list[str]] = None,
        group: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
        shared: bool = False,
    ) -> str:
        """
        Save an artifact to the session with tagging and grouping.
        
        Args:
            name: Artifact name
            data: Data to save (bytes, string, path, or serializable object)
            tags: List of tags for organization
            group: Group name for grouping related artifacts
            description: Human-readable description
            metadata: Additional metadata
            shared: If True, save to shared storage accessible by all sessions
        
        Returns:
            Artifact ID
        
        Example:
            >>> artifact_id = session.save_artifact(
            ...     name="model_results",
            ...     data=results_dict,
            ...     tags=["evaluation", "v1.0"],
            ...     group="experiments",
            ...     description="Evaluation results for model v1"
            ... )
        """
        with self._lock:
            artifact_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # Determine storage location
            if shared:
                base_dir = self.manager.shared_dir
            else:
                base_dir = self.manager.data_dir / self.id / "artifacts"
            
            # Create group subdirectory if specified
            if group:
                storage_dir = base_dir / group
            else:
                storage_dir = base_dir
            
            storage_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine file extension and write data
            if isinstance(data, bytes):
                file_path = storage_dir / f"{artifact_id}_{name}.bin"
                file_path.write_bytes(data)
                artifact_type = "file"
            elif isinstance(data, Path):
                if data.is_dir():
                    file_path = storage_dir / f"{artifact_id}_{name}"
                    shutil.copytree(data, file_path)
                    artifact_type = "directory"
                else:
                    file_path = storage_dir / f"{artifact_id}_{data.name}"
                    shutil.copy2(data, file_path)
                    artifact_type = "file"
            elif isinstance(data, str):
                file_path = storage_dir / f"{artifact_id}_{name}.txt"
                file_path.write_text(data)
                artifact_type = "file"
            else:
                # Serialize as JSON
                file_path = storage_dir / f"{artifact_id}_{name}.json"
                file_path.write_text(json.dumps(data, indent=2, default=str))
                artifact_type = "file"
            
            # Calculate size
            if file_path.is_file():
                size_bytes = file_path.stat().st_size
            else:
                size_bytes = sum(f.stat().st_size for f in file_path.rglob("*") if f.is_file())
            
            # Create artifact record
            artifact = Artifact(
                id=artifact_id,
                session_id=self.id,
                name=name,
                path=str(file_path),
                artifact_type=artifact_type,
                tags=tags or [],
                group=group,
                description=description,
                size_bytes=size_bytes,
                created_at=now,
                updated_at=now,
                metadata=metadata or {},
                is_shared=shared,
            )
            
            self.manager._save_artifact(artifact)
            logger.debug(f"Saved artifact '{name}' to session '{self.name}'")
            
            return artifact_id

    def add_artifact(
        self,
        name: str,
        path: str,
        tag: Optional[str] = None,
        group: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Add an existing file as an artifact reference.
        
        This is a legacy method - prefer save_artifact for new code.
        
        Args:
            name: Artifact name
            path: Path to the existing file
            tag: Single tag (for backwards compatibility)
            group: Group name
            metadata: Additional metadata
        
        Returns:
            Artifact ID
        """
        tags = [tag] if tag else []
        with self._lock:
            artifact_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            file_path = Path(path)
            size_bytes = file_path.stat().st_size if file_path.exists() else None
            
            artifact = Artifact(
                id=artifact_id,
                session_id=self.id,
                name=name,
                path=path,
                artifact_type="reference",
                tags=tags,
                group=group,
                size_bytes=size_bytes,
                created_at=now,
                updated_at=now,
                metadata=metadata or {},
            )
            
            self.manager._save_artifact(artifact)
            return artifact_id

    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """
        Get an artifact by ID.
        
        Args:
            artifact_id: Artifact ID
        
        Returns:
            Artifact or None if not found
        """
        return self.manager._get_artifact(artifact_id)

    def get_artifacts(
        self,
        tag: Optional[str] = None,
        tags: Optional[list[str]] = None,
        group: Optional[str] = None,
        include_shared: bool = True,
    ) -> list[Artifact]:
        """
        Get artifacts from the session, optionally filtered.
        
        Args:
            tag: Filter by single tag (for backwards compatibility)
            tags: Filter by multiple tags (all must match)
            group: Filter by group
            include_shared: Include shared artifacts
        
        Returns:
            List of matching artifacts
        """
        # Merge tag and tags
        all_tags = tags or []
        if tag and tag not in all_tags:
            all_tags.append(tag)
        
        return self.manager._get_artifacts(
            session_id=self.id,
            tags=all_tags or None,
            group=group,
            include_shared=include_shared,
        )

    def get_artifacts_by_group(self, group: str) -> list[Artifact]:
        """
        Get all artifacts in a group.
        
        Args:
            group: Group name
        
        Returns:
            List of artifacts in the group
        """
        return self.get_artifacts(group=group)

    def get_artifacts_by_tag(self, tag: str) -> list[Artifact]:
        """
        Get all artifacts with a specific tag.
        
        Args:
            tag: Tag to filter by
        
        Returns:
            List of artifacts with the tag
        """
        return self.get_artifacts(tags=[tag])

    def list_artifact_groups(self) -> list[str]:
        """
        List all artifact groups in this session.
        
        Returns:
            List of group names
        """
        return self.manager._list_artifact_groups(self.id)

    def list_artifact_tags(self) -> list[str]:
        """
        List all artifact tags used in this session.
        
        Returns:
            List of tag names
        """
        return self.manager._list_artifact_tags(self.id)

    def delete_artifact(self, artifact_id: str, delete_file: bool = True) -> bool:
        """
        Delete an artifact.
        
        Args:
            artifact_id: Artifact ID to delete
            delete_file: Whether to delete the associated file
        
        Returns:
            True if deleted, False if not found
        """
        return self.manager._delete_artifact(artifact_id, delete_file)

    def get_chat_history(
        self,
        limit: Optional[int] = None,
        include_messages: bool = False,
    ) -> list[dict]:
        """
        Get chat history for this session.
        
        Args:
            limit: Maximum number of entries to return
            include_messages: Whether to include full messages
        
        Returns:
            List of chat history entries
        """
        return self.manager._get_chat_history(
            self.id,
            limit=limit,
            include_messages=include_messages,
        )

    def _write_parquet(self, data: Any, path: Path) -> None:
        """Write data to a Parquet file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(data, pa.Table):
            table = data
        elif isinstance(data, list):
            table = pa.Table.from_pylist(data)
        elif isinstance(data, dict):
            table = pa.Table.from_pydict(data)
        else:
            raise TypeError(f"Cannot convert {type(data)} to Parquet")
        
        pq.write_table(table, path)

    def to_dict(self) -> dict:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"Session(id={self.id!r}, name={self.name!r})"


class SessionManager:
    """
    Manages session persistence with SQLite and Parquet.
    
    This class provides:
    - Session creation and retrieval
    - SQLite backend for metadata storage
    - Parquet file storage for large data
    - Artifact management with tagging and grouping
    - Shared artifact storage
    - Thread-safe operations
    
    Attributes:
        config: Agentic configuration
        db_path: Path to SQLite database
        data_dir: Directory for session data
        shared_dir: Directory for shared artifacts
    """

    _instances: dict[str, "SessionManager"] = {}
    _instance_lock = RLock()

    def __init__(self, config: Optional[AgenticConfig] = None):
        """
        Initialize the session manager.
        
        Args:
            config: Configuration instance
        """
        self.config = config or AgenticConfig()
        self.db_path = Path(self.config.session.database_path)
        
        # User-specific and shared storage
        self.user_dir = self.config.user.home_dir
        self.shared_dir = self.config.session_config.shared_artifact_dir
        
        self.data_dir = self.user_dir / "sessions"
        self._lock = RLock()
        self._sessions: dict[str, Session] = {}
        
        # Ensure directories exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.shared_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()

    @classmethod
    def get_instance(cls, config: Optional[AgenticConfig] = None) -> "SessionManager":
        """Get a singleton instance of SessionManager."""
        with cls._instance_lock:
            key = str(config.session.database_path) if config else "default"
            if key not in cls._instances:
                cls._instances[key] = cls(config)
            return cls._instances[key]

    def _init_database(self) -> None:
        """Initialize the SQLite database schema."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}'
                );
                
                CREATE TABLE IF NOT EXISTS context_entries (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    content TEXT,
                    parquet_path TEXT,
                    created_at TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (session_id) REFERENCES sessions(id),
                    UNIQUE(session_id, name)
                );
                
                CREATE TABLE IF NOT EXISTS chat_entries (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    messages TEXT NOT NULL,
                    summary TEXT,
                    model TEXT,
                    tokens_used INTEGER,
                    created_at TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_context_session 
                    ON context_entries(session_id);
                CREATE INDEX IF NOT EXISTS idx_chat_session 
                    ON chat_entries(session_id);
                CREATE INDEX IF NOT EXISTS idx_chat_created ON chat_entries(created_at);
                
                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    artifact_type TEXT DEFAULT 'file',
                    tags TEXT DEFAULT '[]',
                    artifact_group TEXT,
                    description TEXT,
                    size_bytes INTEGER,
                    checksum TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    is_shared INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_artifacts_session ON artifacts(session_id);
                CREATE INDEX IF NOT EXISTS idx_artifacts_group ON artifacts(artifact_group);
                CREATE INDEX IF NOT EXISTS idx_artifacts_shared ON artifacts(is_shared);
            """)

    @contextmanager
    def _get_connection(self):
        """Get a database connection as a context manager."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _get_parquet_path(self, session_id: str, entry_id: str) -> Path:
        """Get the Parquet file path for a context entry."""
        return self.data_dir / session_id / f"{entry_id}.parquet"

    def create_session(
        self,
        name: str,
        metadata: Optional[dict] = None,
    ) -> Session:
        """
        Create a new session.
        
        Args:
            name: Session name (must be unique)
            metadata: Optional metadata
        
        Returns:
            New Session instance
        
        Raises:
            ValueError: If session name already exists
        """
        with self._lock:
            session_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            with self._get_connection() as conn:
                try:
                    conn.execute(
                        """
                        INSERT INTO sessions (id, name, created_at, updated_at, metadata)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            session_id,
                            name,
                            now.isoformat(),
                            now.isoformat(),
                            json.dumps(metadata or {}),
                        ),
                    )
                except sqlite3.IntegrityError:
                    raise ValueError(f"Session '{name}' already exists")
            
            session = Session(session_id, name, self, created_at=now)
            self._sessions[session_id] = session
            
            logger.info(f"Created session: {name} ({session_id})")
            return session

    def get_session(self, name: str) -> Optional[Session]:
        """
        Get a session by name.
        
        Args:
            name: Session name
        
        Returns:
            Session instance or None if not found
        """
        with self._lock:
            # Check cache first
            for session in self._sessions.values():
                if session.name == name:
                    return session
            
            # Load from database
            with self._get_connection() as conn:
                row = conn.execute(
                    "SELECT id, name, created_at FROM sessions WHERE name = ?",
                    (name,),
                ).fetchone()
                
                if row is None:
                    return None
                
                session = Session(
                    session_id=row["id"],
                    name=row["name"],
                    manager=self,
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                self._sessions[row["id"]] = session
                return session

    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session ID
        
        Returns:
            Session instance or None if not found
        """
        with self._lock:
            # Check cache
            if session_id in self._sessions:
                return self._sessions[session_id]
            
            # Load from database
            with self._get_connection() as conn:
                row = conn.execute(
                    "SELECT id, name, created_at FROM sessions WHERE id = ?",
                    (session_id,),
                ).fetchone()
                
                if row is None:
                    return None
                
                session = Session(
                    session_id=row["id"],
                    name=row["name"],
                    manager=self,
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                self._sessions[session_id] = session
                return session

    @classmethod
    def get_or_create(
        cls,
        name: Optional[str] = None,
        config: Optional[AgenticConfig] = None,
    ) -> Session:
        """
        Get an existing session or create a new one.
        
        This is the recommended way to get a session.
        
        Args:
            name: Session name (uses default from config if None)
            config: Configuration instance
        
        Returns:
            Session instance
        """
        manager = cls.get_instance(config)
        config = config or AgenticConfig()
        session_name = name or config.session.default_session_name
        
        session = manager.get_session(session_name)
        if session is None:
            session = manager.create_session(session_name)
        
        return session

    def list_sessions(self) -> list[dict]:
        """
        List all sessions.
        
        Returns:
            List of session metadata dictionaries
        """
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT id, name, created_at, updated_at FROM sessions ORDER BY updated_at DESC"
            ).fetchall()
            
            return [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
                for row in rows
            ]

    def delete_session(self, name: str) -> bool:
        """
        Delete a session and all its data.
        
        Args:
            name: Session name
        
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            session = self.get_session(name)
            if session is None:
                return False
            
            # Delete session data directory
            session_dir = self.data_dir / session.id
            if session_dir.exists():
                shutil.rmtree(session_dir)
            
            # Delete database records
            with self._get_connection() as conn:
                conn.execute(
                    "DELETE FROM chat_entries WHERE session_id = ?",
                    (session.id,),
                )
                conn.execute(
                    "DELETE FROM context_entries WHERE session_id = ?",
                    (session.id,),
                )
                conn.execute(
                    "DELETE FROM artifacts WHERE session_id = ?",
                    (session.id,),
                )
                conn.execute(
                    "DELETE FROM sessions WHERE id = ?",
                    (session.id,),
                )
            
            # Remove from cache
            self._sessions.pop(session.id, None)
            
            logger.info(f"Deleted session: {name}")
            return True

    def get_shared_artifacts(
        self,
        tags: Optional[list[str]] = None,
        group: Optional[str] = None,
    ) -> list[Artifact]:
        """
        Get shared artifacts accessible by all sessions.
        
        Args:
            tags: Filter by tags
            group: Filter by group
        
        Returns:
            List of shared artifacts
        """
        return self._get_artifacts(
            session_id=None,
            tags=tags,
            group=group,
            include_shared=True,
            shared_only=True,
        )

    # === Internal methods for Session class ===

    def _save_context_entry(self, entry: ContextEntry) -> None:
        """Save a context entry to the database."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO context_entries 
                (id, session_id, name, data_type, content, parquet_path, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.id,
                    entry.session_id,
                    entry.name,
                    entry.data_type,
                    entry.content,
                    entry.parquet_path,
                    entry.created_at.isoformat(),
                    json.dumps(entry.metadata),
                ),
            )
            conn.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), entry.session_id),
            )

    def _get_context_entry(self, session_id: str, name: str) -> Optional[ContextEntry]:
        """Get a context entry by session ID and name."""
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT id, session_id, name, data_type, content, parquet_path, 
                       created_at, metadata
                FROM context_entries
                WHERE session_id = ? AND name = ?
                """,
                (session_id, name),
            ).fetchone()
            
            if row is None:
                return None
            
            return ContextEntry(
                id=row["id"],
                session_id=row["session_id"],
                name=row["name"],
                data_type=row["data_type"],
                content=row["content"],
                parquet_path=row["parquet_path"],
                created_at=datetime.fromisoformat(row["created_at"]),
                metadata=json.loads(row["metadata"]),
            )

    def _list_context_entries(self, session_id: str) -> list[dict]:
        """List all context entries for a session."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, name, data_type, created_at, metadata
                FROM context_entries
                WHERE session_id = ?
                ORDER BY created_at DESC
                """,
                (session_id,),
            ).fetchall()
            
            return [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "data_type": row["data_type"],
                    "created_at": row["created_at"],
                    "metadata": json.loads(row["metadata"]),
                }
                for row in rows
            ]

    def _delete_context_entry(self, session_id: str, name: str) -> bool:
        """Delete a context entry."""
        entry = self._get_context_entry(session_id, name)
        if entry is None:
            return False
        
        # Delete Parquet file if exists
        if entry.parquet_path:
            path = Path(entry.parquet_path)
            if path.exists():
                path.unlink()
        
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM context_entries WHERE session_id = ? AND name = ?",
                (session_id, name),
            )
        
        return True

    def _save_chat_entry(self, entry: ChatEntry) -> None:
        """Save a chat entry to the database."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO chat_entries 
                (id, session_id, messages, summary, model, tokens_used, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.id,
                    entry.session_id,
                    json.dumps(entry.messages),
                    entry.summary,
                    entry.model,
                    entry.tokens_used,
                    entry.created_at.isoformat(),
                    json.dumps(entry.metadata),
                ),
            )
            conn.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), entry.session_id),
            )

    def _get_chat_history(
        self,
        session_id: str,
        limit: Optional[int] = None,
        include_messages: bool = False,
    ) -> list[dict]:
        """Get chat history for a session."""
        with self._get_connection() as conn:
            query = """
                SELECT id, messages, summary, model, tokens_used, created_at, metadata
                FROM chat_entries
                WHERE session_id = ?
                ORDER BY created_at DESC
            """
            if limit:
                query += f" LIMIT {limit}"
            
            rows = conn.execute(query, (session_id,)).fetchall()
            
            result = []
            for row in rows:
                entry = {
                    "id": row["id"],
                    "summary": row["summary"],
                    "model": row["model"],
                    "tokens_used": row["tokens_used"],
                    "created_at": row["created_at"],
                    "metadata": json.loads(row["metadata"]),
                }
                if include_messages:
                    entry["messages"] = json.loads(row["messages"])
                result.append(entry)
            
            return result

    def _save_artifact(self, artifact: Artifact) -> None:
        """Save an artifact to the database."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO artifacts 
                (id, session_id, name, path, artifact_type, tags, artifact_group,
                 description, size_bytes, checksum, created_at, updated_at, metadata, is_shared)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact.id,
                    artifact.session_id,
                    artifact.name,
                    artifact.path,
                    artifact.artifact_type,
                    json.dumps(artifact.tags),
                    artifact.group,
                    artifact.description,
                    artifact.size_bytes,
                    artifact.checksum,
                    artifact.created_at.isoformat(),
                    artifact.updated_at.isoformat(),
                    json.dumps(artifact.metadata),
                    1 if artifact.is_shared else 0,
                ),
            )

    def _get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """Get an artifact by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM artifacts WHERE id = ?",
                (artifact_id,),
            ).fetchone()
            
            if row is None:
                return None
            
            return self._row_to_artifact(row)

    def _get_artifacts(
        self,
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        group: Optional[str] = None,
        include_shared: bool = True,
        shared_only: bool = False,
    ) -> list[Artifact]:
        """Get artifacts with filtering."""
        with self._get_connection() as conn:
            conditions = []
            params = []
            
            if shared_only:
                conditions.append("is_shared = 1")
            elif session_id:
                if include_shared:
                    conditions.append("(session_id = ? OR is_shared = 1)")
                else:
                    conditions.append("session_id = ?")
                params.append(session_id)
            
            if group:
                conditions.append("artifact_group = ?")
                params.append(group)
            
            query = "SELECT * FROM artifacts"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY created_at DESC"
            
            rows = conn.execute(query, params).fetchall()
            
            artifacts = [self._row_to_artifact(row) for row in rows]
            
            # Filter by tags if specified
            if tags:
                artifacts = [
                    a for a in artifacts
                    if all(tag in a.tags for tag in tags)
                ]
            
            return artifacts

    def _row_to_artifact(self, row) -> Artifact:
        """Convert a database row to an Artifact."""
        return Artifact(
            id=row["id"],
            session_id=row["session_id"],
            name=row["name"],
            path=row["path"],
            artifact_type=row["artifact_type"],
            tags=json.loads(row["tags"]),
            group=row["artifact_group"],
            description=row["description"],
            size_bytes=row["size_bytes"],
            checksum=row["checksum"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            metadata=json.loads(row["metadata"]),
            is_shared=bool(row["is_shared"]),
        )

    def _list_artifact_groups(self, session_id: str) -> list[str]:
        """List all artifact groups for a session."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT DISTINCT artifact_group
                FROM artifacts
                WHERE session_id = ? AND artifact_group IS NOT NULL
                """,
                (session_id,),
            ).fetchall()
            
            return [row["artifact_group"] for row in rows]

    def _list_artifact_tags(self, session_id: str) -> list[str]:
        """List all artifact tags for a session."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT tags FROM artifacts WHERE session_id = ?",
                (session_id,),
            ).fetchall()
            
            all_tags = set()
            for row in rows:
                tags = json.loads(row["tags"])
                all_tags.update(tags)
            
            return sorted(all_tags)

    def _delete_artifact(self, artifact_id: str, delete_file: bool = True) -> bool:
        """Delete an artifact."""
        artifact = self._get_artifact(artifact_id)
        if artifact is None:
            return False
        
        # Delete file if requested
        if delete_file and artifact.artifact_type != "reference":
            path = Path(artifact.path)
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM artifacts WHERE id = ?",
                (artifact_id,),
            )
        
        return True
