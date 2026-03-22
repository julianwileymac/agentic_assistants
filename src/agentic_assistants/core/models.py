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
class TestCase:
    """A reusable test case for framework components."""
    id: str
    name: str
    description: str = ""
    resource_type: str = "component"
    resource_id: Optional[str] = None
    language: str = "python"
    code: str = ""
    input_data: str = ""
    expected_output: str = ""
    test_type: str = "unit"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "language": self.language,
            "code": self.code,
            "input_data": self.input_data,
            "expected_output": self.expected_output,
            "test_type": self.test_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class TestSuite:
    """A collection of test cases."""
    id: str
    name: str
    description: str = ""
    resource_type: str = "project"
    resource_id: Optional[str] = None
    test_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "test_ids": self.test_ids,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class TestRun:
    """A single execution of a test case or suite."""
    id: str
    run_name: str = ""
    test_case_id: Optional[str] = None
    suite_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    status: str = "pending"
    sandbox_enabled: bool = True
    tracking_enabled: bool = False
    agent_eval_enabled: bool = False
    rl_metrics_enabled: bool = False
    evaluation_provider: Optional[str] = None
    evaluation_model: Optional[str] = None
    evaluation_endpoint: Optional[str] = None
    evaluation_hf_execution_mode: Optional[str] = None
    dataset_id: Optional[str] = None
    input_data: str = ""
    output_data: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "run_name": self.run_name,
            "test_case_id": self.test_case_id,
            "suite_id": self.suite_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "status": self.status,
            "sandbox_enabled": self.sandbox_enabled,
            "tracking_enabled": self.tracking_enabled,
            "agent_eval_enabled": self.agent_eval_enabled,
            "rl_metrics_enabled": self.rl_metrics_enabled,
            "evaluation_provider": self.evaluation_provider,
            "evaluation_model": self.evaluation_model,
            "evaluation_endpoint": self.evaluation_endpoint,
            "evaluation_hf_execution_mode": self.evaluation_hf_execution_mode,
            "dataset_id": self.dataset_id,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "metrics": self.metrics,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class TestResult:
    """Result for a single test case execution."""
    id: str
    run_id: str
    test_case_id: Optional[str] = None
    name: str = ""
    passed: bool = False
    status: str = "failed"
    output: str = ""
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "test_case_id": self.test_case_id,
            "name": self.name,
            "passed": self.passed,
            "status": self.status,
            "output": self.output,
            "error_message": self.error_message,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat(),
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


