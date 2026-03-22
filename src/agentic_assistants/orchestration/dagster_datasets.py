"""
Dagster integration for dataset curation pipelines.

Provides software-defined assets, ops, jobs, schedules, and resources
for orchestrating dataset preparation workflows via Dagster.
"""

from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Attempt Dagster imports; provide stubs when not installed
# ---------------------------------------------------------------------------

try:
    from dagster import (
        asset,
        op,
        job,
        schedule,
        In,
        Out,
        Output,
        ConfigurableResource,
        ScheduleDefinition,
        AssetExecutionContext,
        OpExecutionContext,
        Definitions,
    )
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False

    def asset(*a, **kw):  # type: ignore[no-redef]
        def decorator(fn):
            return fn
        return decorator if not a else decorator(a[0])

    def op(*a, **kw):  # type: ignore[no-redef]
        def decorator(fn):
            return fn
        return decorator if not a else decorator(a[0])

    def job(*a, **kw):  # type: ignore[no-redef]
        def decorator(fn):
            return fn
        return decorator if not a else decorator(a[0])

    def schedule(*a, **kw):  # type: ignore[no-redef]
        def decorator(fn):
            return fn
        return decorator if not a else decorator(a[0])


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

if DAGSTER_AVAILABLE:
    class DatasetCatalogResource(ConfigurableResource):
        """Dagster resource wrapping the DatasetCatalog."""
        project_id: str = "default"
        data_dir: str = "./data/datasets"

        def get_catalog(self):
            from agentic_assistants.datasources.dataset_catalog import DatasetCatalog
            return DatasetCatalog(project_id=self.project_id, data_dir=self.data_dir)


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

@asset(group_name="datasets", description="Raw data fetched from configured sources")
def raw_dataset_asset(context) -> Dict[str, Any]:
    """Materialize raw dataset from sources."""
    from agentic_assistants.pipelines.nodes.dataset_curation import (
        DatasetSourceNode, DatasetSourceConfig,
    )

    config = context.op_config if hasattr(context, "op_config") else {}
    node = DatasetSourceNode(config=DatasetSourceConfig(
        source_type=config.get("source_type", "local"),
        source_path=config.get("source_path", "./data/datasets/raw"),
    ))
    result = node.execute({})
    context.log.info(f"Loaded {result['count']} raw samples")
    return result


@asset(
    group_name="datasets",
    deps=[raw_dataset_asset] if DAGSTER_AVAILABLE else [],
    description="Cleaned and filtered dataset",
)
def processed_dataset_asset(context, raw_dataset_asset: Dict[str, Any]) -> Dict[str, Any]:
    """Process raw data: dedup, filter, quality check."""
    from agentic_assistants.pipelines.nodes.dataset_curation import (
        DatasetFilterNode, DatasetFilterConfig,
    )

    node = DatasetFilterNode(config=DatasetFilterConfig())
    result = node.execute({"samples": raw_dataset_asset.get("samples", [])})
    context.log.info(
        f"Processed: {result['count']} samples kept, {result['removed']} removed"
    )
    return result


@asset(
    group_name="datasets",
    deps=[processed_dataset_asset] if DAGSTER_AVAILABLE else [],
    description="Training-ready formatted dataset",
)
def formatted_dataset_asset(
    context, processed_dataset_asset: Dict[str, Any]
) -> Dict[str, Any]:
    """Format processed data into training format."""
    from agentic_assistants.pipelines.nodes.dataset_curation import (
        DatasetFormatNode, DatasetFormatConfig,
    )

    config = context.op_config if hasattr(context, "op_config") else {}
    node = DatasetFormatNode(config=DatasetFormatConfig(
        output_format=config.get("output_format", "sharegpt"),
    ))
    result = node.execute({"samples": processed_dataset_asset.get("samples", [])})
    context.log.info(f"Formatted {result['count']} samples as {result['format']}")
    return result


