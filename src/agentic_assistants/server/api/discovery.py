"""
REST API endpoints for data source discovery.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agentic_assistants.datasources import DataSourceRegistry
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/datasources", tags=["datasources"])


class DataSourceRegistrationRequest(BaseModel):
    """Request to register a data source."""
    name: str
    source_type: str
    connection_config: Dict[str, Any]
    description: str = ""
    is_global: bool = False
    project_id: Optional[str] = None


class DiscoveryRequest(BaseModel):
    """Request to discover data sources."""
    provider: Optional[str] = None  # aws, gcp, azure, local
    base_dir: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None


@router.post("/register")
async def register_datasource(request: DataSourceRegistrationRequest):
    """
    Register a new data source.
    
    Args:
        request: Registration request
        
    Returns:
        Created data source
    """
    registry = DataSourceRegistry()
    
    datasource = registry.register(
        name=request.name,
        source_type=request.source_type,
        connection_config=request.connection_config,
        description=request.description,
        is_global=request.is_global,
        project_id=request.project_id,
    )
    
    return datasource.to_dict()


@router.post("/discover")
async def discover_datasources(request: DiscoveryRequest):
    """
    Discover available data sources.
    
    Args:
        request: Discovery request
        
    Returns:
        List of discovered sources
    """
    registry = DataSourceRegistry()
    
    if request.provider == "local" or not request.provider:
        base_dir = Path(request.base_dir) if request.base_dir else None
        discovered = registry.discover_local(base_dir=base_dir)
    else:
        discovered = registry.discover_cloud(
            provider=request.provider,
            credentials=request.credentials,
        )
    
    return {"discovered": discovered}


@router.get("/{datasource_id}/test")
async def test_datasource(datasource_id: str):
    """
    Test connection to a data source.
    
    Args:
        datasource_id: Data source ID
        
    Returns:
        Test result
    """
    registry = DataSourceRegistry()
    
    try:
        success = registry.test_connection(datasource_id)
        
        return {
            "datasource_id": datasource_id,
            "success": success,
            "message": "Connection successful" if success else "Connection failed",
        }
    except Exception as e:
        raise HTTPException(500, f"Test failed: {str(e)}")
