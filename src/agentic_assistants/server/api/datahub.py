"""
DataHub catalog REST API router for search, datasets, lineage, and ingestion.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["catalog"])


# -- Request / Response models ------------------------------------------------

class IngestRequest(BaseModel):
    recipe: Dict[str, Any]


# -- Helpers -------------------------------------------------------------------

def _get_client():
    from agentic_assistants.integrations.datahub import get_datahub_client
    return get_datahub_client()


# -- Endpoints ----------------------------------------------------------------

@router.get("/search")
async def search_catalog(
    q: str = Query(..., description="Search query"),
    entity_type: str = Query("dataset"),
    start: int = Query(0, ge=0),
    count: int = Query(20, ge=1, le=100),
    platform: Optional[str] = Query(None),
):
    try:
        client = _get_client()
        filters = {}
        if platform:
            filters["platform"] = f"urn:li:dataPlatform:{platform}"
        result = await client.search(
            query=q,
            entity_type=entity_type,
            start=start,
            count=count,
            filters=filters or None,
        )
        return result
    except Exception as e:
        logger.error("Catalog search failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets")
async def list_datasets(
    start: int = Query(0, ge=0),
    count: int = Query(50, ge=1, le=200),
    platform: Optional[str] = Query(None),
):
    try:
        client = _get_client()
        return await client.list_datasets(start=start, count=count, platform=platform)
    except Exception as e:
        logger.error("Failed to list datasets: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{urn:path}")
async def get_dataset(urn: str):
    try:
        client = _get_client()
        return await client.get_dataset(urn)
    except Exception as e:
        logger.error("Failed to get dataset %s: %s", urn, e)
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/lineage/{urn:path}")
async def get_lineage(
    urn: str,
    direction: str = Query("DOWNSTREAM"),
    max_hops: int = Query(3, ge=1, le=10),
):
    try:
        client = _get_client()
        return await client.get_lineage(urn, direction=direction, max_hops=max_hops)
    except Exception as e:
        logger.error("Failed to get lineage for %s: %s", urn, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/domains")
async def list_domains():
    try:
        client = _get_client()
        return await client.list_domains()
    except Exception as e:
        logger.error("Failed to list domains: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/glossary")
async def list_glossary_terms():
    try:
        client = _get_client()
        return await client.list_glossary_terms()
    except Exception as e:
        logger.error("Failed to list glossary terms: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
async def run_ingestion(req: IngestRequest):
    try:
        client = _get_client()
        return await client.run_ingestion(req.recipe)
    except Exception as e:
        logger.error("Ingestion failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def catalog_stats():
    try:
        client = _get_client()
        return await client.get_stats()
    except Exception as e:
        logger.error("Failed to get catalog stats: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def catalog_health():
    try:
        client = _get_client()
        return await client.health()
    except Exception as e:
        logger.error("DataHub health check failed: %s", e)
        raise HTTPException(status_code=503, detail=str(e))


# -- Registration endpoints for Knowledge Bases & Document Stores ---------------

class RegisterKBRequest(BaseModel):
    name: str
    description: Optional[str] = None
    platform: str = "vectordb"
    tags: list[str] = []


class RegisterDocStoreRequest(BaseModel):
    store_id: str
    name: str
    description: Optional[str] = None
    platform: str = "vectordb"
    ttl_hours: Optional[int] = None


class UpdateLineageRequest(BaseModel):
    upstream_urn: str
    downstream_urn: str


@router.post("/register/kb")
async def register_knowledge_base(request: RegisterKBRequest):
    """Register a knowledge base as a DataHub dataset entity for tracking."""
    try:
        client = _get_client()
        result = await client.register_knowledge_base(
            name=request.name,
            description=request.description or "",
            platform=request.platform,
            tags=request.tags,
        )
        return result
    except Exception as e:
        logger.error("Failed to register KB in DataHub: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register/docstore")
async def register_document_store(request: RegisterDocStoreRequest):
    """Register a document store as a DataHub dataset entity for tracking."""
    try:
        client = _get_client()
        result = await client.register_document_store(
            store_id=request.store_id,
            name=request.name,
            description=request.description or "",
            platform=request.platform,
            ttl_hours=request.ttl_hours,
        )
        return result
    except Exception as e:
        logger.error("Failed to register DocStore in DataHub: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lineage")
async def update_lineage(request: UpdateLineageRequest):
    """Record lineage between two DataHub entities."""
    try:
        client = _get_client()
        result = await client.update_lineage(
            upstream_urn=request.upstream_urn,
            downstream_urn=request.downstream_urn,
        )
        return result
    except Exception as e:
        logger.error("Failed to update lineage: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
