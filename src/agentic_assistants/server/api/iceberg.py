"""
Iceberg REST API router for browsing and managing Iceberg tables.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["iceberg"])


# -- Request / Response models ------------------------------------------------

class CreateNamespaceRequest(BaseModel):
    namespace: str
    properties: Optional[Dict[str, str]] = None


class SchemaFieldDef(BaseModel):
    name: str
    type: str = "string"
    required: bool = False


class CreateTableRequest(BaseModel):
    namespace: str
    table: str
    schema_fields: List[SchemaFieldDef]


class TableMetadataResponse(BaseModel):
    table_uuid: str = ""
    location: str = ""
    format_version: int = 1
    schema_: List[Dict[str, Any]] = Field(default_factory=list, alias="schema")
    snapshot_count: int = 0
    partition_specs: List[Dict[str, Any]] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)


# -- Helpers -------------------------------------------------------------------

def _get_client():
    from agentic_assistants.integrations.iceberg import get_iceberg_client
    return get_iceberg_client()


# -- Endpoints ----------------------------------------------------------------

@router.get("/namespaces")
async def list_namespaces():
    try:
        client = _get_client()
        return {"namespaces": client.list_namespaces()}
    except Exception as e:
        logger.error("Failed to list Iceberg namespaces: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/namespaces")
async def create_namespace(req: CreateNamespaceRequest):
    try:
        client = _get_client()
        client.create_namespace(req.namespace, req.properties)
        return {"status": "created", "namespace": req.namespace}
    except Exception as e:
        logger.error("Failed to create namespace: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables")
async def list_tables(namespace: str = Query("default")):
    try:
        client = _get_client()
        return {"tables": client.list_tables(namespace)}
    except Exception as e:
        logger.error("Failed to list Iceberg tables: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tables")
async def create_table(req: CreateTableRequest):
    try:
        client = _get_client()
        tbl = client.create_table(
            req.namespace,
            req.table,
            [f.model_dump() for f in req.schema_fields],
        )
        return {
            "status": "created",
            "table": f"{req.namespace}.{req.table}",
            "location": str(getattr(tbl.metadata, "location", "")),
        }
    except Exception as e:
        logger.error("Failed to create Iceberg table: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/{namespace}/{table}")
async def get_table_metadata(namespace: str, table: str):
    try:
        client = _get_client()
        return client.table_metadata(namespace, table)
    except Exception as e:
        logger.error("Failed to get table metadata: %s", e)
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/tables/{namespace}/{table}/schema")
async def get_table_schema(namespace: str, table: str):
    try:
        client = _get_client()
        return {"schema": client.get_table_schema(namespace, table)}
    except Exception as e:
        logger.error("Failed to get table schema: %s", e)
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/tables/{namespace}/{table}/snapshots")
async def get_table_snapshots(namespace: str, table: str):
    try:
        client = _get_client()
        return {"snapshots": client.get_snapshots(namespace, table)}
    except Exception as e:
        logger.error("Failed to get snapshots: %s", e)
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/tables/{namespace}/{table}/preview")
async def preview_table(
    namespace: str, table: str, limit: int = Query(50, ge=1, le=1000)
):
    try:
        client = _get_client()
        return client.preview_table(namespace, table, limit=limit)
    except Exception as e:
        logger.error("Failed to preview table: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