@asset(
    group_name="datasets",
    deps=[processed_dataset_asset] if DAGSTER_AVAILABLE else [],
    description="Dataset quality statistics and report",
)
def dataset_stats_asset(
    context, processed_dataset_asset: Dict[str, Any]
) -> Dict[str, Any]:
    """Compute dataset statistics."""
    samples = processed_dataset_asset.get("samples", [])
    lengths = [
        len(s.get("instruction", "")) + len(s.get("output", ""))
        for s in samples
    ]
    stats = {
        "num_samples": len(samples),
        "avg_length": sum(lengths) / max(len(lengths), 1),
        "min_length": min(lengths) if lengths else 0,
        "max_length": max(lengths) if lengths else 0,
    }
    context.log.info(f"Dataset stats: {stats}")
    return stats


# ---------------------------------------------------------------------------
# Ops
# ---------------------------------------------------------------------------

@op(description="Fetch dataset from catalog by ID or name")
def fetch_dataset_op(context, dataset_id: str) -> Dict[str, Any]:
    """Fetch a dataset via the DatasetCatalog."""
    from agentic_assistants.datasources.dataset_catalog import DatasetCatalog
    catalog = DatasetCatalog()
    samples = catalog.get_or_fetch(dataset_id)
    context.log.info(f"Fetched {len(samples)} samples for {dataset_id}")
    return {"samples": samples, "count": len(samples)}


@op(description="Run processing pipeline on samples")
def process_dataset_op(context, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process dataset through filter and dedup nodes."""
    from agentic_assistants.pipelines.nodes.dataset_curation import (
        DatasetFilterNode, DatasetFilterConfig,
    )
    node = DatasetFilterNode(config=DatasetFilterConfig())
    return node.execute(data)


@op(description="Validate dataset against schema")
def validate_dataset_op(context, data: Dict[str, Any]) -> Dict[str, Any]:
    """Run validation checks on dataset."""
    from agentic_assistants.pipelines.nodes.dataset_curation import (
        DatasetValidationNode, DatasetValidationConfig,
    )
    node = DatasetValidationNode(config=DatasetValidationConfig())
    result = node.execute(data)
    if result["errors"]:
        context.log.warning(f"Validation found {len(result['errors'])} invalid samples")
    return result


@op(description="Export dataset to target format and location")
def export_dataset_op(context, data: Dict[str, Any]) -> Dict[str, Any]:
    """Export dataset to disk."""
    from agentic_assistants.pipelines.nodes.dataset_curation import (
        DatasetExportNode, DatasetExportConfig,
    )
    config = context.op_config if hasattr(context, "op_config") else {}
    node = DatasetExportNode(config=DatasetExportConfig(
        output_path=config.get("output_path", "./data/datasets/output/training.jsonl"),
    ))
    return node.execute(data)


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

if DAGSTER_AVAILABLE:
    @job(description="End-to-end dataset curation: fetch -> process -> validate -> export")
    def dataset_curation_job():
        raw = fetch_dataset_op()
        processed = process_dataset_op(raw)
        validated = validate_dataset_op(processed)
        export_dataset_op(validated)

    @job(description="Refresh existing datasets from sources")
    def dataset_refresh_job():
        raw = fetch_dataset_op()
        processed = process_dataset_op(raw)
        export_dataset_op(processed)


# ---------------------------------------------------------------------------
# Schedules
# ---------------------------------------------------------------------------

if DAGSTER_AVAILABLE:
    daily_dataset_refresh = ScheduleDefinition(
        job=dataset_refresh_job,
        cron_schedule="0 4 * * *",
        name="daily_dataset_refresh",
        description="Refresh active datasets daily at 4 AM",
    )


# ---------------------------------------------------------------------------
# Definitions bundle
# ---------------------------------------------------------------------------

def get_dataset_definitions():
    """Return Dagster Definitions for dataset curation."""
    if not DAGSTER_AVAILABLE:
        logger.warning("Dagster not installed; dataset definitions unavailable")
        return None

    return Definitions(
        assets=[
            raw_dataset_asset,
            processed_dataset_asset,
            formatted_dataset_asset,
            dataset_stats_asset,
        ],
        jobs=[dataset_curation_job, dataset_refresh_job],
        schedules=[daily_dataset_refresh],
        resources={
            "dataset_catalog": DatasetCatalogResource(
                project_id="nemotron-coding-assistant",
            ),
        },
    )
