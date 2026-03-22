"""
Benchmark runners for evaluating coding model performance.

Supports HumanEval, MBPP, and custom coding task benchmarks.
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger
from .metrics import CodingMetrics

logger = get_logger(__name__)


@dataclass
class BenchmarkTask:
    """A single benchmark task."""
    task_id: str
    prompt: str
    canonical_solution: str = ""
    test_code: str = ""
    entry_point: str = ""
    language: str = "python"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """Result of running a single benchmark task."""
    task_id: str
    generated: str
    passed: bool
    score: float = 0.0
    execution_output: Optional[str] = None
    error: Optional[str] = None
    latency_ms: float = 0.0


@dataclass
class BenchmarkReport:
    """Aggregated benchmark report."""
    benchmark_name: str
    model_path: str
    total_tasks: int
    passed: int
    metrics: Dict[str, float] = field(default_factory=dict)
    results: List[BenchmarkResult] = field(default_factory=list)
    total_time_seconds: float = 0.0


class BenchmarkRunner:
    """
    Runs coding evaluation benchmarks against a model.

    Loads benchmark tasks, generates completions, executes tests,
    and computes metrics (pass@k, BLEU, syntax correctness).
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metrics = CodingMetrics()

    def run(
        self,
        model_path: str,
        benchmarks: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Run all configured benchmarks."""
        benchmark_configs = self.config.get("benchmarks", [])
        if benchmarks:
            benchmark_configs = [b for b in benchmark_configs if b["name"] in benchmarks]

        reports = []
        for bench_cfg in benchmark_configs:
            if not bench_cfg.get("enabled", True):
                continue
            name = bench_cfg["name"]
            logger.info(f"Running benchmark: {name}")
            report = self._run_benchmark(
                name=name,
                model_path=model_path,
                config=bench_cfg,
            )
            reports.append(report)

        return {
            "model_path": model_path,
            "benchmarks": [
                {
                    "name": r.benchmark_name,
                    "total": r.total_tasks,
                    "passed": r.passed,
                    "metrics": r.metrics,
                    "time_seconds": r.total_time_seconds,
                }
                for r in reports
            ],
        }

    def _run_benchmark(
        self,
        name: str,
        model_path: str,
        config: Dict[str, Any],
    ) -> BenchmarkReport:
        """Run a single benchmark."""
        start = time.time()

        if name == "humaneval":
            tasks = self._load_humaneval()
        elif name == "mbpp":
            tasks = self._load_mbpp()
        elif name == "custom-coding":
            task_path = config.get("path", "")
            tasks = self._load_custom(task_path)
        else:
            logger.warning(f"Unknown benchmark: {name}")
            tasks = []

        results = []
        for task in tasks:
            result = self._evaluate_task(task, model_path)
            results.append(result)

        passed = sum(1 for r in results if r.passed)
        k_values = config.get("k_values", [1])

        metrics: Dict[str, float] = {}
        if results:
            generations = [[r.generated] for r in results]
            references = [tasks[i].canonical_solution for i in range(len(results))]
            for k in k_values:
                metrics[f"pass@{k}"] = self.metrics.pass_at_k(
                    n_samples=[1] * len(results),
                    n_correct=[int(r.passed) for r in results],
                    k=k,
                )
            metrics["syntax_correctness"] = self.metrics.syntax_correctness_rate(
                [r.generated for r in results]
            )

        return BenchmarkReport(
            benchmark_name=name,
            model_path=model_path,
            total_tasks=len(tasks),
            passed=passed,
            metrics=metrics,
            results=results,
            total_time_seconds=time.time() - start,
        )

    def _evaluate_task(
        self, task: BenchmarkTask, model_path: str,
    ) -> BenchmarkResult:
        """Generate and evaluate a single task."""
        start = time.time()
        generated = self._generate(task.prompt, model_path)
        latency = (time.time() - start) * 1000

        passed = False
        error = None
        execution_output = None

        if task.test_code:
            passed, execution_output, error = self._execute_test(
                generated, task.test_code, task.entry_point,
            )
        else:
            passed = bool(generated.strip())

        return BenchmarkResult(
            task_id=task.task_id,
            generated=generated,
            passed=passed,
            score=1.0 if passed else 0.0,
            execution_output=execution_output,
            error=error,
            latency_ms=latency,
        )

    def _generate(self, prompt: str, model_path: str) -> str:
        """Generate a completion (placeholder -- wire to actual model)."""
        try:
            import httpx
            response = httpx.post(
                "http://localhost:11434/api/generate",
                json={"model": "nemotron-nano-coding", "prompt": prompt, "stream": False},
                timeout=120,
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            logger.warning(f"Generation failed: {e}")
            return ""

    def _execute_test(
        self, code: str, test_code: str, entry_point: str,
    ) -> tuple:
        """Execute generated code against test cases."""
        import subprocess
        import tempfile

        full_code = f"{code}\n\n{test_code}"
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as f:
                f.write(full_code)
                tmp = f.name

            result = subprocess.run(
                ["python", tmp],
                capture_output=True, text=True, timeout=30,
            )
            passed = result.returncode == 0
            return passed, result.stdout, result.stderr or None
        except subprocess.TimeoutExpired:
            return False, None, "Execution timed out"
        except Exception as e:
            return False, None, str(e)

    def _load_humaneval(self) -> List[BenchmarkTask]:
        """Load HumanEval tasks (placeholder)."""
        logger.info("Loading HumanEval benchmark (requires human-eval package)")
        return []

    def _load_mbpp(self) -> List[BenchmarkTask]:
        """Load MBPP tasks (placeholder)."""
        logger.info("Loading MBPP benchmark")
        return []

    def _load_custom(self, path: str) -> List[BenchmarkTask]:
        """Load custom benchmark tasks from a JSONL file."""
        tasks = []
        p = Path(path)
        if not p.exists():
            logger.warning(f"Custom benchmark file not found: {path}")
            return tasks

        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                tasks.append(BenchmarkTask(
                    task_id=data.get("task_id", f"custom_{len(tasks)}"),
                    prompt=data.get("prompt", ""),
                    canonical_solution=data.get("canonical_solution", ""),
                    test_code=data.get("test", ""),
                    entry_point=data.get("entry_point", ""),
                    language=data.get("language", "python"),
                ))

        logger.info(f"Loaded {len(tasks)} custom tasks from {path}")
        return tasks
