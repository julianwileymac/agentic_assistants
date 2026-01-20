"""
Jupyter Integration Wrapper for Programmatic Notebook Execution.

This module provides:
- Programmatic notebook execution
- Kernel management and session tracking
- Output capture and artifact storage
- Integration with MLFlow for experiment tracking

Example:
    >>> from agentic_assistants.integrations.jupyter_wrapper import NotebookExecutor
    >>> 
    >>> executor = NotebookExecutor()
    >>> result = executor.execute_notebook("analysis.ipynb", parameters={"input": "data.csv"})
    >>> print(result.outputs)
"""

import asyncio
import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CellOutput:
    """Output from a notebook cell."""
    
    cell_index: int
    cell_type: str  # code, markdown
    execution_count: Optional[int]
    outputs: List[Dict[str, Any]]
    stdout: str
    stderr: str
    error: Optional[str] = None
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_index": self.cell_index,
            "cell_type": self.cell_type,
            "execution_count": self.execution_count,
            "outputs": self.outputs,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "execution_time": self.execution_time,
        }


@dataclass
class NotebookResult:
    """Result of notebook execution."""
    
    notebook_path: str
    success: bool
    start_time: datetime
    end_time: datetime
    cell_outputs: List[CellOutput] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    error: Optional[str] = None
    output_notebook_path: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "notebook_path": self.notebook_path,
            "success": self.success,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "cell_outputs": [c.to_dict() for c in self.cell_outputs],
            "parameters": self.parameters,
            "artifacts": self.artifacts,
            "error": self.error,
            "output_notebook_path": self.output_notebook_path,
        }
    
    def get_outputs(self, output_type: Optional[str] = None) -> List[Dict]:
        """Get all outputs, optionally filtered by type."""
        all_outputs = []
        for cell in self.cell_outputs:
            for output in cell.outputs:
                if output_type is None or output.get("output_type") == output_type:
                    all_outputs.append(output)
        return all_outputs
    
    def get_display_data(self) -> List[Dict]:
        """Get all display_data outputs."""
        return self.get_outputs("display_data")
    
    def get_execute_results(self) -> List[Dict]:
        """Get all execute_result outputs."""
        return self.get_outputs("execute_result")


@dataclass
class KernelSession:
    """Information about a kernel session."""
    
    session_id: str
    kernel_name: str
    kernel_id: str
    started_at: datetime
    status: str = "idle"
    last_activity: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "kernel_name": self.kernel_name,
            "kernel_id": self.kernel_id,
            "started_at": self.started_at.isoformat(),
            "status": self.status,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
        }


