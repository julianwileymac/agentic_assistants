"""
Standalone experiment scripts for the Nemotron project.

Provides convenience functions that can be run directly from the
command line or imported into notebooks.
"""

from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


def run_sft_experiment(
    dataset_sources: Optional[List[str]] = None,
    method: str = "qlora",
    config_path: Optional[str] = None,
    **overrides,
) -> Dict[str, Any]:
    """
    Run a supervised fine-tuning experiment.

    Example:
        >>> result = run_sft_experiment(
        ...     dataset_sources=["code-alpaca"],
        ...     method="qlora",
        ...     learning_rate=1e-4,
        ... )
    """
    from .. import NemotronProject

    project = NemotronProject(config_path=config_path)
    project.fetch_model()
    project.prepare_dataset(
        source_name=dataset_sources[0] if dataset_sources else None,
    )
    result = project.train(method=method, **overrides)
    eval_result = project.evaluate()

    return {
        "experiment_type": "sft",
        "method": method,
        "training": result,
        "evaluation": eval_result,
    }


def run_dpo_experiment(
    sft_model_path: Optional[str] = None,
    preference_dataset: Optional[str] = None,
    config_path: Optional[str] = None,
    **overrides,
) -> Dict[str, Any]:
    """
    Run a DPO alignment experiment.

    If no SFT model is provided, runs SFT first then DPO.
    """
    from .. import NemotronProject
    from ..training.recipes import DPORecipe

    project = NemotronProject(config_path=config_path)

    recipe = DPORecipe(project_config=project._config)
    result = recipe.run(
        sft_model_path=sft_model_path,
        preference_dataset=preference_dataset,
        **overrides,
    )

    return {
        "experiment_type": "dpo",
        "success": result.success,
        "stages": result.stages_completed,
        "artifacts": result.artifacts,
        "error": result.error,
    }


def run_full_experiment(
    name: str = "nemotron-full-pipeline",
    dataset_sources: Optional[List[str]] = None,
    config_path: Optional[str] = None,
    export_format: str = "gguf",
    deploy_backend: str = "ollama",
) -> Dict[str, Any]:
    """
    Run the full experiment pipeline: data prep -> SFT -> DPO -> export -> deploy.
    """
    from .. import NemotronProject
    from ..training.recipes import FullPipelineRecipe

    project = NemotronProject(config_path=config_path)

    recipe = FullPipelineRecipe(project_config=project._config)
    result = recipe.run(
        export_format=export_format,
        deploy_backend=deploy_backend,
    )

    return {
        "experiment_name": name,
        "experiment_type": "full_pipeline",
        "success": result.success,
        "stages": result.stages_completed,
        "artifacts": result.artifacts,
        "error": result.error,
    }


def compare_experiments(
    experiment_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compare results across multiple experiments."""
    comparison = {
        "experiments": [],
        "best": None,
    }

    for exp in experiment_results:
        eval_data = exp.get("evaluation", {})
        benchmarks = eval_data.get("benchmarks", [])
        avg_pass_rate = 0.0
        if benchmarks:
            avg_pass_rate = sum(
                b.get("metrics", {}).get("pass@1", 0.0) for b in benchmarks
            ) / len(benchmarks)

        entry = {
            "type": exp.get("experiment_type", "unknown"),
            "method": exp.get("method", "unknown"),
            "avg_pass_at_1": avg_pass_rate,
        }
        comparison["experiments"].append(entry)

    if comparison["experiments"]:
        best = max(comparison["experiments"], key=lambda e: e["avg_pass_at_1"])
        comparison["best"] = best

    return comparison
