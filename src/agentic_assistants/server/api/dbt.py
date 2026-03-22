"""
dbt REST API router for model management, execution, and metadata.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["dbt"])


# -- Request models -----------------------------------------------------------

class DbtRunRequest(BaseModel):
    select: Optional[str] = None
    exclude: Optional[str] = None
    full_refresh: bool = False


class DbtTestRequest(BaseModel):
    select: Optional[str] = None


# -- Helpers -------------------------------------------------------------------

def _get_client():
    from agentic_assistants.integrations.dbt import get_dbt_client
    return get_dbt_client()


# -- Endpoints ----------------------------------------------------------------

@router.get("/models")
async def list_models():
    try:
        client = _get_client()
        return {"models": client.list_models()}
    except Exception as e:
        logger.error("Failed to list dbt models: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{name}")
async def get_model(name: str):
    try:
        client = _get_client()
        model = client.get_model(name)
        if model is None:
            raise HTTPException(status_code=404, detail=f"Model '{name}' not found")
        return model
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get model %s: %s", name, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run")
async def run_dbt(req: DbtRunRequest):
    try:
        client = _get_client()
        result = client.run(
            select=req.select,
            exclude=req.exclude,
            full_refresh=req.full_refresh,
        )
        return result
    except Exception as e:
        logger.error("dbt run failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_dbt(req: DbtTestRequest):
    try:
        client = _get_client()
        return client.test(select=req.select)
    except Exception as e:
        logger.error("dbt test failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compile")
async def compile_dbt():
    try:
        client = _get_client()
        return client.compile()
    except Exception as e:
        logger.error("dbt compile failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/docs/generate")
async def generate_docs():
    try:
        client = _get_client()
        return client.generate_docs()
    except Exception as e:
        logger.error("dbt docs generate failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lineage")
async def dbt_lineage():
    try:
        client = _get_client()
        return client.get_lineage()
    except Exception as e:
        logger.error("Failed to get dbt lineage: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    try:
        client = _get_client()
        run = client.get_run(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
        return run
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get run %s: %s", run_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/manifest")
async def get_manifest():
    try:
        client = _get_client()
        return client.get_manifest()
    except Exception as e:
        logger.error("Failed to get manifest: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/catalog")
async def get_catalog():
    try:
        client = _get_client()
        return client.get_catalog()
    except Exception as e:
        logger.error("Failed to get catalog: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
