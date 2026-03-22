from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from agentic_assistants.server.rest import create_rest_app


def test_lint_endpoint_accepts_valid_python() -> None:
    client = TestClient(create_rest_app())
    response = client.post(
        "/api/v1/testing/lint",
        json={"code": "def add(a, b):\n    return a + b\n", "language": "python"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["issues"] == []


def test_run_freeform_test() -> None:
    client = TestClient(create_rest_app())
    with patch(
        "agentic_assistants.server.api.testing.LogStreamer.write",
        new=AsyncMock(return_value=None),
    ), patch(
        "agentic_assistants.server.api.testing.LogStreamer.close",
        new=AsyncMock(return_value=None),
    ):
        response = client.post(
            "/api/v1/testing/runs",
            json={
                "code": "result = 2 + 2",
                "language": "python",
                "tracking_enabled": False,
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["run"]["status"] in {"success", "failed"}
    assert data["results"]
    assert data["results"][0]["passed"] is True