@dataclass
class DataSource:
    """A data source connection configuration."""
    id: str
    name: str
    source_type: str  # database, file_store, api
    connection_config: str = ""  # JSON string with connection details
    description: str = ""
    is_global: bool = False  # True = global registry, False = project-scoped
    project_id: Optional[str] = None  # Only set if is_global=False
    status: str = "active"  # active, inactive, error
    last_tested: Optional[datetime] = None
    last_test_success: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "source_type": self.source_type,
            "connection_config": self.connection_config,
            "description": self.description,
            "is_global": self.is_global,
            "project_id": self.project_id,
            "status": self.status,
            "last_tested": self.last_tested.isoformat() if self.last_tested else None,
            "last_test_success": self.last_test_success,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Parse and return the connection configuration."""
        if self.connection_config:
            try:
                return json.loads(self.connection_config)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """Set the connection configuration from a dict."""
        self.connection_config = json.dumps(config)


@dataclass
class ServiceResource:
    """An external service resource associated with a project."""
    id: str
    name: str
    service_type: str  # web_ui, api_endpoint, file_store, background_service, database, ml_deployment
    endpoint_url: str = ""
    description: str = ""
    health_endpoint: Optional[str] = None
    auth_type: Optional[str] = None  # none, api_key, oauth, basic
    credentials_ref: Optional[str] = None  # Reference to secrets store
    config_yaml: str = ""
    is_global: bool = False
    project_id: Optional[str] = None
    status: str = "unknown"  # healthy, unhealthy, unknown
    last_health_check: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "service_type": self.service_type,
            "endpoint_url": self.endpoint_url,
            "description": self.description,
            "health_endpoint": self.health_endpoint,
            "auth_type": self.auth_type,
            "credentials_ref": self.credentials_ref,
            "config_yaml": self.config_yaml,
            "is_global": self.is_global,
            "project_id": self.project_id,
            "status": self.status,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class ProjectResource:
    """Junction table linking projects to global resources."""
    id: str
    project_id: str
    resource_type: str  # datasource, service
    resource_id: str
    alias: Optional[str] = None  # Optional project-local alias
    config_overrides: str = ""  # JSON string with project-specific overrides
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "alias": self.alias,
            "config_overrides": self.config_overrides,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class IndexingState:
    """Tracks codebase indexing status for a project."""
    id: str
    project_id: str
    collection_name: str
    version: str = "2.0"
    status: str = "idle"  # idle, indexing, completed, failed
    file_count: int = 0
    chunk_count: int = 0
    last_indexed: Optional[datetime] = None
    error_message: Optional[str] = None
    indexing_config: str = ""  # JSON string with indexing configuration
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "collection_name": self.collection_name,
            "version": self.version,
            "status": self.status,
            "file_count": self.file_count,
            "chunk_count": self.chunk_count,
            "last_indexed": self.last_indexed.isoformat() if self.last_indexed else None,
            "error_message": self.error_message,
            "indexing_config": self.indexing_config,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
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
                
                -- Test Cases table
                CREATE TABLE IF NOT EXISTS test_cases (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    resource_type TEXT NOT NULL,
                    resource_id TEXT,
                    language TEXT DEFAULT 'python',
                    code TEXT DEFAULT '',
                    input_data TEXT DEFAULT '',
                    expected_output TEXT DEFAULT '',
                    test_type TEXT DEFAULT 'unit',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_test_cases_resource ON test_cases(resource_type, resource_id);
                CREATE INDEX IF NOT EXISTS idx_test_cases_type ON test_cases(test_type);
                
                -- Test Suites table
                CREATE TABLE IF NOT EXISTS test_suites (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    resource_type TEXT NOT NULL,
                    resource_id TEXT,
                    test_ids TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_test_suites_resource ON test_suites(resource_type, resource_id);
                
                -- Test Runs table
                CREATE TABLE IF NOT EXISTS test_runs (
                    id TEXT PRIMARY KEY,
                    run_name TEXT DEFAULT '',
                    test_case_id TEXT,
                    suite_id TEXT,
                    resource_type TEXT,
                    resource_id TEXT,
                    status TEXT DEFAULT 'pending',
                    sandbox_enabled INTEGER DEFAULT 1,
                    tracking_enabled INTEGER DEFAULT 0,
                    agent_eval_enabled INTEGER DEFAULT 0,
                    rl_metrics_enabled INTEGER DEFAULT 0,
                    evaluation_provider TEXT,
                    evaluation_model TEXT,
                    evaluation_endpoint TEXT,
                    evaluation_hf_execution_mode TEXT,
                    dataset_id TEXT,
                    input_data TEXT DEFAULT '',
                    output_data TEXT DEFAULT '',
                    metrics TEXT DEFAULT '{}',
                    error_message TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    duration_seconds REAL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_test_runs_status ON test_runs(status);
                CREATE INDEX IF NOT EXISTS idx_test_runs_resource ON test_runs(resource_type, resource_id);
                
                -- Test Results table
                CREATE TABLE IF NOT EXISTS test_results (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    test_case_id TEXT,
                    name TEXT DEFAULT '',
                    passed INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'failed',
                    output TEXT DEFAULT '',
                    error_message TEXT,
                    metrics TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES test_runs(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_test_results_run ON test_results(run_id);
                
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
                
                -- Data Sources table
                CREATE TABLE IF NOT EXISTS datasources (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    connection_config TEXT DEFAULT '{}',
                    description TEXT DEFAULT '',
                    is_global INTEGER DEFAULT 0,
                    project_id TEXT,
                    status TEXT DEFAULT 'active',
                    last_tested TEXT,
                    last_test_success INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
                );
                CREATE INDEX IF NOT EXISTS idx_datasources_type ON datasources(source_type);
                CREATE INDEX IF NOT EXISTS idx_datasources_global ON datasources(is_global);
                CREATE INDEX IF NOT EXISTS idx_datasources_project ON datasources(project_id);
                
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
                    is_global INTEGER DEFAULT 0,
                    project_id TEXT,
                    status TEXT DEFAULT 'unknown',
                    last_health_check TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
                );
                CREATE INDEX IF NOT EXISTS idx_services_type ON services(service_type);
                CREATE INDEX IF NOT EXISTS idx_services_global ON services(is_global);
                CREATE INDEX IF NOT EXISTS idx_services_project ON services(project_id);
                
                -- Project Resources junction table
                CREATE TABLE IF NOT EXISTS project_resources (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    alias TEXT,
                    config_overrides TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
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
                    last_indexed TEXT,
                    error_message TEXT,
                    indexing_config TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_indexing_states_project ON indexing_states(project_id);
                CREATE INDEX IF NOT EXISTS idx_indexing_states_status ON indexing_states(status);
            """)
            self._migrate_test_runs_schema(conn)
        logger.info(f"Database initialized at {self.db_path}")

    def _migrate_test_runs_schema(self, conn: sqlite3.Connection) -> None:
        """Apply idempotent migrations for test_runs table evolution."""
        existing_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(test_runs)").fetchall()
        }
        expected_columns: Dict[str, str] = {
            "evaluation_provider": "TEXT",
            "evaluation_model": "TEXT",
            "evaluation_endpoint": "TEXT",
            "evaluation_hf_execution_mode": "TEXT",
        }
        for column_name, column_type in expected_columns.items():
            if column_name in existing_columns:
                continue
            conn.execute(f"ALTER TABLE test_runs ADD COLUMN {column_name} {column_type}")
    
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
    # Testing CRUD
    # =========================================================================
    
    def create_test_case(self, name: str, resource_type: str, **kwargs) -> TestCase:
        """Create a new test case."""
        test_case = TestCase(
            id=str(uuid.uuid4()),
            name=name,
            description=kwargs.get("description", ""),
            resource_type=resource_type,
            resource_id=kwargs.get("resource_id"),
            language=kwargs.get("language", "python"),
            code=kwargs.get("code", ""),
            input_data=kwargs.get("input_data", ""),
            expected_output=kwargs.get("expected_output", ""),
            test_type=kwargs.get("test_type", "unit"),
            tags=kwargs.get("tags", []),
            metadata=kwargs.get("metadata", {}),
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO test_cases (id, name, description, resource_type, resource_id,
                                       language, code, input_data, expected_output, test_type,
                                       created_at, updated_at, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_case.id, test_case.name, test_case.description, test_case.resource_type,
                test_case.resource_id, test_case.language, test_case.code, test_case.input_data,
                test_case.expected_output, test_case.test_type, test_case.created_at.isoformat(),
                test_case.updated_at.isoformat(), json.dumps(test_case.tags),
                json.dumps(test_case.metadata),
            ))
        
        return test_case
    
    def get_test_case(self, test_case_id: str) -> Optional[TestCase]:
        """Get a test case by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM test_cases WHERE id = ?", (test_case_id,)
            ).fetchone()
            
            if row is None:
                return None
            return self._row_to_test_case(row)
    
    def list_test_cases(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        test_type: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[List[TestCase], int]:
        """List test cases with optional filtering."""
        offset = (page - 1) * limit
        conditions = []
        params = []
        
        if resource_type:
            conditions.append("resource_type = ?")
            params.append(resource_type)
        if resource_id:
            conditions.append("resource_id = ?")
            params.append(resource_id)
        if test_type:
            conditions.append("test_type = ?")
            params.append(test_type)
        if search:
            conditions.append("(name LIKE ? OR description LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self._get_connection() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM test_cases WHERE {where_clause}", params
            ).fetchone()[0]
            
            rows = conn.execute(
                f"SELECT * FROM test_cases WHERE {where_clause} ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                params + [limit, offset]
            ).fetchall()
            
            return [self._row_to_test_case(row) for row in rows], total
    
    def update_test_case(self, test_case_id: str, **kwargs) -> Optional[TestCase]:
        """Update a test case."""
        test_case = self.get_test_case(test_case_id)
        if test_case is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(test_case, key):
                setattr(test_case, key, value)
        test_case.updated_at = datetime.utcnow()
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE test_cases SET name = ?, description = ?, resource_type = ?, resource_id = ?,
                       language = ?, code = ?, input_data = ?, expected_output = ?, test_type = ?,
                       updated_at = ?, tags = ?, metadata = ?
                WHERE id = ?
            """, (
                test_case.name, test_case.description, test_case.resource_type, test_case.resource_id,
                test_case.language, test_case.code, test_case.input_data, test_case.expected_output,
                test_case.test_type, test_case.updated_at.isoformat(), json.dumps(test_case.tags),
                json.dumps(test_case.metadata), test_case.id,
            ))
        
        return test_case
    
    def delete_test_case(self, test_case_id: str) -> bool:
        """Delete a test case."""
        with self._get_connection() as conn:
            result = conn.execute("DELETE FROM test_cases WHERE id = ?", (test_case_id,))
            return result.rowcount > 0
    
    def _row_to_test_case(self, row) -> TestCase:
        """Convert a database row to a TestCase."""
        return TestCase(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            resource_type=row["resource_type"],
            resource_id=row["resource_id"],
            language=row["language"],
            code=row["code"],
            input_data=row["input_data"],
            expected_output=row["expected_output"],
            test_type=row["test_type"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
        )
    
    def create_test_suite(self, name: str, resource_type: str, **kwargs) -> TestSuite:
        """Create a new test suite."""
        test_suite = TestSuite(
            id=str(uuid.uuid4()),
            name=name,
            description=kwargs.get("description", ""),
            resource_type=resource_type,
            resource_id=kwargs.get("resource_id"),
            test_ids=kwargs.get("test_ids", []),
            tags=kwargs.get("tags", []),
            metadata=kwargs.get("metadata", {}),
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO test_suites (id, name, description, resource_type, resource_id,
                                        test_ids, created_at, updated_at, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_suite.id, test_suite.name, test_suite.description, test_suite.resource_type,
                test_suite.resource_id, json.dumps(test_suite.test_ids),
                test_suite.created_at.isoformat(), test_suite.updated_at.isoformat(),
                json.dumps(test_suite.tags), json.dumps(test_suite.metadata),
            ))
        
        return test_suite
    
    def get_test_suite(self, test_suite_id: str) -> Optional[TestSuite]:
        """Get a test suite by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM test_suites WHERE id = ?", (test_suite_id,)
            ).fetchone()
            
            if row is None:
                return None
            return self._row_to_test_suite(row)
    
    def list_test_suites(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[List[TestSuite], int]:
        """List test suites with optional filtering."""
        offset = (page - 1) * limit
        conditions = []
        params = []
        
        if resource_type:
            conditions.append("resource_type = ?")
            params.append(resource_type)
        if resource_id:
            conditions.append("resource_id = ?")
            params.append(resource_id)
        if search:
            conditions.append("(name LIKE ? OR description LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self._get_connection() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM test_suites WHERE {where_clause}", params
            ).fetchone()[0]
            
            rows = conn.execute(
                f"SELECT * FROM test_suites WHERE {where_clause} ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                params + [limit, offset]
            ).fetchall()
            
            return [self._row_to_test_suite(row) for row in rows], total
    
    def update_test_suite(self, test_suite_id: str, **kwargs) -> Optional[TestSuite]:
        """Update a test suite."""
        test_suite = self.get_test_suite(test_suite_id)
        if test_suite is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(test_suite, key):
                setattr(test_suite, key, value)
        test_suite.updated_at = datetime.utcnow()
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE test_suites SET name = ?, description = ?, resource_type = ?, resource_id = ?,
                       test_ids = ?, updated_at = ?, tags = ?, metadata = ?
                WHERE id = ?
            """, (
                test_suite.name, test_suite.description, test_suite.resource_type,
                test_suite.resource_id, json.dumps(test_suite.test_ids),
                test_suite.updated_at.isoformat(), json.dumps(test_suite.tags),
                json.dumps(test_suite.metadata), test_suite.id,
            ))
        
        return test_suite
    
    def delete_test_suite(self, test_suite_id: str) -> bool:
        """Delete a test suite."""
        with self._get_connection() as conn:
            result = conn.execute("DELETE FROM test_suites WHERE id = ?", (test_suite_id,))
            return result.rowcount > 0
    
    def _row_to_test_suite(self, row) -> TestSuite:
        """Convert a database row to a TestSuite."""
        return TestSuite(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            resource_type=row["resource_type"],
            resource_id=row["resource_id"],
            test_ids=json.loads(row["test_ids"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
        )
    
    def create_test_run(self, **kwargs) -> TestRun:
        """Create a new test run."""
        test_run = TestRun(
            id=str(uuid.uuid4()),
            run_name=kwargs.get("run_name", ""),
            test_case_id=kwargs.get("test_case_id"),
            suite_id=kwargs.get("suite_id"),
            resource_type=kwargs.get("resource_type"),
            resource_id=kwargs.get("resource_id"),
            status=kwargs.get("status", "pending"),
            sandbox_enabled=kwargs.get("sandbox_enabled", True),
            tracking_enabled=kwargs.get("tracking_enabled", False),
            agent_eval_enabled=kwargs.get("agent_eval_enabled", False),
            rl_metrics_enabled=kwargs.get("rl_metrics_enabled", False),
            evaluation_provider=kwargs.get("evaluation_provider"),
            evaluation_model=kwargs.get("evaluation_model"),
            evaluation_endpoint=kwargs.get("evaluation_endpoint"),
            evaluation_hf_execution_mode=kwargs.get("evaluation_hf_execution_mode"),
            dataset_id=kwargs.get("dataset_id"),
            input_data=kwargs.get("input_data", ""),
            output_data=kwargs.get("output_data", ""),
            metrics=kwargs.get("metrics", {}),
            error_message=kwargs.get("error_message"),
            started_at=kwargs.get("started_at"),
            completed_at=kwargs.get("completed_at"),
            duration_seconds=kwargs.get("duration_seconds"),
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO test_runs (id, run_name, test_case_id, suite_id, resource_type, resource_id,
                                      status, sandbox_enabled, tracking_enabled, agent_eval_enabled,
                                      rl_metrics_enabled, evaluation_provider, evaluation_model,
                                      evaluation_endpoint, evaluation_hf_execution_mode, dataset_id,
                                      input_data, output_data, metrics, error_message, started_at,
                                      completed_at, duration_seconds, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_run.id, test_run.run_name, test_run.test_case_id, test_run.suite_id,
                test_run.resource_type, test_run.resource_id, test_run.status,
                int(test_run.sandbox_enabled), int(test_run.tracking_enabled),
                int(test_run.agent_eval_enabled), int(test_run.rl_metrics_enabled),
                test_run.evaluation_provider, test_run.evaluation_model,
                test_run.evaluation_endpoint, test_run.evaluation_hf_execution_mode,
                test_run.dataset_id, test_run.input_data, test_run.output_data,
                json.dumps(test_run.metrics), test_run.error_message,
                test_run.started_at.isoformat() if test_run.started_at else None,
                test_run.completed_at.isoformat() if test_run.completed_at else None,
                test_run.duration_seconds, test_run.created_at.isoformat(),
            ))
        
        return test_run
    
    def get_test_run(self, run_id: str) -> Optional[TestRun]:
        """Get a test run by ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM test_runs WHERE id = ?", (run_id,)).fetchone()
            if row is None:
                return None
            return self._row_to_test_run(row)
    
    def list_test_runs(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[List[TestRun], int]:
        """List test runs with optional filtering."""
        offset = (page - 1) * limit
        conditions = []
        params = []
        
        if resource_type:
            conditions.append("resource_type = ?")
            params.append(resource_type)
        if resource_id:
            conditions.append("resource_id = ?")
            params.append(resource_id)
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self._get_connection() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM test_runs WHERE {where_clause}", params
            ).fetchone()[0]
            
            rows = conn.execute(
                f"SELECT * FROM test_runs WHERE {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                params + [limit, offset]
            ).fetchall()
            
            return [self._row_to_test_run(row) for row in rows], total
    
    def update_test_run(self, run_id: str, **kwargs) -> Optional[TestRun]:
        """Update a test run."""
        test_run = self.get_test_run(run_id)
        if test_run is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(test_run, key):
                setattr(test_run, key, value)
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE test_runs SET run_name = ?, test_case_id = ?, suite_id = ?, resource_type = ?,
                       resource_id = ?, status = ?, sandbox_enabled = ?, tracking_enabled = ?,
                       agent_eval_enabled = ?, rl_metrics_enabled = ?, evaluation_provider = ?,
                       evaluation_model = ?, evaluation_endpoint = ?, evaluation_hf_execution_mode = ?,
                       dataset_id = ?, input_data = ?, output_data = ?, metrics = ?, error_message = ?,
                       started_at = ?, completed_at = ?, duration_seconds = ?
                WHERE id = ?
            """, (
                test_run.run_name, test_run.test_case_id, test_run.suite_id, test_run.resource_type,
                test_run.resource_id, test_run.status, int(test_run.sandbox_enabled),
                int(test_run.tracking_enabled), int(test_run.agent_eval_enabled),
                int(test_run.rl_metrics_enabled), test_run.evaluation_provider,
                test_run.evaluation_model, test_run.evaluation_endpoint,
                test_run.evaluation_hf_execution_mode, test_run.dataset_id, test_run.input_data,
                test_run.output_data, json.dumps(test_run.metrics), test_run.error_message,
                test_run.started_at.isoformat() if test_run.started_at else None,
                test_run.completed_at.isoformat() if test_run.completed_at else None,
                test_run.duration_seconds, test_run.id,
            ))
        
        return test_run
    
    def create_test_result(self, run_id: str, **kwargs) -> TestResult:
        """Create a test result record."""
        result = TestResult(
            id=str(uuid.uuid4()),
            run_id=run_id,
            test_case_id=kwargs.get("test_case_id"),
            name=kwargs.get("name", ""),
            passed=kwargs.get("passed", False),
            status=kwargs.get("status", "failed"),
            output=kwargs.get("output", ""),
            error_message=kwargs.get("error_message"),
            metrics=kwargs.get("metrics", {}),
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO test_results (id, run_id, test_case_id, name, passed, status,
                                         output, error_message, metrics, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.id, result.run_id, result.test_case_id, result.name,
                int(result.passed), result.status, result.output, result.error_message,
                json.dumps(result.metrics), result.created_at.isoformat(),
            ))
        
        return result
    
    def list_test_results(self, run_id: str) -> List[TestResult]:
        """List test results for a run."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM test_results WHERE run_id = ? ORDER BY created_at ASC",
                (run_id,),
            ).fetchall()
            
            return [self._row_to_test_result(row) for row in rows]
    
    def _row_to_test_run(self, row) -> TestRun:
        """Convert a database row to a TestRun."""
        return TestRun(
            id=row["id"],
            run_name=row["run_name"],
            test_case_id=row["test_case_id"],
            suite_id=row["suite_id"],
            resource_type=row["resource_type"],
            resource_id=row["resource_id"],
            status=row["status"],
            sandbox_enabled=bool(row["sandbox_enabled"]),
            tracking_enabled=bool(row["tracking_enabled"]),
            agent_eval_enabled=bool(row["agent_eval_enabled"]),
            rl_metrics_enabled=bool(row["rl_metrics_enabled"]),
            evaluation_provider=row["evaluation_provider"] if "evaluation_provider" in row.keys() else None,
            evaluation_model=row["evaluation_model"] if "evaluation_model" in row.keys() else None,
            evaluation_endpoint=row["evaluation_endpoint"] if "evaluation_endpoint" in row.keys() else None,
            evaluation_hf_execution_mode=row["evaluation_hf_execution_mode"] if "evaluation_hf_execution_mode" in row.keys() else None,
            dataset_id=row["dataset_id"],
            input_data=row["input_data"],
            output_data=row["output_data"],
            metrics=json.loads(row["metrics"]),
            error_message=row["error_message"],
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            duration_seconds=row["duration_seconds"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
    
    def _row_to_test_result(self, row) -> TestResult:
        """Convert a database row to a TestResult."""
        return TestResult(
            id=row["id"],
            run_id=row["run_id"],
            test_case_id=row["test_case_id"],
            name=row["name"],
            passed=bool(row["passed"]),
            status=row["status"],
            output=row["output"],
            error_message=row["error_message"],
            metrics=json.loads(row["metrics"]),
            created_at=datetime.fromisoformat(row["created_at"]),
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
    # DataSources CRUD
    # =========================================================================
    
    def create_datasource(self, name: str, source_type: str, **kwargs) -> DataSource:
        """Create a new data source."""
        datasource = DataSource(
            id=str(uuid.uuid4()),
            name=name,
            source_type=source_type,
            connection_config=kwargs.get("connection_config", "{}"),
            description=kwargs.get("description", ""),
            is_global=kwargs.get("is_global", False),
            project_id=kwargs.get("project_id"),
            status=kwargs.get("status", "active"),
            tags=kwargs.get("tags", []),
            metadata=kwargs.get("metadata", {}),
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO datasources (id, name, source_type, connection_config,
                                        description, is_global, project_id, status,
                                        last_tested, last_test_success,
                                        created_at, updated_at, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datasource.id, datasource.name, datasource.source_type,
                datasource.connection_config, datasource.description,
                1 if datasource.is_global else 0, datasource.project_id,
                datasource.status, None, 0,
                datasource.created_at.isoformat(), datasource.updated_at.isoformat(),
                json.dumps(datasource.tags), json.dumps(datasource.metadata),
            ))
        
        logger.info(f"Created datasource: {name} ({datasource.id})")
        return datasource
    
    def get_datasource(self, datasource_id: str) -> Optional[DataSource]:
        """Get a data source by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM datasources WHERE id = ?", (datasource_id,)
            ).fetchone()
            
            if row is None:
                return None
            
            return self._row_to_datasource(row)
    
    def list_datasources(self, source_type: Optional[str] = None,
                        is_global: Optional[bool] = None,
                        project_id: Optional[str] = None,
                        page: int = 1, limit: int = 50) -> tuple[List[DataSource], int]:
        """List data sources with optional filtering."""
        offset = (page - 1) * limit
        conditions = []
        params = []
        
        if source_type:
            conditions.append("source_type = ?")
            params.append(source_type)
        if is_global is not None:
            conditions.append("is_global = ?")
            params.append(1 if is_global else 0)
        if project_id:
            conditions.append("(project_id = ? OR is_global = 1)")
            params.append(project_id)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self._get_connection() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM datasources WHERE {where_clause}", params
            ).fetchone()[0]
            
            rows = conn.execute(
                f"SELECT * FROM datasources WHERE {where_clause} ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                params + [limit, offset]
            ).fetchall()
            
            return [self._row_to_datasource(row) for row in rows], total
    
    def update_datasource(self, datasource_id: str, **kwargs) -> Optional[DataSource]:
        """Update a data source."""
        datasource = self.get_datasource(datasource_id)
        if datasource is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(datasource, key):
                setattr(datasource, key, value)
        datasource.updated_at = datetime.utcnow()
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE datasources SET name = ?, source_type = ?, connection_config = ?,
                       description = ?, is_global = ?, project_id = ?, status = ?,
                       last_tested = ?, last_test_success = ?,
                       updated_at = ?, tags = ?, metadata = ?
                WHERE id = ?
            """, (
                datasource.name, datasource.source_type, datasource.connection_config,
                datasource.description, 1 if datasource.is_global else 0,
                datasource.project_id, datasource.status,
                datasource.last_tested.isoformat() if datasource.last_tested else None,
                1 if datasource.last_test_success else 0,
                datasource.updated_at.isoformat(),
                json.dumps(datasource.tags), json.dumps(datasource.metadata),
                datasource.id,
            ))
        
        return datasource
    
    def delete_datasource(self, datasource_id: str) -> bool:
        """Delete a data source."""
        with self._get_connection() as conn:
            result = conn.execute("DELETE FROM datasources WHERE id = ?", (datasource_id,))
            return result.rowcount > 0
    
    def _row_to_datasource(self, row) -> DataSource:
        """Convert a database row to a DataSource."""
        return DataSource(
            id=row["id"],
            name=row["name"],
            source_type=row["source_type"],
            connection_config=row["connection_config"],
            description=row["description"],
            is_global=bool(row["is_global"]),
            project_id=row["project_id"],
            status=row["status"],
            last_tested=datetime.fromisoformat(row["last_tested"]) if row["last_tested"] else None,
            last_test_success=bool(row["last_test_success"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
        )
    
    # =========================================================================
    # ServiceResources CRUD
    # =========================================================================
    
    def create_service(self, name: str, service_type: str, **kwargs) -> ServiceResource:
        """Create a new service resource."""
        service = ServiceResource(
            id=str(uuid.uuid4()),
            name=name,
            service_type=service_type,
            endpoint_url=kwargs.get("endpoint_url", ""),
            description=kwargs.get("description", ""),
            health_endpoint=kwargs.get("health_endpoint"),
            auth_type=kwargs.get("auth_type"),
            credentials_ref=kwargs.get("credentials_ref"),
            config_yaml=kwargs.get("config_yaml", ""),
            is_global=kwargs.get("is_global", False),
            project_id=kwargs.get("project_id"),
            status=kwargs.get("status", "unknown"),
            tags=kwargs.get("tags", []),
            metadata=kwargs.get("metadata", {}),
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO services (id, name, service_type, endpoint_url,
                                     description, health_endpoint, auth_type,
                                     credentials_ref, config_yaml, is_global,
                                     project_id, status, last_health_check,
                                     created_at, updated_at, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                service.id, service.name, service.service_type, service.endpoint_url,
                service.description, service.health_endpoint, service.auth_type,
                service.credentials_ref, service.config_yaml,
                1 if service.is_global else 0, service.project_id, service.status, None,
                service.created_at.isoformat(), service.updated_at.isoformat(),
                json.dumps(service.tags), json.dumps(service.metadata),
            ))
        
        logger.info(f"Created service: {name} ({service.id})")
        return service
    
    def get_service(self, service_id: str) -> Optional[ServiceResource]:
        """Get a service by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM services WHERE id = ?", (service_id,)
            ).fetchone()
            
            if row is None:
                return None
            
            return self._row_to_service(row)
    
    def list_services(self, service_type: Optional[str] = None,
                     is_global: Optional[bool] = None,
                     project_id: Optional[str] = None,
                     page: int = 1, limit: int = 50) -> tuple[List[ServiceResource], int]:
        """List services with optional filtering."""
        offset = (page - 1) * limit
        conditions = []
        params = []
        
        if service_type:
            conditions.append("service_type = ?")
            params.append(service_type)
        if is_global is not None:
            conditions.append("is_global = ?")
            params.append(1 if is_global else 0)
        if project_id:
            conditions.append("(project_id = ? OR is_global = 1)")
            params.append(project_id)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self._get_connection() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM services WHERE {where_clause}", params
            ).fetchone()[0]
            
            rows = conn.execute(
                f"SELECT * FROM services WHERE {where_clause} ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                params + [limit, offset]
            ).fetchall()
            
            return [self._row_to_service(row) for row in rows], total
    
    def update_service(self, service_id: str, **kwargs) -> Optional[ServiceResource]:
        """Update a service."""
        service = self.get_service(service_id)
        if service is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(service, key):
                setattr(service, key, value)
        service.updated_at = datetime.utcnow()
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE services SET name = ?, service_type = ?, endpoint_url = ?,
                       description = ?, health_endpoint = ?, auth_type = ?,
                       credentials_ref = ?, config_yaml = ?, is_global = ?,
                       project_id = ?, status = ?, last_health_check = ?,
                       updated_at = ?, tags = ?, metadata = ?
                WHERE id = ?
            """, (
                service.name, service.service_type, service.endpoint_url,
                service.description, service.health_endpoint, service.auth_type,
                service.credentials_ref, service.config_yaml,
                1 if service.is_global else 0, service.project_id, service.status,
                service.last_health_check.isoformat() if service.last_health_check else None,
                service.updated_at.isoformat(),
                json.dumps(service.tags), json.dumps(service.metadata),
                service.id,
            ))
        
        return service
    
    def delete_service(self, service_id: str) -> bool:
        """Delete a service."""
        with self._get_connection() as conn:
            result = conn.execute("DELETE FROM services WHERE id = ?", (service_id,))
            return result.rowcount > 0
    
    def _row_to_service(self, row) -> ServiceResource:
        """Convert a database row to a ServiceResource."""
        return ServiceResource(
            id=row["id"],
            name=row["name"],
            service_type=row["service_type"],
            endpoint_url=row["endpoint_url"],
            description=row["description"],
            health_endpoint=row["health_endpoint"],
            auth_type=row["auth_type"],
            credentials_ref=row["credentials_ref"],
            config_yaml=row["config_yaml"],
            is_global=bool(row["is_global"]),
            project_id=row["project_id"],
            status=row["status"],
            last_health_check=datetime.fromisoformat(row["last_health_check"]) if row["last_health_check"] else None,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
        )
    
    # =========================================================================
    # ProjectResources CRUD
    # =========================================================================
    
    def link_resource_to_project(self, project_id: str, resource_type: str,
                                 resource_id: str, alias: Optional[str] = None,
                                 config_overrides: str = "{}") -> ProjectResource:
        """Link a global resource to a project."""
        pr = ProjectResource(
            id=str(uuid.uuid4()),
            project_id=project_id,
            resource_type=resource_type,
            resource_id=resource_id,
            alias=alias,
            config_overrides=config_overrides,
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO project_resources
                    (id, project_id, resource_type, resource_id, alias, config_overrides, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pr.id, pr.project_id, pr.resource_type, pr.resource_id,
                pr.alias, pr.config_overrides, pr.created_at.isoformat(),
            ))
        
        return pr
    
    def unlink_resource_from_project(self, project_id: str, resource_type: str,
                                     resource_id: str) -> bool:
        """Unlink a resource from a project."""
        with self._get_connection() as conn:
            result = conn.execute("""
                DELETE FROM project_resources
                WHERE project_id = ? AND resource_type = ? AND resource_id = ?
            """, (project_id, resource_type, resource_id))
            return result.rowcount > 0
    
    def get_project_resources(self, project_id: str,
                             resource_type: Optional[str] = None) -> List[ProjectResource]:
        """Get all resources linked to a project."""
        with self._get_connection() as conn:
            if resource_type:
                rows = conn.execute("""
                    SELECT * FROM project_resources
                    WHERE project_id = ? AND resource_type = ?
                """, (project_id, resource_type)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM project_resources WHERE project_id = ?
                """, (project_id,)).fetchall()
            
            return [ProjectResource(
                id=row["id"],
                project_id=row["project_id"],
                resource_type=row["resource_type"],
                resource_id=row["resource_id"],
                alias=row["alias"],
                config_overrides=row["config_overrides"],
                created_at=datetime.fromisoformat(row["created_at"]),
            ) for row in rows]
    
    # =========================================================================
    # IndexingState CRUD
    # =========================================================================
    
    def get_or_create_indexing_state(self, project_id: str,
                                     collection_name: Optional[str] = None) -> IndexingState:
        """Get or create indexing state for a project."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM indexing_states WHERE project_id = ?", (project_id,)
            ).fetchone()
            
            if row:
                return self._row_to_indexing_state(row)
            
            # Create new state
            state = IndexingState(
                id=str(uuid.uuid4()),
                project_id=project_id,
                collection_name=collection_name or f"project-{project_id}",
            )
            
            conn.execute("""
                INSERT INTO indexing_states
                    (id, project_id, collection_name, version, status,
                     file_count, chunk_count, last_indexed, error_message,
                     indexing_config, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state.id, state.project_id, state.collection_name, state.version,
                state.status, state.file_count, state.chunk_count,
                state.last_indexed.isoformat() if state.last_indexed else None,
                state.error_message, state.indexing_config,
                state.created_at.isoformat(), state.updated_at.isoformat(),
            ))
            
            return state
    
    def update_indexing_state(self, project_id: str, **kwargs) -> Optional[IndexingState]:
        """Update indexing state for a project."""
        state = self.get_or_create_indexing_state(project_id)
        
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)
        state.updated_at = datetime.utcnow()
        
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE indexing_states SET collection_name = ?, version = ?,
                       status = ?, file_count = ?, chunk_count = ?,
                       last_indexed = ?, error_message = ?, indexing_config = ?,
                       updated_at = ?
                WHERE project_id = ?
            """, (
                state.collection_name, state.version, state.status,
                state.file_count, state.chunk_count,
                state.last_indexed.isoformat() if state.last_indexed else None,
                state.error_message, state.indexing_config,
                state.updated_at.isoformat(), project_id,
            ))
        
        return state
    
    def _row_to_indexing_state(self, row) -> IndexingState:
        """Convert a database row to an IndexingState."""
        return IndexingState(
            id=row["id"],
            project_id=row["project_id"],
            collection_name=row["collection_name"],
            version=row["version"],
            status=row["status"],
            file_count=row["file_count"],
            chunk_count=row["chunk_count"],
            last_indexed=datetime.fromisoformat(row["last_indexed"]) if row["last_indexed"] else None,
            error_message=row["error_message"],
            indexing_config=row["indexing_config"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
    
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
            test_cases = conn.execute("SELECT COUNT(*) FROM test_cases").fetchone()[0]
            test_runs = conn.execute("SELECT COUNT(*) FROM test_runs").fetchone()[0]
            datasources = conn.execute("SELECT COUNT(*) FROM datasources").fetchone()[0]
            services = conn.execute("SELECT COUNT(*) FROM services").fetchone()[0]
            indexed_projects = conn.execute(
                "SELECT COUNT(*) FROM indexing_states WHERE status = 'completed'"
            ).fetchone()[0]
            
            return {
                "projects_count": projects,
                "agents_count": agents,
                "flows_count": flows,
                "components_count": components,
                "test_cases_count": test_cases,
                "test_runs_count": test_runs,
                "datasources_count": datasources,
                "services_count": services,
                "indexed_projects_count": indexed_projects,
                "experiments_count": 0,  # Will be populated from MLFlow
                "active_sessions": 0,  # Will be populated from sessions
            }