class NotebookExecutor:
    """
    Execute Jupyter notebooks programmatically.
    
    Provides:
    - Notebook execution with parameters (papermill-style)
    - Output capture and parsing
    - Artifact collection
    - MLFlow integration for tracking
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        kernel_name: str = "python3",
        timeout_per_cell: int = 600,
        output_dir: Optional[str] = None,
    ):
        """
        Initialize the notebook executor.
        
        Args:
            config: Configuration instance
            kernel_name: Default kernel name
            timeout_per_cell: Default timeout per cell in seconds
            output_dir: Directory for output notebooks and artifacts
        """
        self.config = config or AgenticConfig()
        self.kernel_name = kernel_name
        self.timeout_per_cell = timeout_per_cell
        self.output_dir = Path(output_dir) if output_dir else Path(self.config.base_dir) / "notebook_outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def execute_notebook(
        self,
        notebook_path: Union[str, Path],
        parameters: Optional[Dict[str, Any]] = None,
        output_path: Optional[Union[str, Path]] = None,
        kernel_name: Optional[str] = None,
        timeout: Optional[int] = None,
        inject_parameters: bool = True,
        collect_artifacts: bool = True,
    ) -> NotebookResult:
        """
        Execute a notebook.
        
        Args:
            notebook_path: Path to the notebook
            parameters: Parameters to inject into the notebook
            output_path: Path for output notebook (auto-generated if None)
            kernel_name: Kernel to use
            timeout: Timeout per cell in seconds
            inject_parameters: Whether to inject parameters as a new cell
            collect_artifacts: Whether to collect output artifacts
            
        Returns:
            NotebookResult with execution details
        """
        notebook_path = Path(notebook_path)
        parameters = parameters or {}
        kernel_name = kernel_name or self.kernel_name
        timeout = timeout or self.timeout_per_cell
        
        if not notebook_path.exists():
            return NotebookResult(
                notebook_path=str(notebook_path),
                success=False,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                error=f"Notebook not found: {notebook_path}",
            )
        
        # Generate output path
        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"{notebook_path.stem}_{timestamp}.ipynb"
        else:
            output_path = Path(output_path)
        
        start_time = datetime.utcnow()
        
        try:
            # Try papermill first (preferred)
            result = self._execute_with_papermill(
                notebook_path=notebook_path,
                output_path=output_path,
                parameters=parameters,
                kernel_name=kernel_name,
                timeout=timeout,
            )
        except ImportError:
            # Fall back to nbconvert
            result = self._execute_with_nbconvert(
                notebook_path=notebook_path,
                output_path=output_path,
                parameters=parameters,
                kernel_name=kernel_name,
                timeout=timeout,
                inject_parameters=inject_parameters,
            )
        
        result.start_time = start_time
        result.end_time = datetime.utcnow()
        result.parameters = parameters
        
        # Collect artifacts if requested
        if collect_artifacts and result.success:
            result.artifacts = self._collect_artifacts(output_path)
        
        return result
    
    def _execute_with_papermill(
        self,
        notebook_path: Path,
        output_path: Path,
        parameters: Dict[str, Any],
        kernel_name: str,
        timeout: int,
    ) -> NotebookResult:
        """Execute notebook using papermill."""
        import papermill as pm
        
        try:
            output_nb = pm.execute_notebook(
                str(notebook_path),
                str(output_path),
                parameters=parameters,
                kernel_name=kernel_name,
                progress_bar=False,
                request_save_on_cell_execute=True,
            )
            
            # Parse outputs
            cell_outputs = self._parse_notebook_outputs(output_path)
            
            return NotebookResult(
                notebook_path=str(notebook_path),
                success=True,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                cell_outputs=cell_outputs,
                output_notebook_path=str(output_path),
            )
            
        except pm.PapermillExecutionError as e:
            return NotebookResult(
                notebook_path=str(notebook_path),
                success=False,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                error=str(e),
                output_notebook_path=str(output_path),
            )
    
    def _execute_with_nbconvert(
        self,
        notebook_path: Path,
        output_path: Path,
        parameters: Dict[str, Any],
        kernel_name: str,
        timeout: int,
        inject_parameters: bool,
    ) -> NotebookResult:
        """Execute notebook using nbconvert."""
        try:
            import nbformat
            from nbconvert.preprocessors import ExecutePreprocessor
        except ImportError:
            raise ImportError("nbconvert not installed. Run: pip install nbconvert")
        
        # Read notebook
        with open(notebook_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        
        # Inject parameters if requested
        if inject_parameters and parameters:
            param_code = "# Parameters\n"
            for key, value in parameters.items():
                param_code += f"{key} = {repr(value)}\n"
            
            param_cell = nbformat.v4.new_code_cell(param_code)
            param_cell["metadata"]["tags"] = ["parameters"]
            nb.cells.insert(0, param_cell)
        
        # Execute
        ep = ExecutePreprocessor(
            timeout=timeout,
            kernel_name=kernel_name,
        )
        
        try:
            ep.preprocess(nb, {"metadata": {"path": str(notebook_path.parent)}})
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
        
        # Save output notebook
        with open(output_path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)
        
        # Parse outputs
        cell_outputs = self._parse_notebook_outputs(output_path)
        
        return NotebookResult(
            notebook_path=str(notebook_path),
            success=success,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            cell_outputs=cell_outputs,
            error=error,
            output_notebook_path=str(output_path),
        )
    
    def _parse_notebook_outputs(self, notebook_path: Path) -> List[CellOutput]:
        """Parse outputs from an executed notebook."""
        try:
            import nbformat
        except ImportError:
            return []
        
        with open(notebook_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        
        cell_outputs = []
        
        for i, cell in enumerate(nb.cells):
            outputs = []
            stdout = ""
            stderr = ""
            error = None
            
            if cell.cell_type == "code":
                for output in cell.get("outputs", []):
                    output_type = output.get("output_type", "")
                    
                    if output_type == "stream":
                        if output.get("name") == "stdout":
                            stdout += output.get("text", "")
                        elif output.get("name") == "stderr":
                            stderr += output.get("text", "")
                    elif output_type == "error":
                        error = f"{output.get('ename', 'Error')}: {output.get('evalue', '')}"
                    else:
                        outputs.append(output)
            
            cell_outputs.append(CellOutput(
                cell_index=i,
                cell_type=cell.cell_type,
                execution_count=cell.get("execution_count"),
                outputs=outputs,
                stdout=stdout,
                stderr=stderr,
                error=error,
            ))
        
        return cell_outputs
    
    def _collect_artifacts(self, notebook_path: Path) -> List[str]:
        """Collect artifacts generated by the notebook."""
        artifacts = []
        
        # Look for common artifact patterns in the notebook directory
        notebook_dir = notebook_path.parent
        artifact_patterns = ["*.png", "*.jpg", "*.svg", "*.pdf", "*.html", "*.csv", "*.pkl"]
        
        # Get files modified after notebook was created
        nb_mtime = notebook_path.stat().st_mtime
        
        for pattern in artifact_patterns:
            for artifact_path in notebook_dir.glob(pattern):
                if artifact_path.stat().st_mtime >= nb_mtime - 60:  # Allow 1 minute buffer
                    artifacts.append(str(artifact_path))
        
        return artifacts
    
    def execute_notebook_with_mlflow(
        self,
        notebook_path: Union[str, Path],
        parameters: Optional[Dict[str, Any]] = None,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        **kwargs,
    ) -> NotebookResult:
        """
        Execute a notebook with MLFlow tracking.
        
        Args:
            notebook_path: Path to the notebook
            parameters: Parameters to inject
            experiment_name: MLFlow experiment name
            run_name: MLFlow run name
            **kwargs: Additional arguments for execute_notebook
            
        Returns:
            NotebookResult with MLFlow run ID in metadata
        """
        try:
            import mlflow
        except ImportError:
            logger.warning("MLFlow not available, executing without tracking")
            return self.execute_notebook(notebook_path, parameters, **kwargs)
        
        notebook_path = Path(notebook_path)
        
        if experiment_name:
            mlflow.set_experiment(experiment_name)
        
        run_name = run_name or f"notebook_{notebook_path.stem}"
        
        with mlflow.start_run(run_name=run_name):
            # Log parameters
            if parameters:
                mlflow.log_params(parameters)
            
            # Execute notebook
            result = self.execute_notebook(notebook_path, parameters, **kwargs)
            
            # Log metrics
            mlflow.log_metric("duration_seconds", result.duration_seconds)
            mlflow.log_metric("success", 1 if result.success else 0)
            mlflow.log_metric("cell_count", len(result.cell_outputs))
            
            # Log artifacts
            if result.output_notebook_path:
                mlflow.log_artifact(result.output_notebook_path, "notebooks")
            
            for artifact_path in result.artifacts:
                mlflow.log_artifact(artifact_path, "artifacts")
            
            # Log run ID
            result.parameters["mlflow_run_id"] = mlflow.active_run().info.run_id
        
        return result


class JupyterServerManager:
    """
    Manage Jupyter server instances.
    
    Provides:
    - Server start/stop
    - Session management
    - Kernel lifecycle
    """
    
    def __init__(
        self,
        config: Optional[AgenticConfig] = None,
        notebook_dir: Optional[str] = None,
        port: int = 8888,
    ):
        """
        Initialize the Jupyter server manager.
        
        Args:
            config: Configuration instance
            notebook_dir: Root directory for notebooks
            port: Server port
        """
        self.config = config or AgenticConfig()
        self.notebook_dir = Path(notebook_dir) if notebook_dir else Path.cwd()
        self.port = port
        self._server_process = None
        self._sessions: Dict[str, KernelSession] = {}
    
    async def start_server(
        self,
        token: Optional[str] = None,
        open_browser: bool = False,
    ) -> Dict[str, Any]:
        """
        Start the Jupyter server.
        
        Args:
            token: Authentication token (generated if None)
            open_browser: Whether to open browser
            
        Returns:
            Server info dictionary
        """
        import secrets
        
        if self._server_process is not None:
            return {"status": "already_running", "port": self.port}
        
        token = token or secrets.token_urlsafe(32)
        
        cmd = [
            "jupyter", "notebook",
            f"--port={self.port}",
            f"--notebook-dir={self.notebook_dir}",
            f"--NotebookApp.token={token}",
            "--no-browser" if not open_browser else "",
        ]
        
        import subprocess
        self._server_process = subprocess.Popen(
            [c for c in cmd if c],  # Filter empty strings
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # Wait for server to start
        await asyncio.sleep(2)
        
        return {
            "status": "started",
            "port": self.port,
            "token": token,
            "url": f"http://localhost:{self.port}/?token={token}",
            "pid": self._server_process.pid,
        }
    
    def stop_server(self) -> bool:
        """Stop the Jupyter server."""
        if self._server_process is None:
            return False
        
        self._server_process.terminate()
        self._server_process.wait(timeout=10)
        self._server_process = None
        self._sessions.clear()
        
        return True
    
    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        if self._server_process is None:
            return False
        return self._server_process.poll() is None
    
    async def get_kernels(self, server_url: str, token: str) -> List[Dict]:
        """
        Get list of running kernels.
        
        Args:
            server_url: Jupyter server URL
            token: Authentication token
            
        Returns:
            List of kernel info dictionaries
        """
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{server_url}/api/kernels",
                headers={"Authorization": f"token {token}"},
            )
            response.raise_for_status()
            return response.json()
    
    async def start_kernel(
        self,
        server_url: str,
        token: str,
        kernel_name: str = "python3",
    ) -> Dict[str, Any]:
        """
        Start a new kernel.
        
        Args:
            server_url: Jupyter server URL
            token: Authentication token
            kernel_name: Kernel specification name
            
        Returns:
            Kernel info dictionary
        """
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{server_url}/api/kernels",
                headers={"Authorization": f"token {token}"},
                json={"name": kernel_name},
            )
            response.raise_for_status()
            
            kernel_info = response.json()
            
            # Track session
            session = KernelSession(
                session_id=kernel_info.get("id", ""),
                kernel_name=kernel_name,
                kernel_id=kernel_info.get("id", ""),
                started_at=datetime.utcnow(),
                status="starting",
            )
            self._sessions[session.session_id] = session
            
            return kernel_info
    
    async def stop_kernel(
        self,
        server_url: str,
        token: str,
        kernel_id: str,
    ) -> bool:
        """
        Stop a kernel.
        
        Args:
            server_url: Jupyter server URL
            token: Authentication token
            kernel_id: Kernel ID
            
        Returns:
            True if stopped successfully
        """
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{server_url}/api/kernels/{kernel_id}",
                headers={"Authorization": f"token {token}"},
            )
            
            if kernel_id in self._sessions:
                del self._sessions[kernel_id]
            
            return response.status_code == 204


class NotebookManager:
    """
    High-level notebook management.
    
    Combines executor, server manager, and MLFlow integration.
    """
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """Initialize notebook manager."""
        self.config = config or AgenticConfig()
        self.executor = NotebookExecutor(config)
        self.server_manager = JupyterServerManager(config)
    
    def run_notebook(
        self,
        notebook_path: str,
        parameters: Optional[Dict[str, Any]] = None,
        track_with_mlflow: bool = False,
        **kwargs,
    ) -> NotebookResult:
        """
        Run a notebook with optional MLFlow tracking.
        
        Args:
            notebook_path: Path to notebook
            parameters: Notebook parameters
            track_with_mlflow: Enable MLFlow tracking
            **kwargs: Additional executor arguments
            
        Returns:
            NotebookResult
        """
        if track_with_mlflow:
            return self.executor.execute_notebook_with_mlflow(
                notebook_path, parameters, **kwargs
            )
        return self.executor.execute_notebook(notebook_path, parameters, **kwargs)
    
    def batch_execute(
        self,
        notebooks: List[Dict[str, Any]],
        parallel: bool = False,
    ) -> Dict[str, NotebookResult]:
        """
        Execute multiple notebooks.
        
        Args:
            notebooks: List of dicts with "path" and optional "parameters"
            parallel: Run in parallel (not recommended for heavy notebooks)
            
        Returns:
            Dictionary mapping paths to results
        """
        results = {}
        
        for notebook_config in notebooks:
            path = notebook_config.get("path")
            params = notebook_config.get("parameters", {})
            
            try:
                result = self.run_notebook(path, params)
                results[path] = result
            except Exception as e:
                results[path] = NotebookResult(
                    notebook_path=path,
                    success=False,
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow(),
                    error=str(e),
                )
        
        return results
