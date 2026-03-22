"""
Evaluation Agent.

Runs evaluation benchmarks and produces comparison reports
across training runs and model checkpoints.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class EvalResult:
    """Result from a single evaluation task."""
    task_id: str
    passed: bool
    score: float
    generated_code: str
    expected_output: Optional[str] = None
    actual_output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalReport:
    """Aggregated evaluation report."""
    model_id: str
    benchmark: str
    total_tasks: int
    passed: int
    failed: int
    pass_rate: float
    metrics: Dict[str, float] = field(default_factory=dict)
    results: List[EvalResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EvaluationAgent:
    """
    Agent for evaluating model performance on coding benchmarks.

    Runs standardized benchmarks (HumanEval, MBPP) and custom tasks,
    produces comparison reports, and identifies model strengths/weaknesses.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        model_manager: Optional[Any] = None,
    ):
        self.config = config or {}
        self.model_manager = model_manager
        self.llm_config = self.config.get("llm", {})

    def evaluate_model(
        self,
        model_path: str,
        benchmark: str = "humaneval",
        k_values: Optional[List[int]] = None,
    ) -> EvalReport:
        """Evaluate a model on a specified benchmark."""
        k_values = k_values or [1, 10]
        logger.info(f"Evaluating {model_path} on {benchmark}")

        if benchmark == "humaneval":
            return self._run_humaneval(model_path, k_values)
        elif benchmark == "mbpp":
            return self._run_mbpp(model_path, k_values)
        elif benchmark == "custom":
            return self._run_custom(model_path)
        else:
            raise ValueError(f"Unknown benchmark: {benchmark}")

    def compare_models(
        self,
        reports: List[EvalReport],
    ) -> Dict[str, Any]:
        """Compare evaluation results across multiple models."""
        if not reports:
            return {"error": "No reports to compare"}

        comparison = {
            "models": [],
            "best_overall": None,
            "best_per_metric": {},
        }

        for report in reports:
            model_summary = {
                "model_id": report.model_id,
                "benchmark": report.benchmark,
                "pass_rate": report.pass_rate,
                "metrics": report.metrics,
            }
            comparison["models"].append(model_summary)

        best = max(reports, key=lambda r: r.pass_rate)
        comparison["best_overall"] = best.model_id

        all_metrics = set()
        for report in reports:
            all_metrics.update(report.metrics.keys())

        for metric in all_metrics:
            best_for_metric = max(
                reports,
                key=lambda r: r.metrics.get(metric, 0),
            )
            comparison["best_per_metric"][metric] = {
                "model_id": best_for_metric.model_id,
                "value": best_for_metric.metrics.get(metric, 0),
            }

        return comparison

    def analyze_failures(
        self,
        report: EvalReport,
    ) -> Dict[str, Any]:
        """Analyze failure patterns in evaluation results."""
        failures = [r for r in report.results if not r.passed]

        analysis = {
            "total_failures": len(failures),
            "failure_categories": {},
            "common_errors": [],
            "suggestions": [],
        }

        error_types: Dict[str, int] = {}
        for failure in failures:
            error = failure.error or "unknown"
            if "SyntaxError" in error:
                category = "syntax"
            elif "NameError" in error or "AttributeError" in error:
                category = "reference"
            elif "TypeError" in error:
                category = "type"
            elif "TimeoutError" in error or "timeout" in error.lower():
                category = "timeout"
            else:
                category = "logic"

            error_types[category] = error_types.get(category, 0) + 1

        analysis["failure_categories"] = error_types

        if error_types.get("syntax", 0) > len(failures) * 0.3:
            analysis["suggestions"].append(
                "High syntax error rate. Consider adding more syntactically correct "
                "examples to the training set."
            )
        if error_types.get("logic", 0) > len(failures) * 0.5:
            analysis["suggestions"].append(
                "Many logic errors. Consider increasing training data complexity "
                "or adding chain-of-thought examples."
            )

        return analysis

    def _run_humaneval(
        self,
        model_path: str,
        k_values: List[int],
    ) -> EvalReport:
        """Run HumanEval benchmark (placeholder for actual integration)."""
        logger.info(f"Running HumanEval on {model_path}")

        results = []
        metrics = {f"pass@{k}": 0.0 for k in k_values}

        return EvalReport(
            model_id=model_path,
            benchmark="humaneval",
            total_tasks=164,
            passed=0,
            failed=164,
            pass_rate=0.0,
            metrics=metrics,
            results=results,
            metadata={"k_values": k_values, "status": "pending_execution"},
        )

    def _run_mbpp(
        self,
        model_path: str,
        k_values: List[int],
    ) -> EvalReport:
        """Run MBPP benchmark (placeholder for actual integration)."""
        logger.info(f"Running MBPP on {model_path}")

        results = []
        metrics = {f"pass@{k}": 0.0 for k in k_values}

        return EvalReport(
            model_id=model_path,
            benchmark="mbpp",
            total_tasks=500,
            passed=0,
            failed=500,
            pass_rate=0.0,
            metrics=metrics,
            results=results,
            metadata={"k_values": k_values, "status": "pending_execution"},
        )

    def _run_custom(self, model_path: str) -> EvalReport:
        """Run custom coding tasks."""
        logger.info(f"Running custom benchmark on {model_path}")
        return EvalReport(
            model_id=model_path,
            benchmark="custom",
            total_tasks=0,
            passed=0,
            failed=0,
            pass_rate=0.0,
            metadata={"status": "pending_task_loading"},
        )
