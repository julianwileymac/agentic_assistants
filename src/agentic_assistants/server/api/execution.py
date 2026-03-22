"""
REST API endpoints for script execution.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from agentic_assistants.execution import ScriptManager
from agentic_assistants.core.mlflow_tracker import MLFlowTracker
from agentic_assistants.config import AgenticConfig
from agentic_assistants.server.websocket import LogStreamer, emitter
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/execution", tags=["execution"])


class ScriptExecutionRequest(BaseModel):
    """Request to execute a script."""
    script_content: str
    script_name: Optional[str] = None
    script_type: str = "python"  # python, shell, notebook
    env_vars: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None
    async_run: bool = False
    tracking_enabled: Optional[bool] = None
    rl_metrics_enabled: Optional[bool] = None


class ScriptExecutionResponse(BaseModel):
    """Response from script execution."""
    run_id: str
    status: str
    message: str


@router.post("/scripts/run", response_model=ScriptExecutionResponse)
async def run_script(
    request: ScriptExecutionRequest,
    background_tasks: BackgroundTasks,
):
    """
    Execute a script.
    
    Args:
        request: Script execution request
        background_tasks: FastAPI background tasks
        
    Returns:
        Execution response
    """
    script_manager = ScriptManager()
    
    if request.async_run:
        # Run in background
        if request.script_type == "python":
            background_tasks.add_task(
                script_manager.execute_python,
                request.script_content,
                request.script_name,
                request.env_vars,
                request.timeout,
            )
        
        return ScriptExecutionResponse(
            run_id="pending",
            status="queued",
            message="Script queued for execution",
        )
    else:
        # Run synchronously
        if request.script_type == "python":
            result = await script_manager.execute_python(
                request.script_content,
                request.script_name,
                request.env_vars,
                request.timeout,
            )
        elif request.script_type == "shell":
            result = await script_manager.execute_shell(
                request.script_content,
                env_vars=request.env_vars,
                timeout=request.timeout,
            )
        else:
            raise HTTPException(400, f"Unsupported script type: {request.script_type}")
        
        config = AgenticConfig()
        tracking = request.tracking_enabled
        if tracking is None:
            tracking = config.testing.tracking_default
        rl_metrics = request.rl_metrics_enabled
        if rl_metrics is None:
            rl_metrics = config.testing.rl_metrics_default
        
        if tracking:
            tracker = MLFlowTracker(config)
            tracker.enabled = bool(config.mlflow_enabled)
            with tracker.start_run(run_name=request.script_name or "script-execution"):
                duration = result.get("duration_seconds")
                if duration is not None:
                    tracker.log_metric("execution_time_s", float(duration))
                tracker.log_param("script_type", request.script_type)
                tracker.log_param("status", result.get("status", "unknown"))
                if rl_metrics:
                    tracker.log_metric(
                        "rl/execution/success",
                        1.0 if result.get("status") == "success" else 0.0,
                    )
        
        log_streamer = LogStreamer(result["run_id"], emitter)
        if result.get("output"):
            await log_streamer.write(result["output"], "INFO")
        if result.get("error"):
            await log_streamer.write(result["error"], "ERROR")
        await log_streamer.close()
        
        return ScriptExecutionResponse(
            run_id=result["run_id"],
            status=result["status"],
            message="Script executed",
        )


@router.get("/runs")
async def list_executions(
    status: Optional[str] = None,
    limit: int = 50,
):
    """List execution runs."""
    script_manager = ScriptManager()
    return script_manager.list_executions(status=status, limit=limit)


@router.get("/runs/{run_id}")
async def get_execution(run_id: str):
    """Get execution details."""
    script_manager = ScriptManager()
    result = script_manager.get_execution(run_id)
    
    if not result:
        raise HTTPException(404, f"Execution not found: {run_id}")
    
    return result
