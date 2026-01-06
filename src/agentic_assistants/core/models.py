"""
Data models for the Agentic Control Panel.

This module provides SQLite-backed data models for:
- Projects: Top-level resource collections
- Agents: AI agent definitions
- Flows: Multi-agent workflows
- Components: Reusable code snippets
- Notes: Free-form notes attached to resources
- Tags: Categorization and search support
"""

import json
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Any, List, Optional, Dict

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Project:
    """A top-level project container."""
    id: str
    name: str
    description: str = ""
    config_yaml: str = ""
    status: str = "active"  # active, archived, draft
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "config_yaml": self.config_yaml,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class Agent:
    """An AI agent definition."""
    id: str
    name: str
    role: str
    goal: str = ""
    backstory: str = ""
    tools: List[str] = field(default_factory=list)
    model: str = "llama3.2"
    status: str = "drafted"  # deployed, created, drafted, in_development
    project_id: Optional[str] = None
    config_yaml: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "tools": self.tools,
            "model": self.model,
            "status": self.status,
            "project_id": self.project_id,
            "config_yaml": self.config_yaml,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class Flow:
    """A multi-agent workflow definition."""
    id: str
    name: str
    description: str = ""
    flow_yaml: str = ""
    flow_type: str = "crew"  # crew, pipeline, workflow
    status: str = "draft"  # active, paused, draft, archived
    agents: List[str] = field(default_factory=list)  # Agent IDs
    project_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "flow_yaml": self.flow_yaml,
            "flow_type": self.flow_type,
            "status": self.status,
            "agents": self.agents,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class Component:
    """A reusable code component."""
    id: str
    name: str
    category: str  # tool, agent, task, pattern, utility, template
    code: str = ""
    language: str = "python"
    description: str = ""
    usage_example: str = ""
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "code": self.code,
            "language": self.language,
            "description": self.description,
            "usage_example": self.usage_example,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class Note:
    """A free-form note attached to a resource."""
    id: str
    resource_type: str  # project, agent, flow, component, experiment
    resource_id: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Tag:
    """A tag for categorization."""
    id: str
    name: str
    color: str = "#6366f1"  # Default indigo color
    resource_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "resource_count": self.resource_count,
        }


# ============================================================================
# Data Store
# ============================================================================

