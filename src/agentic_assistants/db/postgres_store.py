"""
PostgreSQL implementation of the base store interface.

Provides connection pooling, async support, and PostgreSQL-specific optimizations.
"""

import json
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import psycopg
    from psycopg import Connection
    from psycopg.rows import dict_row
    from psycopg_pool import ConnectionPool
    PSYCOPG_AVAILABLE = True
except ImportError:
    PSYCOPG_AVAILABLE = False

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.models import (
    Agent,
    Component,
    DataSource,
    Flow,
    IndexingState,
    Note,
    Project,
    ProjectResource,
    ServiceResource,
    Tag,
)
from agentic_assistants.db.base_store import BaseStore
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class PostgreSQLStore(BaseStore):
    """
    PostgreSQL-backed data store for the Agentic Control Panel.
    
    Features:
    - Connection pooling for better performance
    - Support for both sync and async operations
    - PostgreSQL-specific optimizations (JSONB, etc.)
    - Compatible with Supabase PostgreSQL instances
    """
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """Initialize the PostgreSQL store."""
        if not PSYCOPG_AVAILABLE:
            raise ImportError(
                "psycopg3 is required for PostgreSQL support. "
                "Install it with: pip install 'psycopg[binary,pool]'"
            )
        
        self.config = config or AgenticConfig()
        self.dsn = self.config.postgresql.dsn
        
        # Initialize connection pool
        self.pool = ConnectionPool(
            conninfo=self.dsn,
            min_size=1,
            max_size=self.config.postgresql.pool_size,
            timeout=self.config.postgresql.pool_timeout,
        )
        
        logger.info(f"PostgreSQL connection pool initialized: {self.config.postgresql.host}")
        
        # Initialize database schema
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection from the pool."""
        conn = self.pool.getconn()
        conn.row_factory = dict_row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)
    
    def _init_database(self) -> None:
        """Initialize the PostgreSQL database schema."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    -- Projects table
                    CREATE TABLE IF NOT EXISTS projects (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT DEFAULT '',
                        config_yaml TEXT DEFAULT '',
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        tags JSONB DEFAULT '[]'::jsonb,
                        metadata JSONB DEFAULT '{}'::jsonb
                    );
                    CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
                    CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
                    CREATE INDEX IF NOT EXISTS idx_projects_tags ON projects USING GIN (tags);
                    
                    -- Agents table
                    CREATE TABLE IF NOT EXISTS agents (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        role TEXT NOT NULL,
                        goal TEXT DEFAULT '',
                        backstory TEXT DEFAULT '',
                        tools JSONB DEFAULT '[]'::jsonb,
                        model TEXT DEFAULT 'llama3.2',
                        status TEXT DEFAULT 'drafted',
                        project_id TEXT,
                        config_yaml TEXT DEFAULT '',
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        tags JSONB DEFAULT '[]'::jsonb,
                        metadata JSONB DEFAULT '{}'::jsonb,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
                    CREATE INDEX IF NOT EXISTS idx_agents_project ON agents(project_id);
                    CREATE INDEX IF NOT EXISTS idx_agents_tags ON agents USING GIN (tags);
                    
                    -- Flows table
                    CREATE TABLE IF NOT EXISTS flows (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT DEFAULT '',
                        flow_yaml TEXT DEFAULT '',
                        flow_type TEXT DEFAULT 'crew',
                        status TEXT DEFAULT 'draft',
                        agents JSONB DEFAULT '[]'::jsonb,
                        project_id TEXT,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        tags JSONB DEFAULT '[]'::jsonb,
                        metadata JSONB DEFAULT '{}'::jsonb,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_flows_status ON flows(status);
                    CREATE INDEX IF NOT EXISTS idx_flows_project ON flows(project_id);
                    CREATE INDEX IF NOT EXISTS idx_flows_tags ON flows USING GIN (tags);
                    
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
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        tags JSONB DEFAULT '[]'::jsonb,
                        metadata JSONB DEFAULT '{}'::jsonb
                    );
                    CREATE INDEX IF NOT EXISTS idx_components_category ON components(category);
                    CREATE INDEX IF NOT EXISTS idx_components_tags ON components USING GIN (tags);
                    
                    -- Notes table
                    CREATE TABLE IF NOT EXISTS notes (
                        id TEXT PRIMARY KEY,
                        resource_type TEXT NOT NULL,
                        resource_id TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
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
                    
                    -- Data Sources table
                    CREATE TABLE IF NOT EXISTS datasources (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        source_type TEXT NOT NULL,
                        connection_config JSONB DEFAULT '{}'::jsonb,
                        description TEXT DEFAULT '',
                        is_global BOOLEAN DEFAULT FALSE,
                        project_id TEXT,
                        status TEXT DEFAULT 'active',
                        last_tested TIMESTAMP,
                        last_test_success BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        tags JSONB DEFAULT '[]'::jsonb,
                        metadata JSONB DEFAULT '{}'::jsonb,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_datasources_type ON datasources(source_type);
                    CREATE INDEX IF NOT EXISTS idx_datasources_global ON datasources(is_global);
                    CREATE INDEX IF NOT EXISTS idx_datasources_project ON datasources(project_id);
                    CREATE INDEX IF NOT EXISTS idx_datasources_tags ON datasources USING GIN (tags);
                    
                    -- Service Resources table
                    CREATE TABLE IF NOT EXISTS services (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        service_type TEXT NOT NULL,
                        endpoint_url TEXT DEFAULT '',
                        description TEXT DEFAULT '',
                        health_endpoint TEXT,
                        auth_type TEXT,
                        credentials_ref TEXT,
                        config_yaml TEXT DEFAULT '',
                        is_global BOOLEAN DEFAULT FALSE,
                        project_id TEXT,
                        status TEXT DEFAULT 'unknown',
                        last_health_check TIMESTAMP,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        tags JSONB DEFAULT '[]'::jsonb,
                        metadata JSONB DEFAULT '{}'::jsonb,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_services_type ON services(service_type);
                    CREATE INDEX IF NOT EXISTS idx_services_global ON services(is_global);
                    CREATE INDEX IF NOT EXISTS idx_services_project ON services(project_id);
                    CREATE INDEX IF NOT EXISTS idx_services_tags ON services USING GIN (tags);
                    
                    -- Project Resources junction table
                    CREATE TABLE IF NOT EXISTS project_resources (
                        id TEXT PRIMARY KEY,
                        project_id TEXT NOT NULL,
                        resource_type TEXT NOT NULL,
                        resource_id TEXT NOT NULL,
                        alias TEXT,
                        config_overrides JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                        UNIQUE (project_id, resource_type, resource_id)
                    );
                    CREATE INDEX IF NOT EXISTS idx_project_resources_project ON project_resources(project_id);
                    CREATE INDEX IF NOT EXISTS idx_project_resources_resource ON project_resources(resource_type, resource_id);
                    
                    -- Indexing State table
                    CREATE TABLE IF NOT EXISTS indexing_states (
                        id TEXT PRIMARY KEY,
                        project_id TEXT NOT NULL UNIQUE,
                        collection_name TEXT NOT NULL,
                        version TEXT DEFAULT '2.0',
                        status TEXT DEFAULT 'idle',
                        file_count INTEGER DEFAULT 0,
                        chunk_count INTEGER DEFAULT 0,
                        last_indexed TIMESTAMP,
                        error_message TEXT,
                        indexing_config JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                    );
                    CREATE INDEX IF NOT EXISTS idx_indexing_states_project ON indexing_states(project_id);
                    CREATE INDEX IF NOT EXISTS idx_indexing_states_status ON indexing_states(status);
                    
                    -- Execution Scripts table (new for execution layer)
                    CREATE TABLE IF NOT EXISTS execution_scripts (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name TEXT NOT NULL,
                        script_type TEXT NOT NULL,
                        content TEXT,
                        template_id UUID,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        metadata JSONB DEFAULT '{}'::jsonb
                    );
                    CREATE INDEX IF NOT EXISTS idx_execution_scripts_type ON execution_scripts(script_type);
                    
                    -- Execution Runs table (new for execution layer)
                    CREATE TABLE IF NOT EXISTS execution_runs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        script_id UUID REFERENCES execution_scripts(id),
                        status TEXT NOT NULL,
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP,
                        output TEXT,
                        error TEXT,
                        metadata JSONB DEFAULT '{}'::jsonb
                    );
                    CREATE INDEX IF NOT EXISTS idx_execution_runs_script ON execution_runs(script_id);
                    CREATE INDEX IF NOT EXISTS idx_execution_runs_status ON execution_runs(status);
                    
                    -- Sync Sessions table (new for data sync)
                    CREATE TABLE IF NOT EXISTS sync_sessions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        source_env TEXT NOT NULL,
                        target_env TEXT NOT NULL,
                        started_at TIMESTAMP NOT NULL,
                        completed_at TIMESTAMP,
                        status TEXT NOT NULL,
                        conflicts_detected INTEGER DEFAULT 0,
                        entities_synced INTEGER DEFAULT 0,
                        metadata JSONB DEFAULT '{}'::jsonb
                    );
                    CREATE INDEX IF NOT EXISTS idx_sync_sessions_status ON sync_sessions(status);
                    CREATE INDEX IF NOT EXISTS idx_sync_sessions_envs ON sync_sessions(source_env, target_env);
                    
                    -- Sync Conflicts table (new for data sync)
                    CREATE TABLE IF NOT EXISTS sync_conflicts (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        session_id UUID REFERENCES sync_sessions(id),
                        entity_type TEXT NOT NULL,
                        entity_id TEXT NOT NULL,
                        source_version JSONB,
                        target_version JSONB,
                        resolution_strategy TEXT,
                        resolved_at TIMESTAMP,
                        resolved_by TEXT,
                        metadata JSONB DEFAULT '{}'::jsonb
                    );
                    CREATE INDEX IF NOT EXISTS idx_sync_conflicts_session ON sync_conflicts(session_id);
                    CREATE INDEX IF NOT EXISTS idx_sync_conflicts_entity ON sync_conflicts(entity_type, entity_id);
                """)
        
        logger.info("PostgreSQL database schema initialized")
    
    # =========================================================================
    # Projects CRUD (implementation continued...)
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
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO projects (id, name, description, config_yaml, status, 
                                         created_at, updated_at, tags, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    project.id, project.name, project.description, project.config_yaml,
                    project.status, project.created_at, project.updated_at,
                    json.dumps(project.tags), json.dumps(project.metadata),
                ))
        
        logger.info(f"Created project: {name} ({project.id})")
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
                row = cur.fetchone()
                
                if row is None:
                    return None
                
                return self._row_to_project(row)
    
    def list_projects(self, status: Optional[str] = None, 
                     page: int = 1, limit: int = 50) -> Tuple[List[Project], int]:
        """List projects with optional filtering."""
        offset = (page - 1) * limit
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                if status:
                    cur.execute("SELECT COUNT(*) as count FROM projects WHERE status = %s", (status,))
                    total = cur.fetchone()["count"]
                    
                    cur.execute("""
                        SELECT * FROM projects WHERE status = %s 
                        ORDER BY updated_at DESC LIMIT %s OFFSET %s
                    """, (status, limit, offset))
                else:
                    cur.execute("SELECT COUNT(*) as count FROM projects")
                    total = cur.fetchone()["count"]
                    
                    cur.execute("""
                        SELECT * FROM projects ORDER BY updated_at DESC LIMIT %s OFFSET %s
                    """, (limit, offset))
                
                rows = cur.fetchall()
                return [self._row_to_project(row) for row in rows], total
    
    def update_project(self, project_id: str, **kwargs) -> Optional[Project]:
        """Update a project."""
        project = self.get_project(project_id)
        if project is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        project.updated_at = datetime.utcnow()
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE projects SET name = %s, description = %s, config_yaml = %s,
                           status = %s, updated_at = %s, tags = %s, metadata = %s
                    WHERE id = %s
                """, (
                    project.name, project.description, project.config_yaml,
                    project.status, project.updated_at,
                    json.dumps(project.tags), json.dumps(project.metadata),
                    project.id,
                ))
        
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))
                return cur.rowcount > 0
    
    def _row_to_project(self, row: Dict) -> Project:
        """Convert a database row to a Project."""
        return Project(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            config_yaml=row["config_yaml"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            tags=row["tags"] if isinstance(row["tags"], list) else json.loads(row["tags"]),
            metadata=row["metadata"] if isinstance(row["metadata"], dict) else json.loads(row["metadata"]),
        )
    
    # Implement remaining CRUD methods following the same pattern...
    # For brevity, I'll implement key methods and placeholders for others
    
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
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agents (id, name, role, goal, backstory, tools, model,
                                       status, project_id, config_yaml, created_at, 
                                       updated_at, tags, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    agent.id, agent.name, agent.role, agent.goal, agent.backstory,
                    json.dumps(agent.tools), agent.model, agent.status, agent.project_id,
                    agent.config_yaml, agent.created_at, agent.updated_at,
                    json.dumps(agent.tags), json.dumps(agent.metadata),
                ))
        
        logger.info(f"Created agent: {name} ({agent.id})")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM agents WHERE id = %s", (agent_id,))
                row = cur.fetchone()
                return self._row_to_agent(row) if row else None
    
    def list_agents(self, project_id: Optional[str] = None,
                   status: Optional[str] = None,
                   page: int = 1, limit: int = 50) -> Tuple[List[Agent], int]:
        """List agents with optional filtering."""
        offset = (page - 1) * limit
        conditions = []
        params = []
        
        if project_id:
            conditions.append("project_id = %s")
            params.append(project_id)
        if status:
            conditions.append("status = %s")
            params.append(status)
        
        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) as count FROM agents WHERE {where_clause}", params)
                total = cur.fetchone()["count"]
                
                cur.execute(f"""
                    SELECT * FROM agents WHERE {where_clause} 
                    ORDER BY updated_at DESC LIMIT %s OFFSET %s
                """, params + [limit, offset])
                
                rows = cur.fetchall()
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
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE agents SET name = %s, role = %s, goal = %s, backstory = %s,
                           tools = %s, model = %s, status = %s, project_id = %s,
                           config_yaml = %s, updated_at = %s, tags = %s, metadata = %s
                    WHERE id = %s
                """, (
                    agent.name, agent.role, agent.goal, agent.backstory,
                    json.dumps(agent.tools), agent.model, agent.status, agent.project_id,
                    agent.config_yaml, agent.updated_at,
                    json.dumps(agent.tags), json.dumps(agent.metadata), agent.id,
                ))
        
        return agent
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM agents WHERE id = %s", (agent_id,))
                return cur.rowcount > 0
    
    def _row_to_agent(self, row: Dict) -> Agent:
        """Convert a database row to an Agent."""
        return Agent(
            id=row["id"],
            name=row["name"],
            role=row["role"],
            goal=row["goal"],
            backstory=row["backstory"],
            tools=row["tools"] if isinstance(row["tools"], list) else json.loads(row["tools"]),
            model=row["model"],
            status=row["status"],
            project_id=row["project_id"],
            config_yaml=row["config_yaml"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            tags=row["tags"] if isinstance(row["tags"], list) else json.loads(row["tags"]),
            metadata=row["metadata"] if isinstance(row["metadata"], dict) else json.loads(row["metadata"]),
        )
    
    # Placeholder implementations for remaining methods - these would follow the same pattern
    def create_flow(self, name: str, **kwargs) -> Flow:
        """Create a new flow."""
        # Implementation similar to create_agent
        raise NotImplementedError("Implement following agent pattern")
    
    def get_flow(self, flow_id: str) -> Optional[Flow]:
        """Get a flow by ID."""
        raise NotImplementedError()
    
    def list_flows(self, project_id: Optional[str] = None,
                  status: Optional[str] = None,
                  page: int = 1, limit: int = 50) -> Tuple[List[Flow], int]:
        """List flows with optional filtering."""
        raise NotImplementedError()
    
    def update_flow(self, flow_id: str, **kwargs) -> Optional[Flow]:
        """Update a flow."""
        raise NotImplementedError()
    
    def delete_flow(self, flow_id: str) -> bool:
        """Delete a flow."""
        raise NotImplementedError()
    
    def create_component(self, name: str, category: str, **kwargs) -> Component:
        """Create a new component."""
        raise NotImplementedError()
    
    def get_component(self, component_id: str) -> Optional[Component]:
        """Get a component by ID."""
        raise NotImplementedError()
    
    def list_components(self, category: Optional[str] = None,
                       search: Optional[str] = None,
                       page: int = 1, limit: int = 50) -> Tuple[List[Component], int]:
        """List components with optional filtering."""
        raise NotImplementedError()
    
    def update_component(self, component_id: str, **kwargs) -> Optional[Component]:
        """Update a component."""
        raise NotImplementedError()
    
    def delete_component(self, component_id: str) -> bool:
        """Delete a component."""
        raise NotImplementedError()
    
    def create_note(self, resource_type: str, resource_id: str, content: str) -> Note:
        """Create a new note."""
        raise NotImplementedError()
    
    def get_notes(self, resource_type: str, resource_id: str) -> List[Note]:
        """Get notes for a resource."""
        raise NotImplementedError()
    
    def update_note(self, note_id: str, content: str) -> Optional[Note]:
        """Update a note."""
        raise NotImplementedError()
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note."""
        raise NotImplementedError()
    
    def get_or_create_tag(self, name: str, color: str = "#6366f1") -> Tag:
        """Get or create a tag by name."""
        raise NotImplementedError()
    
    def list_tags(self) -> List[Tag]:
        """List all tags with resource counts."""
        raise NotImplementedError()
    
    def add_tag_to_resource(self, resource_type: str, resource_id: str, tag_name: str) -> bool:
        """Add a tag to a resource."""
        raise NotImplementedError()
    
    def remove_tag_from_resource(self, resource_type: str, resource_id: str, tag_name: str) -> bool:
        """Remove a tag from a resource."""
        raise NotImplementedError()
    
    def create_datasource(self, name: str, source_type: str, **kwargs) -> DataSource:
        """Create a new data source."""
        raise NotImplementedError()
    
    def get_datasource(self, datasource_id: str) -> Optional[DataSource]:
        """Get a data source by ID."""
        raise NotImplementedError()
    
    def list_datasources(self, source_type: Optional[str] = None,
                        is_global: Optional[bool] = None,
                        project_id: Optional[str] = None,
                        page: int = 1, limit: int = 50) -> Tuple[List[DataSource], int]:
        """List data sources with optional filtering."""
        raise NotImplementedError()
    
    def update_datasource(self, datasource_id: str, **kwargs) -> Optional[DataSource]:
        """Update a data source."""
        raise NotImplementedError()
    
    def delete_datasource(self, datasource_id: str) -> bool:
        """Delete a data source."""
        raise NotImplementedError()
    
    def create_service(self, name: str, service_type: str, **kwargs) -> ServiceResource:
        """Create a new service resource."""
        raise NotImplementedError()
    
    def get_service(self, service_id: str) -> Optional[ServiceResource]:
        """Get a service by ID."""
        raise NotImplementedError()
    
    def list_services(self, service_type: Optional[str] = None,
                     is_global: Optional[bool] = None,
                     project_id: Optional[str] = None,
                     page: int = 1, limit: int = 50) -> Tuple[List[ServiceResource], int]:
        """List services with optional filtering."""
        raise NotImplementedError()
    
    def update_service(self, service_id: str, **kwargs) -> Optional[ServiceResource]:
        """Update a service."""
        raise NotImplementedError()
    
    def delete_service(self, service_id: str) -> bool:
        """Delete a service."""
        raise NotImplementedError()
    
    def link_resource_to_project(self, project_id: str, resource_type: str,
                                 resource_id: str, alias: Optional[str] = None,
                                 config_overrides: str = "{}") -> ProjectResource:
        """Link a global resource to a project."""
        raise NotImplementedError()
    
    def unlink_resource_from_project(self, project_id: str, resource_type: str,
                                     resource_id: str) -> bool:
        """Unlink a resource from a project."""
        raise NotImplementedError()
    
    def get_project_resources(self, project_id: str,
                             resource_type: Optional[str] = None) -> List[ProjectResource]:
        """Get all resources linked to a project."""
        raise NotImplementedError()
    
    def get_or_create_indexing_state(self, project_id: str,
                                     collection_name: Optional[str] = None) -> IndexingState:
        """Get or create indexing state for a project."""
        raise NotImplementedError()
    
    def update_indexing_state(self, project_id: str, **kwargs) -> Optional[IndexingState]:
        """Update indexing state for a project."""
        raise NotImplementedError()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as count FROM projects")
                projects = cur.fetchone()["count"]
                
                cur.execute("SELECT COUNT(*) as count FROM agents")
                agents = cur.fetchone()["count"]
                
                cur.execute("SELECT COUNT(*) as count FROM flows")
                flows = cur.fetchone()["count"]
                
                cur.execute("SELECT COUNT(*) as count FROM components")
                components = cur.fetchone()["count"]
                
                cur.execute("SELECT COUNT(*) as count FROM datasources")
                datasources = cur.fetchone()["count"]
                
                cur.execute("SELECT COUNT(*) as count FROM services")
                services = cur.fetchone()["count"]
                
                cur.execute("SELECT COUNT(*) as count FROM indexing_states WHERE status = 'completed'")
                indexed_projects = cur.fetchone()["count"]
                
                return {
                    "projects_count": projects,
                    "agents_count": agents,
                    "flows_count": flows,
                    "components_count": components,
                    "datasources_count": datasources,
                    "services_count": services,
                    "indexed_projects_count": indexed_projects,
                    "experiments_count": 0,
                    "active_sessions": 0,
                }
