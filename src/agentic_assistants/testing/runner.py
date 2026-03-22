"""
Test execution utilities for the Agentic framework.
"""

from __future__ import annotations

import asyncio
import io
import json
import time
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.mlflow_tracker import MLFlowTracker
from agentic_assistants.training.datasets import TrainingDatasetManager
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TestExecutionResult:
    passed: bool
    output: Dict[str, Any]
    metrics: Dict[str, Any]
    error_message: Optional[str] = None
    evaluation: Optional[Dict[str, Any]] = None


class TestRunner:
    """Run sandboxed tests with optional tracking and evaluation."""

    def __init__(self, config: Optional[AgenticConfig] = None):
        self.config = config or AgenticConfig()
        self.dataset_manager = TrainingDatasetManager()

    def load_dataset_samples(
        self,
        dataset_id: Optional[str],
        sample_size: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Load dataset samples for tests."""
        if not dataset_id:
            return []
        dataset = self.dataset_manager.get(dataset_id)
        if not dataset:
            dataset = self.dataset_manager.get_by_name(dataset_id)
        if not dataset:
            return []
        limit = sample_size or self.config.testing.dataset_sample_size
        return dataset.load_samples(limit=limit)

    async def run_test(
        self,
        code: str,
        language: str = "python",
        input_data: Optional[Any] = None,
        expected_output: Optional[Any] = None,
        dataset_id: Optional[str] = None,
        sandbox_enabled: Optional[bool] = None,
        tracking_enabled: Optional[bool] = None,
        agent_eval_enabled: Optional[bool] = None,
        rl_metrics_enabled: Optional[bool] = None,
        run_name: Optional[str] = None,
        evaluation_context: Optional[str] = None,
        evaluation_query: Optional[str] = None,
        evaluation_provider: Optional[str] = None,
        evaluation_model: Optional[str] = None,
        evaluation_endpoint: Optional[str] = None,
        evaluation_api_key_env: Optional[str] = None,
        evaluation_hf_execution_mode: Optional[str] = None,
        log_callback: Optional[Callable[[str, str], Any]] = None,
    ) -> TestExecutionResult:
        """Execute a test with optional tracking and evaluation."""
        sandbox = self._resolve_flag(sandbox_enabled, self.config.testing.sandbox_default)
        tracking = self._resolve_flag(tracking_enabled, self.config.testing.tracking_default)
        agent_eval = self._resolve_flag(agent_eval_enabled, self.config.testing.agent_eval_default)
        rl_metrics = self._resolve_flag(rl_metrics_enabled, self.config.testing.rl_metrics_default)

        dataset_samples = self.load_dataset_samples(dataset_id)
        prepared_input = self._normalize_input(input_data)
        prepared_expected = self._normalize_expected(expected_output)

        tracker: Optional[MLFlowTracker] = None
        if tracking and self.config.mlflow_enabled:
            tracker = MLFlowTracker(self.config)
            tracker.enabled = True

        if log_callback:
            await self._emit_log(log_callback, "Starting test execution.", "INFO")

        start_time = time.time()
        metrics: Dict[str, Any] = {}
        evaluation: Optional[Dict[str, Any]] = None

        try:
            with tracker.start_run(run_name=run_name) if tracker else _null_context():
                if tracker:
                    tracker.log_params(
                        {
                            "language": language,
                            "sandbox_enabled": sandbox,
                            "agent_eval_enabled": agent_eval,
                            "rl_metrics_enabled": rl_metrics,
                            "dataset_id": dataset_id or "",
                            "evaluation_provider": evaluation_provider or self.config.testing.eval_provider or "",
                            "evaluation_model": evaluation_model or self.config.testing.eval_model or "",
                            "evaluation_endpoint": evaluation_endpoint or self.config.testing.eval_endpoint or "",
                            "evaluation_hf_execution_mode": evaluation_hf_execution_mode or self.config.testing.eval_hf_execution_mode,
                        }
                    )

                output = await self._execute_code(
                    code=code,
                    language=language,
                    input_data=prepared_input,
                    expected_output=prepared_expected,
                    dataset_samples=dataset_samples,
                    sandbox=sandbox,
                )

                metrics.update(output.pop("metrics", {}))

                if agent_eval:
                    evaluation = await self._evaluate_output(
                        query=evaluation_query,
                        response=str(output.get("result", "")),
                        context=evaluation_context,
                        tracker=tracker,
                        rl_metrics=rl_metrics,
                        evaluation_provider=evaluation_provider,
                        evaluation_model=evaluation_model,
                        evaluation_endpoint=evaluation_endpoint,
                        evaluation_api_key_env=evaluation_api_key_env,
                    )
                    if evaluation and evaluation.get("metrics"):
                        metrics.update(evaluation["metrics"])

                if rl_metrics:
                    metrics.setdefault("rl/test/passed", 1.0 if output["passed"] else 0.0)

                if tracker:
                    for name, value in metrics.items():
                        if isinstance(value, (int, float)):
                            tracker.log_metric(name, float(value))

        except Exception as exc:
            duration = time.time() - start_time
            metrics["execution_time_s"] = duration
            if log_callback:
                await self._emit_log(log_callback, f"Test failed: {exc}", "ERROR")
            return TestExecutionResult(
                passed=False,
                output={
                    "stdout": "",
                    "stderr": str(exc),
                    "result": None,
                },
                metrics=metrics,
                error_message=str(exc),
                evaluation=evaluation,
            )

        duration = time.time() - start_time
        metrics["execution_time_s"] = duration

        if log_callback:
            await self._emit_log(log_callback, f"Test completed in {duration:.2f}s.", "INFO")

        return TestExecutionResult(
            passed=bool(output["passed"]),
            output=output,
            metrics=metrics,
            evaluation=evaluation,
        )

    async def _execute_code(
        self,
        code: str,
        language: str,
        input_data: Optional[Any],
        expected_output: Optional[Any],
        dataset_samples: List[Dict[str, Any]],
        sandbox: bool,
    ) -> Dict[str, Any]:
        if language.lower() != "python":
            raise ValueError(f"Unsupported language: {language}")

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        local_vars: Dict[str, Any] = {
            "input_data": input_data,
            "dataset": dataset_samples,
            "dataset_samples": dataset_samples,
        }

        restricted_globals = self._build_globals(sandbox)

        def _execute() -> None:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, restricted_globals, local_vars)

        timeout = self.config.testing.timeout_seconds or None
        if timeout:
            await asyncio.wait_for(asyncio.to_thread(_execute), timeout=timeout)
        else:
            await asyncio.to_thread(_execute)

        stdout_value = stdout_capture.getvalue()
        stderr_value = stderr_capture.getvalue()
        result_value = local_vars.get("result")
        passed_override = local_vars.get("passed", None)

        passed = self._determine_passed(
            passed_override=passed_override,
            expected_output=expected_output,
            result_value=result_value,
            stderr_value=stderr_value,
        )

        metrics = {
            "output_stdout_len": len(stdout_value),
            "output_stderr_len": len(stderr_value),
        }

        return {
            "passed": passed,
            "result": result_value,
            "stdout": self._truncate(stdout_value),
            "stderr": self._truncate(stderr_value),
            "metrics": metrics,
        }

    async def _evaluate_output(
        self,
        query: Optional[str],
        response: str,
        context: Optional[str],
        tracker: Optional[MLFlowTracker],
        rl_metrics: bool,
        evaluation_provider: Optional[str],
        evaluation_model: Optional[str],
        evaluation_endpoint: Optional[str],
        evaluation_api_key_env: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        if not response:
            return None

        try:
            from agentic_assistants.pipelines.nodes.eval_nodes import LLMJudgeNode, LLMJudgeConfig
        except Exception as exc:
            logger.warning(f"Failed to load evaluation nodes: {exc}")
            return {"error": "evaluation_nodes_unavailable"}

        resolved_provider = (
            evaluation_provider
            or self.config.testing.eval_provider
            or self.config.llm.provider
        )
        resolved_model = (
            evaluation_model
            or self.config.testing.eval_model
            or self.config.llm.model
            or self.config.ollama.default_model
        )
        resolved_endpoint = (
            evaluation_endpoint
            or self.config.testing.eval_endpoint
            or (self.config.ollama.host if resolved_provider == "ollama" else None)
        )

        judge_config = LLMJudgeConfig(
            model=resolved_model,
            provider=resolved_provider,
            endpoint=resolved_endpoint,
            host=resolved_endpoint or self.config.ollama.host,
            api_key_env=evaluation_api_key_env,
            emit_rl_metric=rl_metrics,
        )
        logger.info(
            "Running LLM-based evaluation",
            extra={
                "provider": resolved_provider,
                "model": resolved_model,
                "endpoint": resolved_endpoint,
                "rl_metrics": rl_metrics,
            },
        )
        judge = LLMJudgeNode(config=judge_config, ml_tracker=tracker)
        result = judge.run(
            {
                "query": query or "",
                "response": response,
                "context": context or "",
            }
        )

        metrics: Dict[str, Any] = {}
        outputs = result.outputs or {}
        overall_score = outputs.get("overall_score")
        if isinstance(overall_score, (int, float)):
            metrics["eval/overall_score"] = float(overall_score)
            logger.info(
                "LLM-based evaluation completed",
                extra={
                    "provider": resolved_provider,
                    "model": resolved_model,
                    "overall_score": float(overall_score),
                },
            )

        scores = outputs.get("scores", {})
        if isinstance(scores, dict):
            for name, value in scores.items():
                if isinstance(value, (int, float)):
                    metrics[f"eval/{name}"] = float(value)

        return {
            "outputs": outputs,
            "metrics": metrics,
            "provider": resolved_provider,
            "model": resolved_model,
            "endpoint": resolved_endpoint,
        }

    def _build_globals(self, sandbox: bool) -> Dict[str, Any]:
        if not sandbox:
            return {"__builtins__": __builtins__}

        allowed_builtins = {
            "abs", "all", "any", "bool", "dict", "enumerate", "filter",
            "float", "int", "len", "list", "map", "max", "min", "print",
            "range", "round", "set", "sorted", "str", "sum", "tuple", "zip",
        }
        if isinstance(__builtins__, dict):
            builtins_map = {k: __builtins__[k] for k in allowed_builtins if k in __builtins__}
        else:
            builtins_map = {k: getattr(__builtins__, k) for k in allowed_builtins if hasattr(__builtins__, k)}

        restricted_globals: Dict[str, Any] = {"__builtins__": builtins_map}

        for module_name in self.config.testing.allowed_imports:
            try:
                restricted_globals[module_name] = __import__(module_name)
            except ImportError:
                continue

        return restricted_globals

    def _determine_passed(
        self,
        passed_override: Any,
        expected_output: Optional[Any],
        result_value: Any,
        stderr_value: str,
    ) -> bool:
        if passed_override is not None:
            return bool(passed_override)
        if stderr_value:
            return False
        if expected_output is None or expected_output == "":
            return True
        if result_value is None:
            return False
        return result_value == expected_output

    def _normalize_input(self, input_data: Optional[Any]) -> Optional[Any]:
        if isinstance(input_data, str):
            trimmed = input_data.strip()
            if trimmed.startswith("{") or trimmed.startswith("["):
                try:
                    return json.loads(trimmed)
                except json.JSONDecodeError:
                    return input_data
        return input_data

    def _normalize_expected(self, expected_output: Optional[Any]) -> Optional[Any]:
        if isinstance(expected_output, str):
            trimmed = expected_output.strip()
            if trimmed.startswith("{") or trimmed.startswith("["):
                try:
                    return json.loads(trimmed)
                except json.JSONDecodeError:
                    return expected_output
        return expected_output

    def _truncate(self, value: str) -> str:
        max_chars = self.config.testing.max_output_chars
        if max_chars and len(value) > max_chars:
            return value[: max_chars - 3] + "..."
        return value

    def _resolve_flag(self, provided: Optional[bool], default: bool) -> bool:
        return default if provided is None else bool(provided)

    async def _emit_log(self, log_callback: Callable[[str, str], Any], message: str, level: str) -> None:
        try:
            result = log_callback(message, level)
            if asyncio.iscoroutine(result):
                await result
        except Exception as exc:
            logger.debug(f"Log callback failed: {exc}")


class _null_context:
    """Fallback context manager when tracking is disabled."""

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False
