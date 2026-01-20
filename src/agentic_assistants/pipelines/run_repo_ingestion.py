"""
Run the repository ingestion pipeline from the command line.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from agentic_assistants.data.catalog import DataCatalog
from agentic_assistants.pipelines.runners import SequentialRunner
from agentic_assistants.pipelines.templates import create_repo_ingestion_pipeline
from agentic_assistants.utils.logging import setup_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run repo ingestion pipeline")
    parser.add_argument(
        "--config",
        default=os.environ.get(
            "AGENTIC_REPO_INGESTION_CONFIG",
            "examples/global-knowledgebase-starter/config.yaml",
        ),
        help="Path to repo ingestion config YAML",
    )
    parser.add_argument("--repo", default=None, help="Only ingest a single repo by name")
    parser.add_argument("--force", action="store_true", help="Force re-indexing")
    parser.add_argument(
        "--ignore-manual-override",
        action="store_true",
        help="Ignore per-repo manual_override flags",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(level="INFO")

    overrides = {
        "force_reindex": args.force,
        "respect_manual_override": not args.ignore_manual_override,
        "only_repos": [args.repo] if args.repo else None,
    }

    pipeline = create_repo_ingestion_pipeline(
        config_path=args.config,
        overrides=overrides,
    )
    runner = SequentialRunner()
    result = runner.run(pipeline, DataCatalog())

    summary = result.outputs.get("summary_result", {})
    print(json.dumps(summary, indent=2))

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
