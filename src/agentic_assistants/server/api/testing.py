"""
Testing API routes.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.testing import TestRunner, lint_code
from agentic_assistants.utils.logging import get_logger
from agentic_assistants.server.websocket import LogStreamer, emitter

logger = get_logger(__name__)

router = APIRouter(prefix="/testing", tags=["testing"])


def _get_store() -> ControlPanelStore:
    return ControlPanelStore.get_instance()


def _ensure_testing_enabled() -> None:
    config = AgenticConfig()
    if not config.testing.enabled:
        raise HTTPException(status_code=403, detail="Testing features are disabled")


class TestCaseCreate(BaseModel):
    name: str
    description: str = ""
    resource_type: str
    resource_id: Optional[str] = None
    language: str = "python"
    code: str = ""
    input_data: str = ""
    expected_output: str = ""
    test_type: str = "unit"
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TestCaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    language: Optional[str] = None
    code: Optional[str] = None
    input_data: Optional[str] = None
    expected_output: Optional[str] = None
    test_type: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TestCaseResponse(BaseModel):
    id: str
    name: str
    description: str
    resource_type: str
    resource_id: Optional[str]
    language: str
    code: str
    input_data: str
    expected_output: str
    test_type: str
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: Dict[str, Any]


class TestCaseListResponse(BaseModel):
    items: List[TestCaseResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class TestSuiteCreate(BaseModel):
    name: str
    description: str = ""
    resource_type: str
    resource_id: Optional[str] = None
    test_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TestSuiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    test_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TestSuiteResponse(BaseModel):
    id: str
    name: str
    description: str
    resource_type: str
    resource_id: Optional[str]
    test_ids: List[str]
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: Dict[str, Any]


class TestSuiteListResponse(BaseModel):
    items: List[TestSuiteResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class TestRunRequest(BaseModel):
    run_name: Optional[str] = None
    test_case_id: Optional[str] = None
    suite_id: Optional[str] = None
    code: Optional[str] = None
    language: str = "python"
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    input_data: Optional[Any] = None
    expected_output: Optional[Any] = None
    dataset_id: Optional[str] = None
    sandbox_enabled: Optional[bool] = None
    tracking_enabled: Optional[bool] = None
    agent_eval_enabled: Optional[bool] = None
    rl_metrics_enabled: Optional[bool] = None
    evaluation_context: Optional[str] = None
    evaluation_query: Optional[str] = None
    evaluation_provider: Optional[str] = None
    evaluation_model: Optional[str] = None
    evaluation_endpoint: Optional[str] = None
    evaluation_api_key_env: Optional[str] = None
    evaluation_hf_execution_mode: Optional[str] = None


class TestRunResponse(BaseModel):
    id: str
    run_name: str
    test_case_id: Optional[str]
    suite_id: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    status: str
    sandbox_enabled: bool
    tracking_enabled: bool
    agent_eval_enabled: bool
    rl_metrics_enabled: bool
    evaluation_provider: Optional[str] = None
    evaluation_model: Optional[str] = None
    evaluation_endpoint: Optional[str] = None
    evaluation_hf_execution_mode: Optional[str] = None
    dataset_id: Optional[str]
    input_data: str
    output_data: str
    metrics: Dict[str, Any]
    error_message: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    duration_seconds: Optional[float]
    created_at: str


class TestResultResponse(BaseModel):
    id: str
    run_id: str
    test_case_id: Optional[str]
    name: str
    passed: bool
    status: str
    output: str
    error_message: Optional[str]
    metrics: Dict[str, Any]
    created_at: str


class TestRunDetailResponse(BaseModel):
    run: TestRunResponse
    results: List[TestResultResponse]


class TestRunListResponse(BaseModel):
    items: List[TestRunResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class LintRequest(BaseModel):
    code: str
    language: str = "python"


class LintResponse(BaseModel):
    issues: List[str]


@router.post("/lint", response_model=LintResponse)
async def lint_snippet(request: LintRequest) -> LintResponse:
    _ensure_testing_enabled()
    result = lint_code(request.code, request.language)
    return LintResponse(issues=result["issues"])


@router.get("/cases", response_model=TestCaseListResponse)
async def list_test_cases(
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    test_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> TestCaseListResponse:
    store = _get_store()
    items, total = store.list_test_cases(
        resource_type=resource_type,
        resource_id=resource_id,
        test_type=test_type,
        search=search,
        page=page,
        limit=limit,
    )
    return TestCaseListResponse(
        items=[TestCaseResponse(**item.to_dict()) for item in items],
        total=total,
        page=page,
        page_size=limit,
        has_more=(page * limit) < total,
    )


@router.post("/cases", response_model=TestCaseResponse)
async def create_test_case(request: TestCaseCreate) -> TestCaseResponse:
    _ensure_testing_enabled()
    store = _get_store()
    test_case = store.create_test_case(
        name=request.name,
        resource_type=request.resource_type,
        description=request.description,
        resource_id=request.resource_id,
        language=request.language,
        code=request.code,
        input_data=request.input_data,
        expected_output=request.expected_output,
        test_type=request.test_type,
        tags=request.tags,
        metadata=request.metadata,
    )
    return TestCaseResponse(**test_case.to_dict())


@router.get("/cases/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(test_case_id: str) -> TestCaseResponse:
    store = _get_store()
    test_case = store.get_test_case(test_case_id)
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    return TestCaseResponse(**test_case.to_dict())


@router.put("/cases/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(test_case_id: str, request: TestCaseUpdate) -> TestCaseResponse:
    store = _get_store()
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    test_case = store.update_test_case(test_case_id, **update_data)
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    return TestCaseResponse(**test_case.to_dict())


@router.delete("/cases/{test_case_id}")
async def delete_test_case(test_case_id: str) -> Dict[str, Any]:
    store = _get_store()
    if not store.delete_test_case(test_case_id):
        raise HTTPException(status_code=404, detail="Test case not found")
    return {"status": "deleted", "id": test_case_id}


@router.get("/suites", response_model=TestSuiteListResponse)
async def list_test_suites(
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> TestSuiteListResponse:
    store = _get_store()
    items, total = store.list_test_suites(
        resource_type=resource_type,
        resource_id=resource_id,
        search=search,
        page=page,
        limit=limit,
    )
    return TestSuiteListResponse(
        items=[TestSuiteResponse(**item.to_dict()) for item in items],
        total=total,
        page=page,
        page_size=limit,
        has_more=(page * limit) < total,
    )


@router.post("/suites", response_model=TestSuiteResponse)
async def create_test_suite(request: TestSuiteCreate) -> TestSuiteResponse:
    _ensure_testing_enabled()
    store = _get_store()
    suite = store.create_test_suite(
        name=request.name,
        resource_type=request.resource_type,
        description=request.description,
        resource_id=request.resource_id,
        test_ids=request.test_ids,
        tags=request.tags,
        metadata=request.metadata,
    )
    return TestSuiteResponse(**suite.to_dict())


@router.get("/suites/{suite_id}", response_model=TestSuiteResponse)
async def get_test_suite(suite_id: str) -> TestSuiteResponse:
    store = _get_store()
    suite = store.get_test_suite(suite_id)
    if suite is None:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return TestSuiteResponse(**suite.to_dict())


@router.put("/suites/{suite_id}", response_model=TestSuiteResponse)
async def update_test_suite(suite_id: str, request: TestSuiteUpdate) -> TestSuiteResponse:
    store = _get_store()
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    suite = store.update_test_suite(suite_id, **update_data)
    if suite is None:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return TestSuiteResponse(**suite.to_dict())


@router.delete("/suites/{suite_id}")
async def delete_test_suite(suite_id: str) -> Dict[str, Any]:
    store = _get_store()
    if not store.delete_test_suite(suite_id):
        raise HTTPException(status_code=404, detail="Test suite not found")
    return {"status": "deleted", "id": suite_id}


@router.get("/runs", response_model=TestRunListResponse)
async def list_test_runs(
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> TestRunListResponse:
    store = _get_store()
    items, total = store.list_test_runs(
        resource_type=resource_type,
        resource_id=resource_id,
        status=status,
        page=page,
        limit=limit,
    )
    return TestRunListResponse(
        items=[TestRunResponse(**item.to_dict()) for item in items],
        total=total,
        page=page,
        page_size=limit,
        has_more=(page * limit) < total,
    )


@router.get("/runs/{run_id}", response_model=TestRunDetailResponse)
async def get_test_run(run_id: str) -> TestRunDetailResponse:
    store = _get_store()
    run = store.get_test_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Test run not found")
    results = store.list_test_results(run_id)
    return TestRunDetailResponse(
        run=TestRunResponse(**run.to_dict()),
        results=[TestResultResponse(**r.to_dict()) for r in results],
    )


@router.get("/runs/{run_id}/results", response_model=List[TestResultResponse])
async def list_test_results(run_id: str) -> List[TestResultResponse]:
    store = _get_store()
    results = store.list_test_results(run_id)
    return [TestResultResponse(**r.to_dict()) for r in results]


@router.post("/runs", response_model=TestRunDetailResponse)
async def run_test(request: TestRunRequest) -> TestRunDetailResponse:
    _ensure_testing_enabled()
    store = _get_store()
    config = AgenticConfig()

    if not (request.test_case_id or request.suite_id or request.code):
        raise HTTPException(status_code=400, detail="Provide test_case_id, suite_id, or code")

    test_case = None
    suite = None
    if request.test_case_id:
        test_case = store.get_test_case(request.test_case_id)
        if test_case is None:
            raise HTTPException(status_code=404, detail="Test case not found")
    if request.suite_id:
        suite = store.get_test_suite(request.suite_id)
        if suite is None:
            raise HTTPException(status_code=404, detail="Test suite not found")

    runner = TestRunner(config)
    run_name = request.run_name or f"test-run-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    test_run = store.create_test_run(
        run_name=run_name,
        test_case_id=request.test_case_id,
        suite_id=request.suite_id,
        resource_type=request.resource_type,
        resource_id=request.resource_id,
        status="running",
        sandbox_enabled=request.sandbox_enabled if request.sandbox_enabled is not None else config.testing.sandbox_default,
        tracking_enabled=request.tracking_enabled if request.tracking_enabled is not None else config.testing.tracking_default,
        agent_eval_enabled=request.agent_eval_enabled if request.agent_eval_enabled is not None else config.testing.agent_eval_default,
        rl_metrics_enabled=request.rl_metrics_enabled if request.rl_metrics_enabled is not None else config.testing.rl_metrics_default,
        evaluation_provider=request.evaluation_provider or config.testing.eval_provider,
        evaluation_model=request.evaluation_model or config.testing.eval_model,
        evaluation_endpoint=request.evaluation_endpoint or config.testing.eval_endpoint,
        evaluation_hf_execution_mode=request.evaluation_hf_execution_mode or config.testing.eval_hf_execution_mode,
        dataset_id=request.dataset_id,
        input_data=json.dumps(request.input_data) if request.input_data is not None else "",
        started_at=datetime.utcnow(),
    )
    logger.info(
        "Started test run",
        extra={
            "run_id": test_run.id,
            "agent_eval_enabled": test_run.agent_eval_enabled,
            "evaluation_provider": test_run.evaluation_provider,
            "evaluation_model": test_run.evaluation_model,
            "evaluation_endpoint": test_run.evaluation_endpoint,
        },
    )

    log_streamer = LogStreamer(test_run.id, emitter)

    results: List[TestResultResponse] = []
    status = "completed"
    error_message = None
    aggregated_metrics: Dict[str, Any] = {}

    try:
        if request.suite_id and suite:
            passed_count = 0
            for test_id in suite.test_ids:
                test_case = store.get_test_case(test_id)
                if test_case is None:
                    continue

                exec_result = await runner.run_test(
                    code=test_case.code,
                    language=test_case.language,
                    input_data=test_case.input_data,
                    expected_output=test_case.expected_output,
                    dataset_id=request.dataset_id,
                    sandbox_enabled=request.sandbox_enabled,
                    tracking_enabled=request.tracking_enabled,
                    agent_eval_enabled=request.agent_eval_enabled,
                    rl_metrics_enabled=request.rl_metrics_enabled,
                    run_name=run_name,
                    evaluation_context=request.evaluation_context,
                    evaluation_query=request.evaluation_query,
                    evaluation_provider=request.evaluation_provider,
                    evaluation_model=request.evaluation_model,
                    evaluation_endpoint=request.evaluation_endpoint,
                    evaluation_api_key_env=request.evaluation_api_key_env,
                    evaluation_hf_execution_mode=request.evaluation_hf_execution_mode,
                    log_callback=log_streamer.write,
                )

                passed_count += 1 if exec_result.passed else 0

                result_record = store.create_test_result(
                    run_id=test_run.id,
                    test_case_id=test_case.id,
                    name=test_case.name,
                    passed=exec_result.passed,
                    status="passed" if exec_result.passed else "failed",
                    output=json.dumps(exec_result.output, default=str),
                    error_message=exec_result.error_message,
                    metrics=exec_result.metrics,
                )
                results.append(TestResultResponse(**result_record.to_dict()))

            aggregated_metrics.update(
                {
                    "passed_count": passed_count,
                    "total_count": len(results),
                }
            )

            status = "success" if passed_count == len(results) else "failed"

        else:
            if request.test_case_id and test_case:
                code = test_case.code
                language = test_case.language
                input_data = test_case.input_data
                expected_output = test_case.expected_output
            else:
                code = request.code or ""
                language = request.language
                input_data = request.input_data
                expected_output = request.expected_output

            exec_result = await runner.run_test(
                code=code,
                language=language,
                input_data=input_data,
                expected_output=expected_output,
                dataset_id=request.dataset_id,
                sandbox_enabled=request.sandbox_enabled,
                tracking_enabled=request.tracking_enabled,
                agent_eval_enabled=request.agent_eval_enabled,
                rl_metrics_enabled=request.rl_metrics_enabled,
                run_name=run_name,
                evaluation_context=request.evaluation_context,
                evaluation_query=request.evaluation_query,
                evaluation_provider=request.evaluation_provider,
                evaluation_model=request.evaluation_model,
                evaluation_endpoint=request.evaluation_endpoint,
                evaluation_api_key_env=request.evaluation_api_key_env,
                evaluation_hf_execution_mode=request.evaluation_hf_execution_mode,
                log_callback=log_streamer.write,
            )

            result_record = store.create_test_result(
                run_id=test_run.id,
                test_case_id=request.test_case_id,
                name=run_name,
                passed=exec_result.passed,
                status="passed" if exec_result.passed else "failed",
                output=json.dumps(exec_result.output, default=str),
                error_message=exec_result.error_message,
                metrics=exec_result.metrics,
            )
            results.append(TestResultResponse(**result_record.to_dict()))
            status = "success" if exec_result.passed else "failed"
            aggregated_metrics.update(exec_result.metrics)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Test run failed: {exc}")
        status = "failed"
        error_message = str(exc)
    finally:
        await log_streamer.close()

    completed_at = datetime.utcnow()
    duration = (completed_at - test_run.created_at).total_seconds()

    output_payload = {
        "results": [r.model_dump() for r in results],
    }

    store.update_test_run(
        test_run.id,
        status=status,
        completed_at=completed_at,
        duration_seconds=duration,
        output_data=json.dumps(output_payload, default=str),
        metrics=aggregated_metrics,
        error_message=error_message,
    )

    updated_run = store.get_test_run(test_run.id)
    if updated_run is None:
        raise HTTPException(status_code=500, detail="Failed to load test run")

    return TestRunDetailResponse(
        run=TestRunResponse(**updated_run.to_dict()),
        results=results,
    )
