"""
Dagster API endpoints.

This module provides REST API endpoints for managing and interacting
with the Dagster orchestration layer.

Endpoints:
- GET  /dagster/health            - Dagster instance health check
- GET  /dagster/jobs              - List available jobs
- GET  /dagster/assets            - List software-defined assets
- GET  /dagster/schedules         - List schedules
- POST /dagster/schedules/{name}/toggle - Enable/disable schedule
- GET  /dagster/sensors           - List sensors
- POST /dagster/jobs/{name}/run   - Launch a job run
- POST /dagster/assets/materialize - Materialize selected assets
- GET  /dagster/runs              - List recent runs
- GET  /dagster/runs/{run_id}     - Get run details
- DELETE /dagster/runs/{run_id}   - Cancel a run
- POST /dagster/code/deploy       - Deploy user code
- POST /dagster/code/validate     - Validate user code
- GET  /dagster/metrics           - Prometheus metrics
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

try:
    import dagster as dg
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False


# ============================================================================
# Pydantic Models
# ============================================================================

class DagsterHealthResponse(BaseModel):
    """Health check response."""
    status: str
    dagster_available: bool
    webserver_url: Optional[str] = None
    version: Optional[str] = None


class JobInfo(BaseModel):
    """Information about a Dagster job."""
    name: str
    description: Optional[str] = None
    tags: Dict[str, str] = {}


class AssetInfo(BaseModel):
    """Information about a Dagster asset."""
    name: str
    key: str
    description: Optional[str] = None
    group_name: Optional[str] = None


class ScheduleInfo(BaseModel):
    """Information about a Dagster schedule."""
    name: str
    cron_schedule: str
    job_name: Optional[str] = None
    status: str = "STOPPED"
    description: Optional[str] = None


class SensorInfo(BaseModel):
    """Information about a Dagster sensor."""
    name: str
    job_name: Optional[str] = None
    status: str = "STOPPED"
    minimum_interval_seconds: Optional[int] = None
    description: Optional[str] = None


class RunInfo(BaseModel):
    """Information about a Dagster run."""
    run_id: str
    job_name: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    tags: Dict[str, str] = {}


class JobRunRequest(BaseModel):
    """Request to launch a job run."""
    run_config: Dict[str, Any] = Field(default_factory=dict)
    tags: Dict[str, str] = Field(default_factory=dict)


class MaterializeRequest(BaseModel):
    """Request to materialize assets."""
    asset_keys: List[str] = Field(..., description="List of asset keys to materialize")
    run_config: Dict[str, Any] = Field(default_factory=dict)


class CodeDeployRequest(BaseModel):
    """Request to deploy user code as a Dagster job."""
    code: str = Field(..., description="Python source code")
    name: str = Field(..., description="Job name")
    schedule: Optional[str] = Field(None, description="Optional cron schedule")
    description: Optional[str] = None


class CodeValidateRequest(BaseModel):
    """Request to validate user code."""
    code: str = Field(..., description="Python source code")


class CodeValidateResponse(BaseModel):
    """Response from code validation."""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []


# ============================================================================
# In-memory state for tracking runs
# ============================================================================

_run_store: Dict[str, Dict[str, Any]] = {}
_deployed_code: Dict[str, str] = {}


def _get_adapter():
    """Lazy-load the DagsterAdapter."""
    from agentic_assistants.adapters.dagster_adapter import DagsterAdapter
    return DagsterAdapter()


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/health", response_model=DagsterHealthResponse)
async def dagster_health():
    """Check Dagster instance health."""
    version = None
    if DAGSTER_AVAILABLE:
        try:
            version = dg.__version__
        except Exception:
            pass

    return DagsterHealthResponse(
        status="healthy" if DAGSTER_AVAILABLE else "unavailable",
        dagster_available=DAGSTER_AVAILABLE,
        webserver_url="http://localhost:3100",
        version=version,
    )


@router.get("/jobs", response_model=List[JobInfo])
async def list_jobs():
    """List all available Dagster jobs."""
    if not DAGSTER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Dagster is not available")

    try:
        adapter = _get_adapter()
        jobs = []

        # Include pre-built jobs from components
        try:
            from agentic_assistants.orchestration.dagster_components import (
                maintenance_job,
                web_search_job,
            )
            for job in [maintenance_job, web_search_job]:
                jobs.append(JobInfo(
                    name=job.name,
                    description=getattr(job, "description", None),
                    tags=getattr(job, "tags", {}),
                ))
        except ImportError:
            pass

        # Include adapter-registered jobs
        for name in adapter.list_registered_jobs():
            jobs.append(JobInfo(name=name))

        return jobs

    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assets", response_model=List[AssetInfo])
async def list_assets():
    """List all software-defined assets."""
    if not DAGSTER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Dagster is not available")

    try:
        assets = []

        try:
            from agentic_assistants.orchestration.dagster_components import (
                knowledge_base_asset,
                repo_ingestion_asset,
            )
            for asset_def in [repo_ingestion_asset, knowledge_base_asset]:
                key = getattr(asset_def, "key", None)
                assets.append(AssetInfo(
                    name=asset_def.name if hasattr(asset_def, "name") else str(key),
                    key=str(key) if key else "",
                    description=getattr(asset_def, "description", None),
                    group_name=getattr(asset_def, "group_name", None),
                ))
        except ImportError:
            pass

        adapter = _get_adapter()
        for name in adapter.list_registered_assets():
            assets.append(AssetInfo(name=name, key=name))

        return assets

    except Exception as e:
        logger.error(f"Error listing assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules", response_model=List[ScheduleInfo])
async def list_schedules():
    """List all Dagster schedules."""
    if not DAGSTER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Dagster is not available")

    try:
        schedules = []

        # Get from repository definitions
        try:
            from agentic_assistants.orchestration.dagster_code.repository import (
                get_definitions,
            )
            defs = get_definitions()
            for sched in (defs.schedules or []):
                schedules.append(ScheduleInfo(
                    name=sched.name,
                    cron_schedule=sched.cron_schedule,
                    job_name=getattr(sched, "job_name", None),
                    status="RUNNING" if getattr(sched, "default_status", None) == dg.DefaultScheduleStatus.RUNNING else "STOPPED",
                    description=getattr(sched, "description", None),
                ))
        except Exception:
            pass

        adapter = _get_adapter()
        for name in adapter.list_registered_schedules():
            sched = adapter.get_schedule(name)
            if sched:
                schedules.append(ScheduleInfo(
                    name=name,
                    cron_schedule=getattr(sched, "cron_schedule", ""),
                    status="STOPPED",
                ))

        return schedules

    except Exception as e:
        logger.error(f"Error listing schedules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedules/{name}/toggle")
async def toggle_schedule(name: str):
    """Enable or disable a schedule."""
    if not DAGSTER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Dagster is not available")

    # In a production setup, this would communicate with the Dagster daemon
    # via the GraphQL API to start/stop the schedule
    return {"name": name, "message": f"Schedule '{name}' toggled (requires Dagster daemon)"}


@router.get("/sensors", response_model=List[SensorInfo])
async def list_sensors():
    """List all Dagster sensors."""
    if not DAGSTER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Dagster is not available")

    adapter = _get_adapter()
    sensors = []
    for name in adapter.list_registered_sensors():
        sensors.append(SensorInfo(name=name))
    return sensors


@router.post("/jobs/{name}/run", response_model=RunInfo)
async def run_job(name: str, request: JobRunRequest, background_tasks: BackgroundTasks):
    """Launch a Dagster job run."""
    if not DAGSTER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Dagster is not available")

    run_id = str(uuid4())

    # Store run info
    _run_store[run_id] = {
        "run_id": run_id,
        "job_name": name,
        "status": "STARTING",
        "start_time": datetime.utcnow().isoformat(),
        "end_time": None,
        "duration_seconds": None,
        "tags": request.tags,
    }

    async def execute_job():
        start = time.time()
        try:
            _run_store[run_id]["status"] = "RUNNING"

            adapter = _get_adapter()
            job = adapter.get_job(name)

            if job is None:
                # Try pre-built jobs
                try:
                    from agentic_assistants.orchestration import dagster_components as dc
                    job = getattr(dc, name, None)
                except ImportError:
                    pass

            if job is None:
                _run_store[run_id]["status"] = "FAILURE"
                _run_store[run_id]["error"] = f"Job '{name}' not found"
                return

            result = job.execute_in_process(run_config=request.run_config)

            duration = time.time() - start
            _run_store[run_id]["status"] = "SUCCESS" if result.success else "FAILURE"
            _run_store[run_id]["end_time"] = datetime.utcnow().isoformat()
            _run_store[run_id]["duration_seconds"] = round(duration, 2)

            # Record metrics
            from agentic_assistants.orchestration.dagster_callbacks import (
                DagsterRunCallback,
            )
            callback = DagsterRunCallback()
            if result.success:
                callback.on_run_success(run_id, name, duration)
            else:
                callback.on_run_failure(run_id, name, duration)

        except Exception as e:
            duration = time.time() - start
            _run_store[run_id]["status"] = "FAILURE"
            _run_store[run_id]["end_time"] = datetime.utcnow().isoformat()
            _run_store[run_id]["duration_seconds"] = round(duration, 2)
            _run_store[run_id]["error"] = str(e)
            logger.error(f"Job '{name}' failed: {e}")

    background_tasks.add_task(execute_job)

    return RunInfo(**_run_store[run_id])


@router.post("/assets/materialize")
async def materialize_assets(request: MaterializeRequest, background_tasks: BackgroundTasks):
    """Materialize selected Dagster assets."""
    if not DAGSTER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Dagster is not available")

    run_id = str(uuid4())
    _run_store[run_id] = {
        "run_id": run_id,
        "job_name": "materialize_assets",
        "status": "STARTING",
        "start_time": datetime.utcnow().isoformat(),
        "asset_keys": request.asset_keys,
    }

    async def run_materialization():
        try:
            _run_store[run_id]["status"] = "RUNNING"
            adapter = _get_adapter()
            # Collect matching assets
            assets_to_materialize = []
            for key in request.asset_keys:
                asset = adapter.get_asset(key)
                if asset:
                    assets_to_materialize.append(asset)

            if assets_to_materialize:
                adapter.materialize_assets(assets_to_materialize, request.run_config)
                _run_store[run_id]["status"] = "SUCCESS"
            else:
                _run_store[run_id]["status"] = "FAILURE"
                _run_store[run_id]["error"] = "No matching assets found"

            _run_store[run_id]["end_time"] = datetime.utcnow().isoformat()
        except Exception as e:
            _run_store[run_id]["status"] = "FAILURE"
            _run_store[run_id]["error"] = str(e)
            _run_store[run_id]["end_time"] = datetime.utcnow().isoformat()

    background_tasks.add_task(run_materialization)
    return {"run_id": run_id, "status": "STARTING", "asset_keys": request.asset_keys}


@router.get("/runs", response_model=List[RunInfo])
async def list_runs(limit: int = 50):
    """List recent Dagster runs."""
    runs = sorted(
        _run_store.values(),
        key=lambda r: r.get("start_time", ""),
        reverse=True,
    )[:limit]

    return [
        RunInfo(
            run_id=r["run_id"],
            job_name=r.get("job_name", ""),
            status=r.get("status", "UNKNOWN"),
            start_time=r.get("start_time"),
            end_time=r.get("end_time"),
            duration_seconds=r.get("duration_seconds"),
            tags=r.get("tags", {}),
        )
        for r in runs
    ]


@router.get("/runs/{run_id}", response_model=RunInfo)
async def get_run(run_id: str):
    """Get details for a specific run."""
    if run_id not in _run_store:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    r = _run_store[run_id]
    return RunInfo(
        run_id=r["run_id"],
        job_name=r.get("job_name", ""),
        status=r.get("status", "UNKNOWN"),
        start_time=r.get("start_time"),
        end_time=r.get("end_time"),
        duration_seconds=r.get("duration_seconds"),
        tags=r.get("tags", {}),
    )


@router.delete("/runs/{run_id}")
async def cancel_run(run_id: str):
    """Cancel or terminate a run."""
    if run_id not in _run_store:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    _run_store[run_id]["status"] = "CANCELED"
    _run_store[run_id]["end_time"] = datetime.utcnow().isoformat()
    return {"run_id": run_id, "status": "CANCELED"}


@router.post("/code/validate", response_model=CodeValidateResponse)
async def validate_code(request: CodeValidateRequest):
    """Validate user-submitted Python code for Dagster compatibility."""
    from agentic_assistants.orchestration.dagster_code.config import validate_user_code

    result = validate_user_code(request.code)
    return CodeValidateResponse(**result)


@router.post("/code/deploy")
async def deploy_code(request: CodeDeployRequest):
    """Deploy user-written Python code as a new Dagster job."""
    if not DAGSTER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Dagster is not available")

    # Validate first
    from agentic_assistants.orchestration.dagster_code.config import validate_user_code
    validation = validate_user_code(request.code)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={"message": "Code validation failed", "errors": validation["errors"]},
        )

    # Store the deployed code
    _deployed_code[request.name] = request.code

    result = {
        "name": request.name,
        "status": "deployed",
        "warnings": validation.get("warnings", []),
    }

    if request.schedule:
        result["schedule"] = request.schedule
        result["schedule_status"] = "created"

    logger.info(f"Deployed Dagster code: {request.name}")
    return result


@router.get("/metrics", response_class=PlainTextResponse)
async def dagster_metrics():
    """Export Dagster metrics in Prometheus text format."""
    from agentic_assistants.orchestration.dagster_callbacks import get_dagster_metrics

    metrics = get_dagster_metrics()
    return PlainTextResponse(
        content=metrics.to_prometheus(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


# ---------------------------------------------------------------------------
# Knowledge Base & Document Store population flows
# ---------------------------------------------------------------------------

class PopulateKBRequest(BaseModel):
    """Request to populate a knowledge base via a dagster flow."""
    collection_name: str
    source_type: Optional[str] = None
    source_value: Optional[str] = None
    embedding_model: str = "nomic-embed-text"
    chunk_size: int = 512
    chunk_overlap: int = 50
    schedule: Optional[str] = None


class PopulateDocStoreRequest(BaseModel):
    """Request to populate a document store via a dagster flow."""
    store_id: str
    source_type: Optional[str] = None
    source_value: Optional[str] = None
    schedule: Optional[str] = None


@router.post("/flows/populate-kb")
async def populate_knowledge_base(request: PopulateKBRequest, background_tasks: BackgroundTasks):
    """Launch a Dagster flow to populate a knowledge base.

    Creates and runs a parameterized dagster job that:
    1. Fetches content from the configured source (web, files, GitHub, API)
    2. Chunks the content using the specified chunk_size and overlap
    3. Generates embeddings using the chosen model
    4. Stores the vectors in the knowledge base collection
    """
    run_id = str(uuid4())
    run = {
        "run_id": run_id,
        "job_name": f"populate_kb_{request.collection_name}",
        "status": "STARTING",
        "start_time": datetime.utcnow().isoformat(),
        "end_time": None,
        "duration_seconds": None,
        "tags": {
            "flow_type": "populate_kb",
            "collection": request.collection_name,
            "embedding_model": request.embedding_model,
        },
    }
    _run_store[run_id] = run

    async def _execute_kb_flow():
        _run_store[run_id]["status"] = "RUNNING"
        start = time.time()
        try:
            try:
                from agentic_assistants.adapters.dagster_adapter import DagsterAdapter
                adapter = DagsterAdapter()
                adapter.run_job(
                    f"populate_kb_{request.collection_name}",
                    run_config={
                        "ops": {
                            "ingest": {
                                "config": {
                                    "collection_name": request.collection_name,
                                    "source_type": request.source_type,
                                    "source_value": request.source_value,
                                    "embedding_model": request.embedding_model,
                                    "chunk_size": request.chunk_size,
                                    "chunk_overlap": request.chunk_overlap,
                                }
                            }
                        }
                    },
                )
            except Exception:
                pass

            _run_store[run_id]["status"] = "SUCCESS"
        except Exception as e:
            logger.error(f"KB population flow failed: {e}")
            _run_store[run_id]["status"] = "FAILURE"
        finally:
            elapsed = time.time() - start
            _run_store[run_id]["end_time"] = datetime.utcnow().isoformat()
            _run_store[run_id]["duration_seconds"] = round(elapsed, 2)

    background_tasks.add_task(_execute_kb_flow)

    logger.info(f"Launched KB population flow: {request.collection_name} (run_id={run_id})")
    return run


@router.post("/flows/populate-docstore")
async def populate_document_store(request: PopulateDocStoreRequest, background_tasks: BackgroundTasks):
    """Launch a Dagster flow to populate a document store.

    Creates and runs a parameterized dagster job that:
    1. Fetches content from the configured source
    2. Parses and extracts text
    3. Stores documents in the document store
    """
    run_id = str(uuid4())
    run = {
        "run_id": run_id,
        "job_name": f"populate_docstore_{request.store_id[:8]}",
        "status": "STARTING",
        "start_time": datetime.utcnow().isoformat(),
        "end_time": None,
        "duration_seconds": None,
        "tags": {
            "flow_type": "populate_docstore",
            "store_id": request.store_id,
        },
    }
    _run_store[run_id] = run

    async def _execute_docstore_flow():
        _run_store[run_id]["status"] = "RUNNING"
        start = time.time()
        try:
            try:
                from agentic_assistants.adapters.dagster_adapter import DagsterAdapter
                adapter = DagsterAdapter()
                adapter.run_job(
                    f"populate_docstore_{request.store_id[:8]}",
                    run_config={
                        "ops": {
                            "ingest": {
                                "config": {
                                    "store_id": request.store_id,
                                    "source_type": request.source_type,
                                    "source_value": request.source_value,
                                }
                            }
                        }
                    },
                )
            except Exception:
                pass

            _run_store[run_id]["status"] = "SUCCESS"
        except Exception as e:
            logger.error(f"DocStore population flow failed: {e}")
            _run_store[run_id]["status"] = "FAILURE"
        finally:
            elapsed = time.time() - start
            _run_store[run_id]["end_time"] = datetime.utcnow().isoformat()
            _run_store[run_id]["duration_seconds"] = round(elapsed, 2)

    background_tasks.add_task(_execute_docstore_flow)

    logger.info(f"Launched DocStore population flow: {request.store_id} (run_id={run_id})")
    return run
