"""Run repo-intel-hub ingestion."""

from agentic_assistants.data.catalog import DataCatalog
from agentic_assistants.pipelines.runners import SequentialRunner
from agentic_assistants.pipelines.templates import create_repo_ingestion_pipeline


def main() -> None:
    pipe = create_repo_ingestion_pipeline(
        config_path="examples/starters/repo-intel-hub/config.yaml"
    )
    result = SequentialRunner().run(pipe, DataCatalog())
    print(result.success)
    print(result.outputs.get("summary_result", {}))


if __name__ == "__main__":
    main()

