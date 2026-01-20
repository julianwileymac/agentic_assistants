"""
Human-in-the-Loop (HITL) nodes.

This module provides flow nodes for human intervention:
- HumanReviewNode: Queue output for human review
- ApprovalGateNode: Require human approval to proceed
- FeedbackNode: Collect human feedback

These nodes support asynchronous workflows where human input
is required before proceeding.

Example:
    >>> from agentic_assistants.pipelines.nodes import HumanReviewNode
    >>> 
    >>> review = HumanReviewNode(config=HumanReviewConfig(
    ...     assignee="reviewer@example.com",
    ...     timeout=3600,
    ... ))
    >>> 
    >>> result = review.run({"content": "Review this response..."})
    >>> print(result.outputs["task_id"])  # Returns task ID for async processing
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from agentic_assistants.pipelines.nodes.base import BaseFlowNode, NodeConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Configuration Classes
# =============================================================================

@dataclass
class HumanReviewConfig(NodeConfig):
    """Configuration for HumanReviewNode."""
    
    # Assignee for the review task
    assignee: str = ""
    
    # Timeout in seconds before auto-continuing
    timeout: int = 3600
    
    # Instructions for the reviewer
    instructions: str = ""
    
    # Webhook URL to notify when submitted
    webhook_url: str = ""
    
    # Whether to block until review is complete
    blocking: bool = True
    
    # Priority level
    priority: str = "normal"  # low, normal, high, critical


@dataclass
class ApprovalGateConfig(NodeConfig):
    """Configuration for ApprovalGateNode."""
    
    # List of approver identifiers
    approvers: List[str] = field(default_factory=list)
    
    # Minimum number of approvals required
    min_approvals: int = 1
    
    # Timeout in seconds
    timeout: int = 86400  # 24 hours
    
    # Whether rejection should fail the flow
    fail_on_reject: bool = True
    
    # Custom approval message
    approval_message: str = ""


@dataclass
class FeedbackConfig(NodeConfig):
    """Configuration for FeedbackNode."""
    
    # Type of feedback: rating, binary, text, ranking
    feedback_type: str = "rating"
    
    # Rating scale (for rating type)
    rating_scale: int = 5
    
    # Whether to emit feedback as RL metric
    emit_rl_metric: bool = True
    
    # RL metric name
    metric_name: str = "human_feedback"
    
    # Required or optional
    required: bool = True


# =============================================================================
# Task Store (In-memory for demo, would use database in production)
# =============================================================================

class HITLTaskStore:
    """Simple in-memory store for HITL tasks."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tasks: Dict[str, Dict[str, Any]] = {}
        return cls._instance
    
    def create_task(
        self,
        task_type: str,
        content: Any,
        metadata: Dict[str, Any],
    ) -> str:
        """Create a new HITL task."""
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "content": content,
            "metadata": metadata,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "result": None,
        }
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID."""
        return self._tasks.get(task_id)
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update a task."""
        if task_id in self._tasks:
            self._tasks[task_id].update(updates)
            return True
        return False
    
    def complete_task(self, task_id: str, result: Any) -> bool:
        """Mark a task as complete."""
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = "completed"
            self._tasks[task_id]["result"] = result
            self._tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()
            return True
        return False
    
    def list_pending_tasks(self, task_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List pending tasks."""
        tasks = [t for t in self._tasks.values() if t["status"] == "pending"]
        if task_type:
            tasks = [t for t in tasks if t["type"] == task_type]
        return tasks


def get_hitl_store() -> HITLTaskStore:
    """Get the HITL task store instance."""
    return HITLTaskStore()


# =============================================================================
# Node Implementations
# =============================================================================

class HumanReviewNode(BaseFlowNode):
    """
    Node for queuing content for human review.
    
    This node creates a review task and optionally blocks until
    the review is complete.
    
    Inputs:
        content: The content to review
        context: Additional context for the reviewer
        
    Outputs:
        task_id: ID of the created review task
        status: Current status (pending/completed)
        result: Review result (if completed)
    """
    
    node_type = "human_review"
    config_class = HumanReviewConfig
    
    def __init__(self, config: Optional[HumanReviewConfig] = None, **kwargs):
        super().__init__(config or HumanReviewConfig(), **kwargs)
        self.config: HumanReviewConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        content = inputs.get("content", "")
        context = inputs.get("context", {})
        
        store = get_hitl_store()
        
        # Create review task
        task_id = store.create_task(
            task_type="review",
            content=content,
            metadata={
                "assignee": self.config.assignee,
                "instructions": self.config.instructions,
                "priority": self.config.priority,
                "timeout": self.config.timeout,
                "context": context,
                "node_id": self.config.node_id,
            },
        )
        
        logger.info(f"Created human review task: {task_id}")
        
        # Emit metric
        self.emit_metric("review_tasks_created", 1)
        
        # If non-blocking, return immediately
        if not self.config.blocking:
            return {
                "task_id": task_id,
                "status": "pending",
                "result": None,
            }
        
        # For blocking mode, we return the task info
        # In a real implementation, this would wait or use callbacks
        task = store.get_task(task_id)
        
        return {
            "task_id": task_id,
            "status": task["status"] if task else "unknown",
            "result": task.get("result") if task else None,
        }
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "context": {"type": "object"},
            },
            "required": ["content"],
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "status": {"type": "string"},
                "result": {},
            },
        }


class ApprovalGateNode(BaseFlowNode):
    """
    Node for requiring human approval to proceed.
    
    Creates an approval request that must be approved by the
    specified approvers before the flow continues.
    
    Inputs:
        content: Content requiring approval
        reason: Reason for requiring approval
        
    Outputs:
        task_id: Approval task ID
        approved: Whether approval was granted
        approvals: List of approvals received
    """
    
    node_type = "approval_gate"
    config_class = ApprovalGateConfig
    
    def __init__(self, config: Optional[ApprovalGateConfig] = None, **kwargs):
        super().__init__(config or ApprovalGateConfig(), **kwargs)
        self.config: ApprovalGateConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        content = inputs.get("content", "")
        reason = inputs.get("reason", "")
        
        store = get_hitl_store()
        
        # Create approval task
        task_id = store.create_task(
            task_type="approval",
            content=content,
            metadata={
                "approvers": self.config.approvers,
                "min_approvals": self.config.min_approvals,
                "approval_message": self.config.approval_message or reason,
                "timeout": self.config.timeout,
                "node_id": self.config.node_id,
                "approvals": [],
                "rejections": [],
            },
        )
        
        logger.info(f"Created approval gate task: {task_id}")
        
        # Emit metric
        self.emit_metric("approval_gates_created", 1)
        
        # Return task info (in real implementation, would wait for approval)
        return {
            "task_id": task_id,
            "approved": False,  # Will be updated when approvals come in
            "approvals": [],
            "status": "pending",
        }
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {},
                "reason": {"type": "string"},
            },
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "approved": {"type": "boolean"},
                "approvals": {"type": "array"},
                "status": {"type": "string"},
            },
        }


class FeedbackNode(BaseFlowNode):
    """
    Node for collecting human feedback.
    
    Creates a feedback request and captures the response for
    use in RL training or quality monitoring.
    
    Inputs:
        content: Content to get feedback on
        query: Original query (for context)
        response: Generated response (if applicable)
        
    Outputs:
        task_id: Feedback task ID
        feedback: Collected feedback (if available)
        score: Normalized feedback score (0-1)
    """
    
    node_type = "feedback"
    config_class = FeedbackConfig
    
    def __init__(self, config: Optional[FeedbackConfig] = None, **kwargs):
        super().__init__(config or FeedbackConfig(), **kwargs)
        self.config: FeedbackConfig
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        content = inputs.get("content", "")
        query = inputs.get("query", "")
        response = inputs.get("response", "")
        
        store = get_hitl_store()
        
        # Create feedback task
        task_id = store.create_task(
            task_type="feedback",
            content={
                "content": content,
                "query": query,
                "response": response,
            },
            metadata={
                "feedback_type": self.config.feedback_type,
                "rating_scale": self.config.rating_scale,
                "required": self.config.required,
                "node_id": self.config.node_id,
            },
        )
        
        logger.info(f"Created feedback task: {task_id}")
        
        # Emit metric
        self.emit_metric("feedback_requests_created", 1)
        
        # Return task info
        return {
            "task_id": task_id,
            "feedback": None,
            "score": None,
            "status": "pending",
        }
    
    def process_feedback(self, task_id: str, feedback: Any) -> Dict[str, Any]:
        """
        Process received feedback.
        
        This method should be called when feedback is received
        to calculate the score and emit RL metrics.
        """
        store = get_hitl_store()
        task = store.get_task(task_id)
        
        if not task:
            return {"error": "Task not found"}
        
        # Calculate normalized score based on feedback type
        score = 0.5
        
        if self.config.feedback_type == "rating":
            if isinstance(feedback, (int, float)):
                score = feedback / self.config.rating_scale
        elif self.config.feedback_type == "binary":
            score = 1.0 if feedback else 0.0
        elif self.config.feedback_type == "ranking":
            # For ranking, would need more complex processing
            score = 0.5
        
        # Emit RL metric
        if self.config.emit_rl_metric:
            self.emit_rl_metric(self.config.metric_name, score)
        
        # Update task
        store.complete_task(task_id, {
            "feedback": feedback,
            "score": score,
        })
        
        return {
            "task_id": task_id,
            "feedback": feedback,
            "score": score,
            "status": "completed",
        }
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {},
                "query": {"type": "string"},
                "response": {"type": "string"},
            },
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "feedback": {},
                "score": {"type": "number"},
                "status": {"type": "string"},
            },
        }
