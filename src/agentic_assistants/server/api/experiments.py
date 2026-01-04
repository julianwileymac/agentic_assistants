"""
MLFlow Experiments API Router.

This module provides REST endpoints for MLFlow experiment management:
- CRUD operations for experiments
- Run management (start, stop, log metrics)
- Artifact association with experiments
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/experiments", tags=["experiments"])


# === Request/Response Models ===


class ExperimentCreate(BaseModel):
    """Request to create a new experiment."""
    
    name: str = Field(..., description="Experiment name")
    description: Optional[str] = Field(None, description="Experiment description")
    tags: Optional[dict[str, str]] = Field(default_factory=dict, description="Experiment tags")


class ExperimentUpdate(BaseModel):
    """Request to update an experiment."""
    
    name: Optional[str] = Field(None, description="New experiment name")
    description: Optional[str] = Field(None, description="New description")
    tags: Optional[dict[str, str]] = Field(None, description="Updated tags")


class RunCreate(BaseModel):
    """Request to create a new run."""
    
    run_name: Optional[str] = Field(None, description="Run name")
    tags: Optional[dict[str, str]] = Field(default_factory=dict, description="Run tags")
    description: Optional[str] = Field(None, description="Run description")


class RunUpdate(BaseModel):
    """Request to update a run."""
    
    status: Optional[str] = Field(None, description="Run status (RUNNING, FINISHED, FAILED)")
    end_time: Optional[datetime] = Field(None, description="Run end time")


class LogMetrics(BaseModel):
    """Request to log metrics to a run."""
    
    metrics: dict[str, float] = Field(..., description="Metrics to log")
    step: Optional[int] = Field(None, description="Step number")
    timestamp: Optional[datetime] = Field(None, description="Timestamp for metrics")


class LogParams(BaseModel):
    """Request to log parameters to a run."""
    
    params: dict[str, str] = Field(..., description="Parameters to log")


class ExperimentResponse(BaseModel):
    """Response containing experiment details."""
    
    experiment_id: str
    name: str
    description: Optional[str] = None
    artifact_location: Optional[str] = None
    lifecycle_stage: str = "active"
    tags: dict[str, str] = Field(default_factory=dict)
    creation_time: Optional[datetime] = None
    last_update_time: Optional[datetime] = None


class RunResponse(BaseModel):
    """Response containing run details."""
    
    run_id: str
    experiment_id: str
    run_name: Optional[str] = None
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    artifact_uri: Optional[str] = None
    metrics: dict[str, float] = Field(default_factory=dict)
    params: dict[str, str] = Field(default_factory=dict)
    tags: dict[str, str] = Field(default_factory=dict)


class ExperimentsListResponse(BaseModel):
    """Response containing list of experiments."""
    
    experiments: list[ExperimentResponse]
    total: int


class RunsListResponse(BaseModel):
    """Response containing list of runs."""
    
    runs: list[RunResponse]
    total: int


# === Helper Functions ===


def _get_mlflow_client():
    """Get MLFlow client instance."""
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
        
        config = AgenticConfig()
        mlflow.set_tracking_uri(config.mlflow.tracking_uri)
        return MlflowClient()
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="MLFlow is not installed or not available"
        )
    except Exception as e:
        logger.error(f"Failed to initialize MLFlow client: {e}")
        raise HTTPException(status_code=503, detail=str(e))


def _experiment_to_response(experiment) -> ExperimentResponse:
    """Convert MLFlow experiment to response model."""
    return ExperimentResponse(
        experiment_id=experiment.experiment_id,
        name=experiment.name,
        artifact_location=experiment.artifact_location,
        lifecycle_stage=experiment.lifecycle_stage,
        tags=dict(experiment.tags) if experiment.tags else {},
        creation_time=datetime.fromtimestamp(experiment.creation_time / 1000) 
            if experiment.creation_time else None,
        last_update_time=datetime.fromtimestamp(experiment.last_update_time / 1000)
            if experiment.last_update_time else None,
    )


def _run_to_response(run) -> RunResponse:
    """Convert MLFlow run to response model."""
    return RunResponse(
        run_id=run.info.run_id,
        experiment_id=run.info.experiment_id,
        run_name=run.info.run_name,
        status=run.info.status,
        start_time=datetime.fromtimestamp(run.info.start_time / 1000)
            if run.info.start_time else None,
        end_time=datetime.fromtimestamp(run.info.end_time / 1000)
            if run.info.end_time else None,
        artifact_uri=run.info.artifact_uri,
        metrics=dict(run.data.metrics) if run.data.metrics else {},
        params=dict(run.data.params) if run.data.params else {},
        tags=dict(run.data.tags) if run.data.tags else {},
    )


# === Endpoints ===


@router.get("", response_model=ExperimentsListResponse)
async def list_experiments(
    view_type: str = Query("ACTIVE_ONLY", description="View type: ACTIVE_ONLY, DELETED_ONLY, ALL"),
    max_results: int = Query(100, ge=1, le=1000, description="Maximum results"),
) -> ExperimentsListResponse:
    """List all experiments."""
    logger.debug(f"Listing experiments with view_type={view_type}")
    
    client = _get_mlflow_client()
    
    try:
        from mlflow.entities import ViewType
        
        view_type_map = {
            "ACTIVE_ONLY": ViewType.ACTIVE_ONLY,
            "DELETED_ONLY": ViewType.DELETED_ONLY,
            "ALL": ViewType.ALL,
        }
        view = view_type_map.get(view_type, ViewType.ACTIVE_ONLY)
        
        experiments = client.search_experiments(
            view_type=view,
            max_results=max_results,
        )
        
        return ExperimentsListResponse(
            experiments=[_experiment_to_response(exp) for exp in experiments],
            total=len(experiments),
        )
    except Exception as e:
        logger.error(f"Failed to list experiments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ExperimentResponse)
async def create_experiment(request: ExperimentCreate) -> ExperimentResponse:
    """Create a new experiment."""
    logger.info(f"Creating experiment: {request.name}")
    
    client = _get_mlflow_client()
    
    try:
        experiment_id = client.create_experiment(
            name=request.name,
            tags=request.tags,
        )
        
        if request.description:
            client.set_experiment_tag(experiment_id, "mlflow.note.content", request.description)
        
        experiment = client.get_experiment(experiment_id)
        return _experiment_to_response(experiment)
    except Exception as e:
        logger.error(f"Failed to create experiment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: str) -> ExperimentResponse:
    """Get experiment by ID."""
    logger.debug(f"Getting experiment: {experiment_id}")
    
    client = _get_mlflow_client()
    
    try:
        experiment = client.get_experiment(experiment_id)
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        return _experiment_to_response(experiment)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(experiment_id: str, request: ExperimentUpdate) -> ExperimentResponse:
    """Update an experiment."""
    logger.info(f"Updating experiment: {experiment_id}")
    
    client = _get_mlflow_client()
    
    try:
        if request.name:
            client.rename_experiment(experiment_id, request.name)
        
        if request.description:
            client.set_experiment_tag(experiment_id, "mlflow.note.content", request.description)
        
        if request.tags:
            for key, value in request.tags.items():
                client.set_experiment_tag(experiment_id, key, value)
        
        experiment = client.get_experiment(experiment_id)
        return _experiment_to_response(experiment)
    except Exception as e:
        logger.error(f"Failed to update experiment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{experiment_id}")
async def delete_experiment(experiment_id: str) -> dict[str, str]:
    """Delete an experiment (soft delete)."""
    logger.info(f"Deleting experiment: {experiment_id}")
    
    client = _get_mlflow_client()
    
    try:
        client.delete_experiment(experiment_id)
        return {"status": "deleted", "experiment_id": experiment_id}
    except Exception as e:
        logger.error(f"Failed to delete experiment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{experiment_id}/restore")
async def restore_experiment(experiment_id: str) -> dict[str, str]:
    """Restore a deleted experiment."""
    logger.info(f"Restoring experiment: {experiment_id}")
    
    client = _get_mlflow_client()
    
    try:
        client.restore_experiment(experiment_id)
        return {"status": "restored", "experiment_id": experiment_id}
    except Exception as e:
        logger.error(f"Failed to restore experiment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# === Run Endpoints ===


@router.get("/{experiment_id}/runs", response_model=RunsListResponse)
async def list_runs(
    experiment_id: str,
    filter_string: Optional[str] = Query(None, description="Filter expression"),
    order_by: Optional[str] = Query(None, description="Order by field"),
    max_results: int = Query(100, ge=1, le=1000, description="Maximum results"),
) -> RunsListResponse:
    """List runs for an experiment."""
    logger.debug(f"Listing runs for experiment: {experiment_id}")
    
    client = _get_mlflow_client()
    
    try:
        runs = client.search_runs(
            experiment_ids=[experiment_id],
            filter_string=filter_string or "",
            order_by=[order_by] if order_by else None,
            max_results=max_results,
        )
        
        return RunsListResponse(
            runs=[_run_to_response(run) for run in runs],
            total=len(runs),
        )
    except Exception as e:
        logger.error(f"Failed to list runs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{experiment_id}/runs", response_model=RunResponse)
async def create_run(experiment_id: str, request: RunCreate) -> RunResponse:
    """Create a new run in an experiment."""
    logger.info(f"Creating run in experiment: {experiment_id}")
    
    client = _get_mlflow_client()
    
    try:
        run = client.create_run(
            experiment_id=experiment_id,
            run_name=request.run_name,
            tags=request.tags,
        )
        
        if request.description:
            client.set_tag(run.info.run_id, "mlflow.note.content", request.description)
        
        return _run_to_response(run)
    except Exception as e:
        logger.error(f"Failed to create run: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: str) -> RunResponse:
    """Get run by ID."""
    logger.debug(f"Getting run: {run_id}")
    
    client = _get_mlflow_client()
    
    try:
        run = client.get_run(run_id)
        return _run_to_response(run)
    except Exception as e:
        logger.error(f"Failed to get run: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/runs/{run_id}", response_model=RunResponse)
async def update_run(run_id: str, request: RunUpdate) -> RunResponse:
    """Update a run."""
    logger.info(f"Updating run: {run_id}")
    
    client = _get_mlflow_client()
    
    try:
        if request.status:
            from mlflow.entities import RunStatus
            status_map = {
                "RUNNING": RunStatus.RUNNING,
                "FINISHED": RunStatus.FINISHED,
                "FAILED": RunStatus.FAILED,
                "KILLED": RunStatus.KILLED,
            }
            status = status_map.get(request.status)
            if status:
                end_time = int(request.end_time.timestamp() * 1000) if request.end_time else None
                client.set_terminated(run_id, status=request.status, end_time=end_time)
        
        run = client.get_run(run_id)
        return _run_to_response(run)
    except Exception as e:
        logger.error(f"Failed to update run: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/runs/{run_id}")
async def delete_run(run_id: str) -> dict[str, str]:
    """Delete a run."""
    logger.info(f"Deleting run: {run_id}")
    
    client = _get_mlflow_client()
    
    try:
        client.delete_run(run_id)
        return {"status": "deleted", "run_id": run_id}
    except Exception as e:
        logger.error(f"Failed to delete run: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/runs/{run_id}/end")
async def end_run(run_id: str, status: str = "FINISHED") -> dict[str, Any]:
    """End a run with the specified status."""
    logger.info(f"Ending run {run_id} with status {status}")
    
    client = _get_mlflow_client()
    
    try:
        end_time = int(datetime.now().timestamp() * 1000)
        client.set_terminated(run_id, status=status, end_time=end_time)
        return {"status": "ended", "run_id": run_id, "final_status": status}
    except Exception as e:
        logger.error(f"Failed to end run: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/runs/{run_id}/metrics")
async def log_metrics(run_id: str, request: LogMetrics) -> dict[str, Any]:
    """Log metrics to a run."""
    logger.debug(f"Logging metrics to run: {run_id}")
    
    client = _get_mlflow_client()
    
    try:
        timestamp = int((request.timestamp or datetime.now()).timestamp() * 1000)
        
        for key, value in request.metrics.items():
            client.log_metric(
                run_id=run_id,
                key=key,
                value=value,
                step=request.step or 0,
                timestamp=timestamp,
            )
        
        return {
            "status": "logged",
            "run_id": run_id,
            "metrics_count": len(request.metrics),
        }
    except Exception as e:
        logger.error(f"Failed to log metrics: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/runs/{run_id}/params")
async def log_params(run_id: str, request: LogParams) -> dict[str, Any]:
    """Log parameters to a run."""
    logger.debug(f"Logging params to run: {run_id}")
    
    client = _get_mlflow_client()
    
    try:
        for key, value in request.params.items():
            client.log_param(run_id=run_id, key=key, value=value)
        
        return {
            "status": "logged",
            "run_id": run_id,
            "params_count": len(request.params),
        }
    except Exception as e:
        logger.error(f"Failed to log params: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/runs/{run_id}/tags")
async def set_run_tags(run_id: str, tags: dict[str, str]) -> dict[str, Any]:
    """Set tags on a run."""
    logger.debug(f"Setting tags on run: {run_id}")
    
    client = _get_mlflow_client()
    
    try:
        for key, value in tags.items():
            client.set_tag(run_id=run_id, key=key, value=value)
        
        return {
            "status": "tagged",
            "run_id": run_id,
            "tags_count": len(tags),
        }
    except Exception as e:
        logger.error(f"Failed to set tags: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/runs/{run_id}/artifacts")
async def list_run_artifacts(
    run_id: str,
    path: str = Query("", description="Artifact path prefix"),
) -> dict[str, Any]:
    """List artifacts for a run."""
    logger.debug(f"Listing artifacts for run: {run_id}")
    
    client = _get_mlflow_client()
    
    try:
        artifacts = client.list_artifacts(run_id, path)
        return {
            "run_id": run_id,
            "artifacts": [
                {
                    "path": a.path,
                    "is_dir": a.is_dir,
                    "file_size": a.file_size,
                }
                for a in artifacts
            ],
        }
    except Exception as e:
        logger.error(f"Failed to list artifacts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

