"""
Base store interface for database abstraction.

Provides a common interface for different database backends
(SQLite, PostgreSQL, Supabase) to enable seamless switching.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

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


class BaseStore(ABC):
    """
    Abstract base class for database stores.
    
    Defines the common interface that all store implementations must provide.
    """
    
    @abstractmethod
    def _init_database(self) -> None:
        """Initialize the database schema."""
        pass
    
    # =========================================================================
    # Projects
    # =========================================================================
    
    @abstractmethod
    def create_project(self, name: str, description: str = "", 
                      config_yaml: str = "", status: str = "active",
                      tags: List[str] = None, metadata: Dict = None) -> Project:
        """Create a new project."""
        pass
    
    @abstractmethod
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        pass
    
    @abstractmethod
    def list_projects(self, status: Optional[str] = None, 
                     page: int = 1, limit: int = 50) -> Tuple[List[Project], int]:
        """List projects with optional filtering."""
        pass
    
    @abstractmethod
    def update_project(self, project_id: str, **kwargs) -> Optional[Project]:
        """Update a project."""
        pass
    
    @abstractmethod
    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        pass
    
    # =========================================================================
    # Agents
    # =========================================================================
    
    @abstractmethod
    def create_agent(self, name: str, role: str, **kwargs) -> Agent:
        """Create a new agent."""
        pass
    
    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        pass
    
    @abstractmethod
    def list_agents(self, project_id: Optional[str] = None,
                   status: Optional[str] = None,
                   page: int = 1, limit: int = 50) -> Tuple[List[Agent], int]:
        """List agents with optional filtering."""
        pass
    
    @abstractmethod
    def update_agent(self, agent_id: str, **kwargs) -> Optional[Agent]:
        """Update an agent."""
        pass
    
    @abstractmethod
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        pass
    
    # =========================================================================
    # Flows
    # =========================================================================
    
    @abstractmethod
    def create_flow(self, name: str, **kwargs) -> Flow:
        """Create a new flow."""
        pass
    
    @abstractmethod
    def get_flow(self, flow_id: str) -> Optional[Flow]:
        """Get a flow by ID."""
        pass
    
    @abstractmethod
    def list_flows(self, project_id: Optional[str] = None,
                  status: Optional[str] = None,
                  page: int = 1, limit: int = 50) -> Tuple[List[Flow], int]:
        """List flows with optional filtering."""
        pass
    
    @abstractmethod
    def update_flow(self, flow_id: str, **kwargs) -> Optional[Flow]:
        """Update a flow."""
        pass
    
    @abstractmethod
    def delete_flow(self, flow_id: str) -> bool:
        """Delete a flow."""
        pass
    
    # =========================================================================
    # Components
    # =========================================================================
    
    @abstractmethod
    def create_component(self, name: str, category: str, **kwargs) -> Component:
        """Create a new component."""
        pass
    
    @abstractmethod
    def get_component(self, component_id: str) -> Optional[Component]:
        """Get a component by ID."""
        pass
    
    @abstractmethod
    def list_components(self, category: Optional[str] = None,
                       search: Optional[str] = None,
                       page: int = 1, limit: int = 50) -> Tuple[List[Component], int]:
        """List components with optional filtering."""
        pass
    
    @abstractmethod
    def update_component(self, component_id: str, **kwargs) -> Optional[Component]:
        """Update a component."""
        pass
    
    @abstractmethod
    def delete_component(self, component_id: str) -> bool:
        """Delete a component."""
        pass
    
    # =========================================================================
    # Notes
    # =========================================================================
    
    @abstractmethod
    def create_note(self, resource_type: str, resource_id: str, 
                   content: str) -> Note:
        """Create a new note."""
        pass
    
    @abstractmethod
    def get_notes(self, resource_type: str, resource_id: str) -> List[Note]:
        """Get notes for a resource."""
        pass
    
    @abstractmethod
    def update_note(self, note_id: str, content: str) -> Optional[Note]:
        """Update a note."""
        pass
    
    @abstractmethod
    def delete_note(self, note_id: str) -> bool:
        """Delete a note."""
        pass
    
    # =========================================================================
    # Tags
    # =========================================================================
    
    @abstractmethod
    def get_or_create_tag(self, name: str, color: str = "#6366f1") -> Tag:
        """Get or create a tag by name."""
        pass
    
    @abstractmethod
    def list_tags(self) -> List[Tag]:
        """List all tags with resource counts."""
        pass
    
    @abstractmethod
    def add_tag_to_resource(self, resource_type: str, resource_id: str, 
                           tag_name: str) -> bool:
        """Add a tag to a resource."""
        pass
    
    @abstractmethod
    def remove_tag_from_resource(self, resource_type: str, resource_id: str,
                                tag_name: str) -> bool:
        """Remove a tag from a resource."""
        pass
    
    # =========================================================================
    # DataSources
    # =========================================================================
    
    @abstractmethod
    def create_datasource(self, name: str, source_type: str, **kwargs) -> DataSource:
        """Create a new data source."""
        pass
    
    @abstractmethod
    def get_datasource(self, datasource_id: str) -> Optional[DataSource]:
        """Get a data source by ID."""
        pass
    
    @abstractmethod
    def list_datasources(self, source_type: Optional[str] = None,
                        is_global: Optional[bool] = None,
                        project_id: Optional[str] = None,
                        page: int = 1, limit: int = 50) -> Tuple[List[DataSource], int]:
        """List data sources with optional filtering."""
        pass
    
    @abstractmethod
    def update_datasource(self, datasource_id: str, **kwargs) -> Optional[DataSource]:
        """Update a data source."""
        pass
    
    @abstractmethod
    def delete_datasource(self, datasource_id: str) -> bool:
        """Delete a data source."""
        pass
    
    # =========================================================================
    # ServiceResources
    # =========================================================================
    
    @abstractmethod
    def create_service(self, name: str, service_type: str, **kwargs) -> ServiceResource:
        """Create a new service resource."""
        pass
    
    @abstractmethod
    def get_service(self, service_id: str) -> Optional[ServiceResource]:
        """Get a service by ID."""
        pass
    
    @abstractmethod
    def list_services(self, service_type: Optional[str] = None,
                     is_global: Optional[bool] = None,
                     project_id: Optional[str] = None,
                     page: int = 1, limit: int = 50) -> Tuple[List[ServiceResource], int]:
        """List services with optional filtering."""
        pass
    
    @abstractmethod
    def update_service(self, service_id: str, **kwargs) -> Optional[ServiceResource]:
        """Update a service."""
        pass
    
    @abstractmethod
    def delete_service(self, service_id: str) -> bool:
        """Delete a service."""
        pass
    
    # =========================================================================
    # ProjectResources
    # =========================================================================
    
    @abstractmethod
    def link_resource_to_project(self, project_id: str, resource_type: str,
                                 resource_id: str, alias: Optional[str] = None,
                                 config_overrides: str = "{}") -> ProjectResource:
        """Link a global resource to a project."""
        pass
    
    @abstractmethod
    def unlink_resource_from_project(self, project_id: str, resource_type: str,
                                     resource_id: str) -> bool:
        """Unlink a resource from a project."""
        pass
    
    @abstractmethod
    def get_project_resources(self, project_id: str,
                             resource_type: Optional[str] = None) -> List[ProjectResource]:
        """Get all resources linked to a project."""
        pass
    
    # =========================================================================
    # IndexingState
    # =========================================================================
    
    @abstractmethod
    def get_or_create_indexing_state(self, project_id: str,
                                     collection_name: Optional[str] = None) -> IndexingState:
        """Get or create indexing state for a project."""
        pass
    
    @abstractmethod
    def update_indexing_state(self, project_id: str, **kwargs) -> Optional[IndexingState]:
        """Update indexing state for a project."""
        pass
    
    # =========================================================================
    # Stats
    # =========================================================================
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        pass


def get_store(config: Optional[Any] = None) -> BaseStore:
    """
    Factory function to get the appropriate store based on configuration.
    
    Args:
        config: AgenticConfig instance
        
    Returns:
        BaseStore implementation (SQLite, PostgreSQL, or Supabase)
    """
    from agentic_assistants.config import AgenticConfig
    from agentic_assistants.core.models import ControlPanelStore
    
    if config is None:
        config = AgenticConfig()
    
    db_type = config.database.type.lower()
    
    if db_type == "sqlite":
        # Use existing SQLite store
        return ControlPanelStore(config)
    elif db_type == "postgres" or db_type == "postgresql":
        # Use PostgreSQL store
        from agentic_assistants.db.postgres_store import PostgreSQLStore
        return PostgreSQLStore(config)
    elif db_type == "supabase":
        # Use Supabase store
        from agentic_assistants.db.supabase_client import SupabaseStore
        return SupabaseStore(config)
    else:
        raise ValueError(f"Unknown database type: {db_type}. Must be one of: sqlite, postgres, supabase")