class ControlPanelStore:
    """
    SQLite-based data store for the Agentic Control Panel.
    
    Provides CRUD operations for all entity types.
    """
    
    _instance: Optional["ControlPanelStore"] = None
    _lock = RLock()
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """Initialize the data store."""
        self.config = config or AgenticConfig()
        self.db_path = Path(self.config.data_dir) / "control_panel.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    @classmethod
    def get_instance(cls, config: Optional[AgenticConfig] = None) -> "ControlPanelStore":
        """Get singleton instance of the data store."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(config)
            return cls._instance
    
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
    
    def _init_database(self) -> None:
        """Initialize the database schema."""
        with self._get_connection() as conn:
            conn.executescript("""
                -- Projects table
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    config_yaml TEXT DEFAULT '',
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
                CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
                
                -- Agents table
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    goal TEXT DEFAULT '',
                    backstory TEXT DEFAULT '',
                    tools TEXT DEFAULT '[]',
                    model TEXT DEFAULT 'llama3.2',
                    status TEXT DEFAULT 'drafted',
                    project_id TEXT,
                    config_yaml TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
                );
                CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
                CREATE INDEX IF NOT EXISTS idx_agents_project ON agents(project_id);
                
                -- Flows table
                CREATE TABLE IF NOT EXISTS flows (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    flow_yaml TEXT DEFAULT '',
                    flow_type TEXT DEFAULT 'crew',
                    status TEXT DEFAULT 'draft',
                    agents TEXT DEFAULT '[]',
                    project_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
                );
                CREATE INDEX IF NOT EXISTS idx_flows_status ON flows(status);
                CREATE INDEX IF NOT EXISTS idx_flows_project ON flows(project_id);
                
                -- Components table
                CREATE TABLE IF NOT EXISTS components (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    code TEXT DEFAULT '',
                    language TEXT DEFAULT 'python',
                    description TEXT DEFAULT '',
                    usage_example TEXT DEFAULT '',
                    version TEXT DEFAULT '1.0.0',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_components_category ON components(category);
                
                -- Notes table
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_notes_resource ON notes(resource_type, resource_id);
                
                -- Tags table
                CREATE TABLE IF NOT EXISTS tags (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT DEFAULT '#6366f1'
                );
                
                -- Resource-Tag mapping table
                CREATE TABLE IF NOT EXISTS resource_tags (
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    tag_id TEXT NOT NULL,
                    PRIMARY KEY (resource_type, resource_id, tag_id),
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_resource_tags_tag ON resource_tags(tag_id);
            """)
        logger.info(f"Database initialized at {self.db_path}")
    
    # =========================================================================
    # Projects CRUD
    # =========================================================================
    
    def create_project(self, name: str, description: str = "", 
                      config_yaml: str = "", status: str = "active",
                      tags: List[str] = None, metadata: Dict = None) -> Project:
        """Create a new project."""
        project = Project(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            config_yaml=config_yaml,
            status=status,
            tags=tags or [],
            metadata=metadata or {},
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO projects (id, name, description, config_yaml, status, 
                                     created_at, updated_at, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project.id, project.name, project.description, project.config_yaml,
                project.status, project.created_at.isoformat(), 
                project.updated_at.isoformat(), json.dumps(project.tags),
                json.dumps(project.metadata),
            ))
        
        logger.info(f"Created project: {name} ({project.id})")
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
            
            if row is None:
                return None
            
            return self._row_to_project(row)
    
    def list_projects(self, status: Optional[str] = None, 
                     page: int = 1, limit: int = 50) -> tuple[List[Project], int]:
        """List projects with optional filtering."""
        offset = (page - 1) * limit
        
        with self._get_connection() as conn:
            # Count total
            if status:
                total = conn.execute(
                    "SELECT COUNT(*) FROM projects WHERE status = ?", (status,)
                ).fetchone()[0]
                rows = conn.execute(
                    "SELECT * FROM projects WHERE status = ? ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                    (status, limit, offset)
                ).fetchall()
            else:
                total = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
                rows = conn.execute(
                    "SELECT * FROM projects ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                    (limit, offset)
                ).fetchall()
            
            return [self._row_to_project(row) for row in rows], total
    
    def update_project(self, project_id: str, **kwargs) -> Optional[Project]:
        """Update a project."""
        project = self.get_project(project_id)
        if project is None:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        project.updated_at = datetime.utcnow()
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE projects SET name = ?, description = ?, config_yaml = ?,
                       status = ?, updated_at = ?, tags = ?, metadata = ?
                WHERE id = ?
            """, (
                project.name, project.description, project.config_yaml,
                project.status, project.updated_at.isoformat(),
                json.dumps(project.tags), json.dumps(project.metadata),
                project.id,
            ))
        
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        with self._get_connection() as conn:
            result = conn.execute(
                "DELETE FROM projects WHERE id = ?", (project_id,)
            )
            return result.rowcount > 0
    
    def _row_to_project(self, row) -> Project:
        """Convert a database row to a Project."""
        return Project(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            config_yaml=row["config_yaml"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
        )
    
    # =========================================================================
    # Agents CRUD
    # =========================================================================
    
    def create_agent(self, name: str, role: str, **kwargs) -> Agent:
        """Create a new agent."""
        agent = Agent(
            id=str(uuid.uuid4()),
            name=name,
            role=role,
            goal=kwargs.get("goal", ""),
            backstory=kwargs.get("backstory", ""),
            tools=kwargs.get("tools", []),
            model=kwargs.get("model", "llama3.2"),
            status=kwargs.get("status", "drafted"),
            project_id=kwargs.get("project_id"),
            config_yaml=kwargs.get("config_yaml", ""),
            tags=kwargs.get("tags", []),
            metadata=kwargs.get("metadata", {}),
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO agents (id, name, role, goal, backstory, tools, model,
                                   status, project_id, config_yaml, created_at, 
                                   updated_at, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent.id, agent.name, agent.role, agent.goal, agent.backstory,
                json.dumps(agent.tools), agent.model, agent.status, agent.project_id,
                agent.config_yaml, agent.created_at.isoformat(),
                agent.updated_at.isoformat(), json.dumps(agent.tags),
                json.dumps(agent.metadata),
            ))
        
        logger.info(f"Created agent: {name} ({agent.id})")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM agents WHERE id = ?", (agent_id,)
            ).fetchone()
            
            if row is None:
                return None
            
            return self._row_to_agent(row)
    
    def list_agents(self, project_id: Optional[str] = None,
                   status: Optional[str] = None,
                   page: int = 1, limit: int = 50) -> tuple[List[Agent], int]:
        """List agents with optional filtering."""
        offset = (page - 1) * limit
        conditions = []
        params = []
        
        if project_id:
            conditions.append("project_id = ?")
            params.append(project_id)
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self._get_connection() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM agents WHERE {where_clause}", params
            ).fetchone()[0]
            
            rows = conn.execute(
                f"SELECT * FROM agents WHERE {where_clause} ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                params + [limit, offset]
            ).fetchall()
            
            return [self._row_to_agent(row) for row in rows], total
    
    def update_agent(self, agent_id: str, **kwargs) -> Optional[Agent]:
        """Update an agent."""
        agent = self.get_agent(agent_id)
        if agent is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(agent, key):
                setattr(agent, key, value)
        agent.updated_at = datetime.utcnow()
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE agents SET name = ?, role = ?, goal = ?, backstory = ?,
                       tools = ?, model = ?, status = ?, project_id = ?,
                       config_yaml = ?, updated_at = ?, tags = ?, metadata = ?
                WHERE id = ?
            """, (
                agent.name, agent.role, agent.goal, agent.backstory,
                json.dumps(agent.tools), agent.model, agent.status, agent.project_id,
                agent.config_yaml, agent.updated_at.isoformat(),
                json.dumps(agent.tags), json.dumps(agent.metadata), agent.id,
            ))
        
        return agent
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        with self._get_connection() as conn:
            result = conn.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
            return result.rowcount > 0
    
    def _row_to_agent(self, row) -> Agent:
        """Convert a database row to an Agent."""
        return Agent(
            id=row["id"],
            name=row["name"],
            role=row["role"],
            goal=row["goal"],
            backstory=row["backstory"],
            tools=json.loads(row["tools"]),
            model=row["model"],
            status=row["status"],
            project_id=row["project_id"],
            config_yaml=row["config_yaml"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
        )
    
    # =========================================================================
    # Flows CRUD
    # =========================================================================
    
    def create_flow(self, name: str, **kwargs) -> Flow:
        """Create a new flow."""
        flow = Flow(
            id=str(uuid.uuid4()),
            name=name,
            description=kwargs.get("description", ""),
            flow_yaml=kwargs.get("flow_yaml", ""),
            flow_type=kwargs.get("flow_type", "crew"),
            status=kwargs.get("status", "draft"),
            agents=kwargs.get("agents", []),
            project_id=kwargs.get("project_id"),
            tags=kwargs.get("tags", []),
            metadata=kwargs.get("metadata", {}),
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO flows (id, name, description, flow_yaml, flow_type,
                                  status, agents, project_id, created_at,
                                  updated_at, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                flow.id, flow.name, flow.description, flow.flow_yaml,
                flow.flow_type, flow.status, json.dumps(flow.agents),
                flow.project_id, flow.created_at.isoformat(),
                flow.updated_at.isoformat(), json.dumps(flow.tags),
                json.dumps(flow.metadata),
            ))
        
        logger.info(f"Created flow: {name} ({flow.id})")
        return flow
    
    def get_flow(self, flow_id: str) -> Optional[Flow]:
        """Get a flow by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM flows WHERE id = ?", (flow_id,)
            ).fetchone()
            
            if row is None:
                return None
            
            return self._row_to_flow(row)
    
    def list_flows(self, project_id: Optional[str] = None,
                  status: Optional[str] = None,
                  page: int = 1, limit: int = 50) -> tuple[List[Flow], int]:
        """List flows with optional filtering."""
        offset = (page - 1) * limit
        conditions = []
        params = []
        
        if project_id:
            conditions.append("project_id = ?")
            params.append(project_id)
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self._get_connection() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM flows WHERE {where_clause}", params
            ).fetchone()[0]
            
            rows = conn.execute(
                f"SELECT * FROM flows WHERE {where_clause} ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                params + [limit, offset]
            ).fetchall()
            
            return [self._row_to_flow(row) for row in rows], total
    
    def update_flow(self, flow_id: str, **kwargs) -> Optional[Flow]:
        """Update a flow."""
        flow = self.get_flow(flow_id)
        if flow is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(flow, key):
                setattr(flow, key, value)
        flow.updated_at = datetime.utcnow()
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE flows SET name = ?, description = ?, flow_yaml = ?,
                       flow_type = ?, status = ?, agents = ?, project_id = ?,
                       updated_at = ?, tags = ?, metadata = ?
                WHERE id = ?
            """, (
                flow.name, flow.description, flow.flow_yaml, flow.flow_type,
                flow.status, json.dumps(flow.agents), flow.project_id,
                flow.updated_at.isoformat(), json.dumps(flow.tags),
                json.dumps(flow.metadata), flow.id,
            ))
        
        return flow
    
    def delete_flow(self, flow_id: str) -> bool:
        """Delete a flow."""
        with self._get_connection() as conn:
            result = conn.execute("DELETE FROM flows WHERE id = ?", (flow_id,))
            return result.rowcount > 0
    
    def _row_to_flow(self, row) -> Flow:
        """Convert a database row to a Flow."""
        return Flow(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            flow_yaml=row["flow_yaml"],
            flow_type=row["flow_type"],
            status=row["status"],
            agents=json.loads(row["agents"]),
            project_id=row["project_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
        )
    
    # =========================================================================
    # Components CRUD
    # =========================================================================
    
    def create_component(self, name: str, category: str, **kwargs) -> Component:
        """Create a new component."""
        component = Component(
            id=str(uuid.uuid4()),
            name=name,
            category=category,
            code=kwargs.get("code", ""),
            language=kwargs.get("language", "python"),
            description=kwargs.get("description", ""),
            usage_example=kwargs.get("usage_example", ""),
            version=kwargs.get("version", "1.0.0"),
            tags=kwargs.get("tags", []),
            metadata=kwargs.get("metadata", {}),
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO components (id, name, category, code, language,
                                       description, usage_example, version,
                                       created_at, updated_at, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                component.id, component.name, component.category, component.code,
                component.language, component.description, component.usage_example,
                component.version, component.created_at.isoformat(),
                component.updated_at.isoformat(), json.dumps(component.tags),
                json.dumps(component.metadata),
            ))
        
        logger.info(f"Created component: {name} ({component.id})")
        return component
    
    def get_component(self, component_id: str) -> Optional[Component]:
        """Get a component by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM components WHERE id = ?", (component_id,)
            ).fetchone()
            
            if row is None:
                return None
            
            return self._row_to_component(row)
    
    def list_components(self, category: Optional[str] = None,
                       search: Optional[str] = None,
                       page: int = 1, limit: int = 50) -> tuple[List[Component], int]:
        """List components with optional filtering."""
        offset = (page - 1) * limit
        conditions = []
        params = []
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        if search:
            conditions.append("(name LIKE ? OR description LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self._get_connection() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM components WHERE {where_clause}", params
            ).fetchone()[0]
            
            rows = conn.execute(
                f"SELECT * FROM components WHERE {where_clause} ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                params + [limit, offset]
            ).fetchall()
            
            return [self._row_to_component(row) for row in rows], total
    
    def update_component(self, component_id: str, **kwargs) -> Optional[Component]:
        """Update a component."""
        component = self.get_component(component_id)
        if component is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(component, key):
                setattr(component, key, value)
        component.updated_at = datetime.utcnow()
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE components SET name = ?, category = ?, code = ?,
                       language = ?, description = ?, usage_example = ?,
                       version = ?, updated_at = ?, tags = ?, metadata = ?
                WHERE id = ?
            """, (
                component.name, component.category, component.code,
                component.language, component.description, component.usage_example,
                component.version, component.updated_at.isoformat(),
                json.dumps(component.tags), json.dumps(component.metadata),
                component.id,
            ))
        
        return component
    
    def delete_component(self, component_id: str) -> bool:
        """Delete a component."""
        with self._get_connection() as conn:
            result = conn.execute(
                "DELETE FROM components WHERE id = ?", (component_id,)
            )
            return result.rowcount > 0
    
    def _row_to_component(self, row) -> Component:
        """Convert a database row to a Component."""
        return Component(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            code=row["code"],
            language=row["language"],
            description=row["description"],
            usage_example=row["usage_example"],
            version=row["version"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
        )
    
    # =========================================================================
    # Notes CRUD
    # =========================================================================
    
    def create_note(self, resource_type: str, resource_id: str, 
                   content: str) -> Note:
        """Create a new note."""
        note = Note(
            id=str(uuid.uuid4()),
            resource_type=resource_type,
            resource_id=resource_id,
            content=content,
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO notes (id, resource_type, resource_id, content,
                                  created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                note.id, note.resource_type, note.resource_id, note.content,
                note.created_at.isoformat(), note.updated_at.isoformat(),
            ))
        
        return note
    
    def get_notes(self, resource_type: str, resource_id: str) -> List[Note]:
        """Get notes for a resource."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM notes WHERE resource_type = ? AND resource_id = ?
                ORDER BY created_at DESC
            """, (resource_type, resource_id)).fetchall()
            
            return [self._row_to_note(row) for row in rows]
    
    def update_note(self, note_id: str, content: str) -> Optional[Note]:
        """Update a note."""
        with self._get_connection() as conn:
            now = datetime.utcnow().isoformat()
            conn.execute("""
                UPDATE notes SET content = ?, updated_at = ? WHERE id = ?
            """, (content, now, note_id))
            
            row = conn.execute(
                "SELECT * FROM notes WHERE id = ?", (note_id,)
            ).fetchone()
            
            if row:
                return self._row_to_note(row)
            return None
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note."""
        with self._get_connection() as conn:
            result = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            return result.rowcount > 0
    
    def _row_to_note(self, row) -> Note:
        """Convert a database row to a Note."""
        return Note(
            id=row["id"],
            resource_type=row["resource_type"],
            resource_id=row["resource_id"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
    
    # =========================================================================
    # Tags
    # =========================================================================
    
    def get_or_create_tag(self, name: str, color: str = "#6366f1") -> Tag:
        """Get or create a tag by name."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tags WHERE name = ?", (name,)
            ).fetchone()
            
            if row:
                return Tag(id=row["id"], name=row["name"], color=row["color"])
            
            tag = Tag(id=str(uuid.uuid4()), name=name, color=color)
            conn.execute(
                "INSERT INTO tags (id, name, color) VALUES (?, ?, ?)",
                (tag.id, tag.name, tag.color)
            )
            return tag
    
    def list_tags(self) -> List[Tag]:
        """List all tags with resource counts."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT t.*, COUNT(rt.tag_id) as resource_count
                FROM tags t
                LEFT JOIN resource_tags rt ON t.id = rt.tag_id
                GROUP BY t.id
                ORDER BY t.name
            """).fetchall()
            
            return [
                Tag(
                    id=row["id"],
                    name=row["name"],
                    color=row["color"],
                    resource_count=row["resource_count"],
                )
                for row in rows
            ]
    
    def add_tag_to_resource(self, resource_type: str, resource_id: str, 
                           tag_name: str) -> bool:
        """Add a tag to a resource."""
        tag = self.get_or_create_tag(tag_name)
        
        with self._get_connection() as conn:
            try:
                conn.execute("""
                    INSERT INTO resource_tags (resource_type, resource_id, tag_id)
                    VALUES (?, ?, ?)
                """, (resource_type, resource_id, tag.id))
                return True
            except sqlite3.IntegrityError:
                return False  # Already tagged
    
    def remove_tag_from_resource(self, resource_type: str, resource_id: str,
                                tag_name: str) -> bool:
        """Remove a tag from a resource."""
        with self._get_connection() as conn:
            result = conn.execute("""
                DELETE FROM resource_tags 
                WHERE resource_type = ? AND resource_id = ? 
                AND tag_id = (SELECT id FROM tags WHERE name = ?)
            """, (resource_type, resource_id, tag_name))
            return result.rowcount > 0
    
    # =========================================================================
    # Stats
    # =========================================================================
    
    def get_stats(self) -> dict:
        """Get overall statistics."""
        with self._get_connection() as conn:
            projects = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
            agents = conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
            flows = conn.execute("SELECT COUNT(*) FROM flows").fetchone()[0]
            components = conn.execute("SELECT COUNT(*) FROM components").fetchone()[0]
            
            return {
                "projects_count": projects,
                "agents_count": agents,
                "flows_count": flows,
                "components_count": components,
                "experiments_count": 0,  # Will be populated from MLFlow
                "active_sessions": 0,  # Will be populated from sessions
            }

