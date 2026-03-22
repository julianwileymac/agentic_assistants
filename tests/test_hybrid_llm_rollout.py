import sqlite3
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.models import ControlPanelStore
from agentic_assistants.llms.provider import ChatResult, LLMProvider, OllamaLLMProvider
from agentic_assistants.server.rest import create_rest_app


def test_llm_provider_factory_dispatches_ollama() -> None:
    config = AgenticConfig()
    provider = LLMProvider.from_config(config, provider="ollama", model="llama3.2")
    assert isinstance(provider, OllamaLLMProvider)
    assert provider.model == "llama3.2"


def test_testing_router_prefix_no_double_prefix() -> None:
    client = TestClient(create_rest_app())

    ok = client.post(
        "/api/v1/testing/lint",
        json={"code": "result = 1 + 1\n", "language": "python"},
    )
    assert ok.status_code == 200

    bad = client.post(
        "/api/v1/api/v1/testing/lint",
        json={"code": "result = 1 + 1\n", "language": "python"},
    )
    assert bad.status_code == 404


def test_assistant_routes_are_disambiguated() -> None:
    client = TestClient(create_rest_app())

    config_resp = client.get("/api/v1/assistant/config")
    framework_resp = client.get("/api/v1/assistant/framework-config")

    assert config_resp.status_code == 200
    assert framework_resp.status_code == 200


def test_assistant_chat_accepts_provider_overrides() -> None:
    client = TestClient(create_rest_app())

    class _FakeProvider:
        async def achat(self, *, messages, model=None, temperature=None, **kwargs):
            _ = (messages, temperature, kwargs)
            return ChatResult(
                content="provider override works",
                model=model or "test-model",
                provider="openai_compatible",
            )

    with patch(
        "agentic_assistants.server.api.assistant.LLMProvider.from_config",
        return_value=_FakeProvider(),
    ) as mocked_factory:
        resp = client.post(
            "/api/v1/assistant/chat",
            json={
                "messages": [{"role": "user", "content": "hello"}],
                "provider": "openai_compatible",
                "model": "my-eval-model",
                "endpoint": "http://localhost:8000/v1",
            },
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "openai_compatible"
    assert body["model"] == "my-eval-model"
    assert body["message"]["content"] == "provider override works"
    assert mocked_factory.called


def test_test_run_eval_columns_migrated_and_persisted(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "control_panel.db"

    # Simulate a pre-migration database with an older test_runs schema.
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS test_runs (
            id TEXT PRIMARY KEY,
            run_name TEXT DEFAULT '',
            test_case_id TEXT,
            suite_id TEXT,
            resource_type TEXT,
            resource_id TEXT,
            status TEXT DEFAULT 'pending',
            sandbox_enabled INTEGER DEFAULT 1,
            tracking_enabled INTEGER DEFAULT 0,
            agent_eval_enabled INTEGER DEFAULT 0,
            rl_metrics_enabled INTEGER DEFAULT 0,
            dataset_id TEXT,
            input_data TEXT DEFAULT '',
            output_data TEXT DEFAULT '',
            metrics TEXT DEFAULT '{}',
            error_message TEXT,
            started_at TEXT,
            completed_at TEXT,
            duration_seconds REAL,
            created_at TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()

    config = AgenticConfig(data_dir=data_dir)
    store = ControlPanelStore(config=config)

    # Verify migration added provider-aware evaluation columns.
    with sqlite3.connect(db_path) as migrated:
        migrated.row_factory = sqlite3.Row
        columns = {
            row["name"]
            for row in migrated.execute("PRAGMA table_info(test_runs)").fetchall()
        }
    assert "evaluation_provider" in columns
    assert "evaluation_model" in columns
    assert "evaluation_endpoint" in columns
    assert "evaluation_hf_execution_mode" in columns

    test_run = store.create_test_run(
        run_name="eval-metadata-run",
        status="running",
        evaluation_provider="openai_compatible",
        evaluation_model="meta-llama/Llama-3.1-8B-Instruct",
        evaluation_endpoint="http://localhost:8000/v1",
        evaluation_hf_execution_mode="hybrid",
    )
    loaded = store.get_test_run(test_run.id)

    assert loaded is not None
    assert loaded.evaluation_provider == "openai_compatible"
    assert loaded.evaluation_model == "meta-llama/Llama-3.1-8B-Instruct"
    assert loaded.evaluation_endpoint == "http://localhost:8000/v1"
    assert loaded.evaluation_hf_execution_mode == "hybrid"

