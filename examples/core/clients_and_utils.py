from __future__ import annotations

from agentic_assistants.core.foundation import (
    HTTPDatasetClient,
    PrefectClient,
    append_step,
    deep_merge_state,
    ensure_required_keys,
    merge_metadata,
    project_state,
)


def main() -> None:
    merged = merge_metadata({"project": "agentic"}, {"owner": "julian"}, {"project": "core"})
    state = deep_merge_state({"history": [1]}, {"history": [2], "status": "ok"})
    append_step(state, "demo-step")
    selected = project_state(state, ["status", "__steps__"])
    ensure_required_keys(merged, ["project", "owner"])

    prefect_client = PrefectClient()
    print("Prefect available:", prefect_client.available)
    print("Metadata:", merged)
    print("State:", state)
    print("Selected:", selected)

    # Example only. Avoid network calls by default.
    _ = HTTPDatasetClient(base_url="http://localhost:8000")


if __name__ == "__main__":
    main()

