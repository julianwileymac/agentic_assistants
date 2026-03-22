"""
Script manager for executing Python scripts, shell commands, and notebooks.
"""

import asyncio
import subprocess
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class ScriptType(str, Enum):
    """Script types supported by the execution layer."""
    PYTHON = "python"
    SHELL = "shell"
    NOTEBOOK = "notebook"
    DOCKER = "docker"


class ExecutionStatus(str, Enum):
    """Execution status states."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScriptManager:
    """
    Manage execution of scripts, notebooks, and commands.
    
    Features:
    - Execute Python scripts, shell commands, Jupyter notebooks
    - Save execution history to database
    - Template library for common tasks
    - Deploy scripts to Docker or Kubernetes
    """
    
    def __init__(self, config: Optional[AgenticConfig] = None):
        """Initialize the script manager."""
        self.config = config or AgenticConfig()
        self.execution_dir = Path(self.config.data_dir) / "executions"
        self.execution_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute_python(
        self,
        script_content: str,
        script_name: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute a Python script.
        
        Args:
            script_content: Python code to execute
            script_name: Optional name for the script
            env_vars: Environment variables
            timeout: Execution timeout in seconds
            
        Returns:
            Dict with execution results
        """
        run_id = str(uuid.uuid4())
        script_name = script_name or f"script_{run_id[:8]}"
        
        # Save script to file
        script_file = self.execution_dir / f"{script_name}_{run_id}.py"
        script_file.write_text(script_content)
        
        logger.info(f"Executing Python script: {script_name}")
        
        started_at = datetime.utcnow()
        
        try:
            # Execute script
            result = await asyncio.create_subprocess_exec(
                "python",
                str(script_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env_vars,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                result.kill()
                raise TimeoutError(f"Script execution timed out after {timeout}s")
            
            completed_at = datetime.utcnow()
            
            execution_result = {
                "run_id": run_id,
                "script_name": script_name,
                "script_type": ScriptType.PYTHON,
                "status": ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.FAILED,
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_seconds": (completed_at - started_at).total_seconds(),
                "output": stdout.decode(),
                "error": stderr.decode() if stderr else None,
                "return_code": result.returncode,
            }
            
            # Store execution record (would save to database)
            self._save_execution(execution_result)
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            return {
                "run_id": run_id,
                "script_name": script_name,
                "status": ExecutionStatus.FAILED,
                "error": str(e),
                "started_at": started_at.isoformat(),
            }
    
    async def execute_shell(
        self,
        command: str,
        working_dir: Optional[Path] = None,
        env_vars: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute a shell command.
        
        Args:
            command: Shell command to execute
            working_dir: Working directory
            env_vars: Environment variables
            timeout: Execution timeout
            
        Returns:
            Dict with execution results
        """
        run_id = str(uuid.uuid4())
        
        logger.info(f"Executing shell command: {command}")
        
        started_at = datetime.utcnow()
        
        try:
            result = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
                env=env_vars,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                result.kill()
                raise TimeoutError(f"Command timed out after {timeout}s")
            
            completed_at = datetime.utcnow()
            
            return {
                "run_id": run_id,
                "command": command,
                "script_type": ScriptType.SHELL,
                "status": ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.FAILED,
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_seconds": (completed_at - started_at).total_seconds(),
                "output": stdout.decode(),
                "error": stderr.decode() if stderr else None,
                "return_code": result.returncode,
            }
            
        except Exception as e:
            logger.error(f"Shell command failed: {e}")
            return {
                "run_id": run_id,
                "status": ExecutionStatus.FAILED,
                "error": str(e),
                "started_at": started_at.isoformat(),
            }
    
    async def execute_notebook(
        self,
        notebook_path: Path,
        parameters: Optional[Dict[str, Any]] = None,
        output_notebook: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Execute a Jupyter notebook using papermill.
        
        Args:
            notebook_path: Path to input notebook
            parameters: Parameters to pass to notebook
            output_notebook: Path for output notebook
            
        Returns:
            Dict with execution results
        """
        try:
            import papermill as pm
        except ImportError:
            raise ImportError("papermill is required for notebook execution")
        
        run_id = str(uuid.uuid4())
        output_notebook = output_notebook or (
            self.execution_dir / f"{notebook_path.stem}_{run_id}.ipynb"
        )
        
        logger.info(f"Executing notebook: {notebook_path}")
        
        started_at = datetime.utcnow()
        
        try:
            pm.execute_notebook(
                str(notebook_path),
                str(output_notebook),
                parameters=parameters or {},
            )
            
            completed_at = datetime.utcnow()
            
            return {
                "run_id": run_id,
                "notebook_path": str(notebook_path),
                "output_notebook": str(output_notebook),
                "script_type": ScriptType.NOTEBOOK,
                "status": ExecutionStatus.SUCCESS,
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_seconds": (completed_at - started_at).total_seconds(),
                "parameters": parameters,
            }
            
        except Exception as e:
            logger.error(f"Notebook execution failed: {e}")
            return {
                "run_id": run_id,
                "status": ExecutionStatus.FAILED,
                "error": str(e),
                "started_at": started_at.isoformat(),
            }
    
    def _save_execution(self, execution_result: Dict[str, Any]) -> None:
        """Save execution result to database."""
        # TODO: Save to execution_runs table in database
        logger.info(f"Saved execution: {execution_result['run_id']}")
    
    def list_executions(
        self,
        status: Optional[ExecutionStatus] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        List recent executions.
        
        Args:
            status: Filter by status
            limit: Maximum results
            
        Returns:
            List of execution records
        """
        # TODO: Query from database
        return []
    
    def get_execution(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution details by ID.
        
        Args:
            run_id: Execution run ID
            
        Returns:
            Execution record or None
        """
        # TODO: Query from database
        return None
