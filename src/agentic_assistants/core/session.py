"""
Session management for Agentic Assistants.

This module provides session persistence with SQLite for metadata
and Parquet for large data storage.

Example:
    >>> from agentic_assistants.core.session import SessionManager
    >>> 
    >>> session = SessionManager.get_or_create("default")
    >>> session.save_context("research_notes", context_data)
    >>> session.log_chat(messages, summary="User asked about X")
"""

import json
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Any, Optional

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


class Session:
    """
    Represents a single session with its data.
    
    A session provides methods for:
    - Storing and retrieving context data
    - Logging chat interactions
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

    def add_artifact(
        self,
        name: str,
        path: str,
        tag: Optional[str] = None,
        group: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """Add an artifact to the session."""
        with self._lock:
            artifact_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            with self.manager._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO artifacts (id, session_id, name, path, tag, artifact_group, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        artifact_id,
                        self.id,
                        name,
                        path,
                        tag,
                        group,
                        now.isoformat(),
                        json.dumps(metadata or {}),
                    ),
                )
            
            return artifact_id

    def get_artifacts(self, tag: Optional[str] = None, group: Optional[str] = None) -> list[dict]:
        """Get artifacts from the session, optionally filtered by tag or group."""
        with self.manager._get_connection() as conn:
            query = "SELECT * FROM artifacts WHERE session_id = ?"
            params = [self.id]
            if tag:
                query += " AND tag = ?"
                params.append(tag)
            if group:
                query += " AND artifact_group = ?"
                params.append(group)
            
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

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
    - Thread-safe operations
    
    Attributes:
        config: Agentic configuration
        db_path: Path to SQLite database
        data_dir: Directory for Parquet files
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
                    tag TEXT,
                    artifact_group TEXT,
                    created_at TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_artifacts_session ON artifacts(session_id);
                CREATE INDEX IF NOT EXISTS idx_artifacts_tag ON artifacts(tag);
                CREATE INDEX IF NOT EXISTS idx_artifacts_group ON artifacts(artifact_group);
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
            
            # Delete Parquet files
            session_dir = self.data_dir / session.id
            if session_dir.exists():
                import shutil
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
                    "DELETE FROM sessions WHERE id = ?",
                    (session.id,),
                )
            
            # Remove from cache
            self._sessions.pop(session.id, None)
            
            logger.info(f"Deleted session: {name}")
            return True

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

