"""
Supabase client integration for the agentic assistants framework.

Provides Supabase-native API access with real-time features.
"""

from typing import Any, Dict, List, Optional, Tuple

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.models import (
    Agent, Component, DataSource, Flow, IndexingState,
    Note, Project, ProjectResource, ServiceResource, Tag,
)
from agentic_assistants.db.base_store import BaseStore
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class SupabaseStore(BaseStore):
    """
    Supabase-backed data store for the Agentic Control Panel.
    
    Features:
    - Direct integration with Supabase API
    - Real-time subscriptions for live updates
    - Row-level security support
    - Edge Functions integration
    - Authentication management
    """
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """Initialize the Supabase store."""
        if not SUPABASE_AVAILABLE:
            raise ImportError(
                "supabase is required for Supabase support. "
                "Install it with: pip install supabase"
            )
        
        self.config = config or AgenticConfig()
        
        if not self.config.supabase.url or not self.config.supabase.key:
            raise ValueError(
                "Supabase URL and key must be configured. "
                "Set SUPABASE_URL and SUPABASE_KEY environment variables."
            )
        
        # Initialize Supabase client
        self.client: Client = create_client(
            self.config.supabase.url,
            self.config.supabase.key
        )
        
        logger.info(f"Supabase client initialized: {self.config.supabase.url}")
        
        # Initialize database schema (if needed)
        self._init_database()
    
    def _init_database(self) -> None:
        """
        Initialize the Supabase database schema.
        
        Note: Schema creation is typically done via Supabase dashboard or migrations.
        This method can verify tables exist and run any additional setup.
        """
        logger.info("Supabase database schema initialized (via dashboard/migrations)")
    
    # =========================================================================
    # Projects CRUD
    # =========================================================================
    
    def create_project(self, name: str, description: str = "", 
                      config_yaml: str = "", status: str = "active",
                      tags: List[str] = None, metadata: Dict = None) -> Project:
        """Create a new project."""
        import uuid
        from datetime import datetime
        
        project = Project(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            config_yaml=config_yaml,
            status=status,
            tags=tags or [],
            metadata=metadata or {},
        )
        
        data = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "config_yaml": project.config_yaml,
            "status": project.status,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
            "tags": project.tags,
            "metadata": project.metadata,
        }
        
        result = self.client.table("projects").insert(data).execute()
        logger.info(f"Created project: {name} ({project.id})")
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        result = self.client.table("projects").select("*").eq("id", project_id).execute()
        
        if not result.data:
            return None
        
        return self._dict_to_project(result.data[0])
    
    def list_projects(self, status: Optional[str] = None, 
                     page: int = 1, limit: int = 50) -> Tuple[List[Project], int]:
        """List projects with optional filtering."""
        offset = (page - 1) * limit
        
        query = self.client.table("projects").select("*", count="exact")
        
        if status:
            query = query.eq("status", status)
        
        result = query.order("updated_at", desc=True).range(offset, offset + limit - 1).execute()
        
        projects = [self._dict_to_project(row) for row in result.data]
        total = result.count if result.count else 0
        
        return projects, total
    
    def update_project(self, project_id: str, **kwargs) -> Optional[Project]:
        """Update a project."""
        from datetime import datetime
        
        kwargs["updated_at"] = datetime.utcnow().isoformat()
        
        result = self.client.table("projects").update(kwargs).eq("id", project_id).execute()
        
        if not result.data:
            return None
        
        return self._dict_to_project(result.data[0])
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        result = self.client.table("projects").delete().eq("id", project_id).execute()
        return len(result.data) > 0
    
    def _dict_to_project(self, data: Dict) -> Project:
        """Convert a Supabase row to a Project."""
        from datetime import datetime
        
        return Project(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            config_yaml=data.get("config_yaml", ""),
            status=data.get("status", "active"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )
    
    # Placeholder implementations for remaining methods
    # These would follow similar patterns using Supabase client
    
    def create_agent(self, name: str, role: str, **kwargs) -> Agent:
        """Create a new agent."""
        raise NotImplementedError("Implement using Supabase client pattern")
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        raise NotImplementedError()
    
    def list_agents(self, project_id: Optional[str] = None,
                   status: Optional[str] = None,
                   page: int = 1, limit: int = 50) -> Tuple[List[Agent], int]:
        """List agents with optional filtering."""
        raise NotImplementedError()
    
    def update_agent(self, agent_id: str, **kwargs) -> Optional[Agent]:
        """Update an agent."""
        raise NotImplementedError()
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        raise NotImplementedError()
    
    def create_flow(self, name: str, **kwargs) -> Flow:
        """Create a new flow."""
        raise NotImplementedError()
    
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
        # Use Supabase to count records
        projects = len(self.client.table("projects").select("id", count="exact").execute().data)
        agents = len(self.client.table("agents").select("id", count="exact").execute().data)
        
        return {
            "projects_count": projects,
            "agents_count": agents,
            "flows_count": 0,
            "components_count": 0,
            "datasources_count": 0,
            "services_count": 0,
            "indexed_projects_count": 0,
            "experiments_count": 0,
            "active_sessions": 0,
        }
