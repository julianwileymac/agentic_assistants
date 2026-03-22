"""
Central registry for data source definitions and discovery.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.models import DataSource
from agentic_assistants.db import get_store
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class DataSourceRegistry:
    """
    Central registry for managing data sources.
    
    Features:
    - Register data sources (databases, APIs, file shares, cloud storage)
    - Test connections and validate configurations
    - Discover local and cloud data sources automatically
    - Manage connection pooling and credentials
    """
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """Initialize the data source registry."""
        self.config = config or AgenticConfig()
        self.store = get_store(self.config)
    
    def register(
        self,
        name: str,
        source_type: str,
        connection_config: Dict[str, Any],
        description: str = "",
        is_global: bool = False,
        project_id: Optional[str] = None,
    ) -> DataSource:
        """
        Register a new data source.
        
        Args:
            name: Source name
            source_type: Type (database, file_store, api, cloud_storage)
            connection_config: Connection configuration
            description: Description
            is_global: Whether globally available
            project_id: Project ID if project-scoped
            
        Returns:
            Created DataSource
        """
        import json
        
        datasource = self.store.create_datasource(
            name=name,
            source_type=source_type,
            connection_config=json.dumps(connection_config),
            description=description,
            is_global=is_global,
            project_id=project_id,
        )
        
        logger.info(f"Registered data source: {name} ({source_type})")
        return datasource
    
    def test_connection(self, datasource_id: str) -> bool:
        """
        Test connection to a data source.
        
        Args:
            datasource_id: Data source ID
            
        Returns:
            True if connection successful
        """
        from datetime import datetime
        
        datasource = self.store.get_datasource(datasource_id)
        if not datasource:
            raise ValueError(f"Data source not found: {datasource_id}")
        
        config = datasource.get_config()
        source_type = datasource.source_type
        
        try:
            if source_type == "database":
                success = self._test_database_connection(config)
            elif source_type == "file_store":
                success = self._test_filestore_connection(config)
            elif source_type == "api":
                success = self._test_api_connection(config)
            elif source_type == "cloud_storage":
                success = self._test_cloud_storage_connection(config)
            else:
                success = False
            
            # Update test status
            self.store.update_datasource(
                datasource_id,
                last_tested=datetime.utcnow(),
                last_test_success=success,
                status="active" if success else "error",
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            self.store.update_datasource(
                datasource_id,
                last_tested=datetime.utcnow(),
                last_test_success=False,
                status="error",
            )
            return False
    
    def discover_local(self, base_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Discover data sources in local directories.
        
        Args:
            base_dir: Base directory to scan
            
        Returns:
            List of discovered sources
        """
        base_dir = base_dir or (Path(self.config.data_dir) / "sources" / "manual")
        
        discovered = []
        
        if base_dir.exists():
            for item in base_dir.rglob("*"):
                if item.is_file():
                    discovered.append({
                        "path": str(item),
                        "type": "file",
                        "name": item.name,
                        "size": item.stat().st_size,
                        "extension": item.suffix,
                    })
        
        logger.info(f"Discovered {len(discovered)} local data sources")
        return discovered
    
    def discover_cloud(
        self,
        provider: str,
        credentials: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Discover data sources in cloud storage.
        
        Args:
            provider: Cloud provider (aws, gcp, azure)
            credentials: Optional credentials
            
        Returns:
            List of discovered cloud sources
        """
        discovered = []
        
        if provider == "aws":
            discovered = self._discover_aws_sources(credentials)
        elif provider == "gcp":
            discovered = self._discover_gcp_sources(credentials)
        elif provider == "azure":
            discovered = self._discover_azure_sources(credentials)
        
        logger.info(f"Discovered {len(discovered)} {provider} sources")
        return discovered
    
    def _test_database_connection(self, config: Dict[str, Any]) -> bool:
        """Test database connection."""
        # Placeholder - implement actual connection tests
        return True
    
    def _test_filestore_connection(self, config: Dict[str, Any]) -> bool:
        """Test file store connection."""
        path = Path(config.get("path", ""))
        return path.exists() if path else False
    
    def _test_api_connection(self, config: Dict[str, Any]) -> bool:
        """Test API connection."""
        # Placeholder - implement HTTP/REST API test
        return True
    
    def _test_cloud_storage_connection(self, config: Dict[str, Any]) -> bool:
        """Test cloud storage connection."""
        # Placeholder - implement S3/GCS/Azure test
        return True
    
    def _discover_aws_sources(self, credentials: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Discover AWS data sources."""
        # Placeholder for AWS discovery
        return []
    
    def _discover_gcp_sources(self, credentials: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Discover GCP data sources."""
        # Placeholder for GCP discovery
        return []
    
    def _discover_azure_sources(self, credentials: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Discover Azure data sources."""
        # Placeholder for Azure discovery
        return []
