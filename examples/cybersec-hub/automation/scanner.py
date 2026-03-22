"""
Automated Scanner Workflows.

Orchestrates multi-stage scanning operations.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class ScanPhase(str, Enum):
    """Scan workflow phases."""
    DISCOVERY = "discovery"
    ENUMERATION = "enumeration"
    VULNERABILITY = "vulnerability"
    EXPLOITATION = "exploitation"
    POST_EXPLOIT = "post_exploitation"


@dataclass
class ScanStep:
    """Individual scan step."""
    step_id: str
    phase: ScanPhase
    tool: str
    options: List[str]
    depends_on: List[str]
    timeout: int
    retry_count: int = 0


@dataclass
class ScanWorkflow:
    """Complete scan workflow."""
    workflow_id: str
    name: str
    description: str
    target: str
    steps: List[ScanStep]
    schedule: Optional[str]  # Cron expression
    metadata: Dict[str, Any]


class ScannerWorkflow:
    """
    Automated scanning workflow orchestration.
    
    Example:
        >>> workflow = ScannerWorkflow()
        >>> workflow.add_step("discovery", tool="nmap", options=["-sn"])
        >>> workflow.add_step("ports", tool="nmap", options=["-p-"], depends_on=["discovery"])
        >>> result = workflow.execute(target="192.168.1.0/24")
    """
    
    def __init__(self, tool_manager=None):
        """Initialize scanner workflow."""
        self.tool_manager = tool_manager
        self.steps = []
        self.results = {}
        
        logger.info("ScannerWorkflow initialized")
    
    def add_step(
        self,
        step_id: str,
        tool: str,
        options: Optional[List[str]] = None,
        phase: ScanPhase = ScanPhase.DISCOVERY,
        depends_on: Optional[List[str]] = None,
        timeout: int = 600
    ):
        """Add step to workflow."""
        step = ScanStep(
            step_id=step_id,
            phase=phase,
            tool=tool,
            options=options or [],
            depends_on=depends_on or [],
            timeout=timeout
        )
        self.steps.append(step)
        logger.debug(f"Added step: {step_id} ({tool})")
    
    def execute(self, target: str) -> Dict[str, Any]:
        """Execute complete workflow."""
        logger.info(f"Executing workflow on {target}")
        
        start_time = datetime.now()
        results = {}
        
        # Execute steps in order, respecting dependencies
        for step in self._order_steps():
            logger.info(f"Executing step: {step.step_id}")
            
            try:
                result = self._execute_step(step, target)
                results[step.step_id] = result
                self.results = results
            except Exception as e:
                logger.error(f"Step {step.step_id} failed: {e}")
                results[step.step_id] = {"error": str(e)}
        
        end_time = datetime.now()
        
        return {
            "target": target,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": (end_time - start_time).total_seconds(),
            "steps": results,
            "success": all(r.get("success", False) for r in results.values())
        }
    
    def _order_steps(self) -> List[ScanStep]:
        """Order steps based on dependencies."""
        # Simple topological sort
        ordered = []
        completed = set()
        
        while len(ordered) < len(self.steps):
            for step in self.steps:
                if step.step_id in completed:
                    continue
                
                # Check if dependencies are met
                if all(dep in completed for dep in step.depends_on):
                    ordered.append(step)
                    completed.add(step.step_id)
        
        return ordered
    
    def _execute_step(self, step: ScanStep, target: str) -> Dict[str, Any]:
        """Execute individual step."""
        if not self.tool_manager:
            return {
                "success": False,
                "error": "Tool manager not available"
            }
        
        result = self.tool_manager.execute(
            tool=step.tool,
            target=target,
            options=step.options,
            timeout=step.timeout
        )
        
        return {
            "success": result.success,
            "output": result.stdout,
            "error": result.stderr if not result.success else None,
            "duration": result.duration
        }
    
    def schedule(self, cron_expression: str):
        """Schedule workflow for recurring execution."""
        logger.info(f"Workflow scheduled: {cron_expression}")
        # In production, this would integrate with Kubernetes CronJobs
        return cron_expression


__all__ = ["ScannerWorkflow", "ScanWorkflow", "ScanStep", "ScanPhase"]
