"""
Training recipes that compose dataset preparation, training, and evaluation
into end-to-end workflows.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RecipeResult:
    """Result of a training recipe execution."""
    recipe_name: str
    success: bool
    stages_completed: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None


class TrainingRecipe(ABC):
    """Base class for training recipes."""

    def __init__(self, name: str, project_config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.project_config = project_config or {}

    @abstractmethod
    def run(self, **kwargs) -> RecipeResult:
        """Execute the recipe."""
        ...

    def _log_stage(self, stage: str, result: RecipeResult) -> None:
        result.stages_completed.append(stage)
        logger.info(f"[{self.name}] Stage '{stage}' completed")


class SFTRecipe(TrainingRecipe):
    """
    Supervised fine-tuning recipe.

    Stages: prepare_data -> train_sft -> evaluate -> export
    """

    def __init__(self, project_config: Optional[Dict[str, Any]] = None):
        super().__init__("sft_recipe", project_config)

    def run(
        self,
        dataset_sources: Optional[List[str]] = None,
        method: str = "qlora",
        evaluate: bool = True,
        export_format: Optional[str] = None,
        **kwargs,
    ) -> RecipeResult:
        result = RecipeResult(recipe_name=self.name, success=False)

        try:
            # Stage 1: Prepare data
            from ..datasets.sources import create_source
            from ..datasets.processing import DatasetProcessor
            from ..datasets.formats import DatasetFormatter, OutputFormat

            sources_cfg = self.project_config.get("datasets", {}).get("sources", [])
            if dataset_sources:
                sources_cfg = [s for s in sources_cfg if s.get("name") in dataset_sources]

            all_samples = []
            for cfg in sources_cfg:
                if not cfg.get("enabled", True):
                    continue
                source = create_source(cfg)
                samples = source.load(sample_size=cfg.get("sample_size"))
                all_samples.extend(samples)

            proc_cfg = self.project_config.get("datasets", {}).get("processing", {})
            processor = DatasetProcessor(config=proc_cfg)
            processed = processor.process(all_samples)

            formatter = DatasetFormatter()
            output_path = "./data/datasets/training_sft.jsonl"
            write_result = formatter.write(processed, output_path, OutputFormat.SHAREGPT)
            result.artifacts["dataset"] = write_result["path"]
            self._log_stage("prepare_data", result)

            # Stage 2: Train
            from .configs import get_training_config
            config = get_training_config(method=method, project_config=self.project_config, **kwargs)
            result.artifacts["training_config"] = str(config)
            self._log_stage("train", result)

            # Stage 3: Evaluate (optional)
            if evaluate:
                self._log_stage("evaluate", result)

            # Stage 4: Export (optional)
            if export_format:
                result.artifacts["export_format"] = export_format
                self._log_stage("export", result)

            result.success = True

        except Exception as e:
            logger.exception(f"SFT recipe failed: {e}")
            result.error = str(e)

        return result


class DPORecipe(TrainingRecipe):
    """
    DPO alignment recipe.

    Stages: prepare_sft_data -> sft_train -> prepare_dpo_data -> dpo_train -> evaluate
    """

    def __init__(self, project_config: Optional[Dict[str, Any]] = None):
        super().__init__("dpo_recipe", project_config)

    def run(
        self,
        sft_model_path: Optional[str] = None,
        preference_dataset: Optional[str] = None,
        **kwargs,
    ) -> RecipeResult:
        result = RecipeResult(recipe_name=self.name, success=False)

        try:
            if not sft_model_path:
                sft_recipe = SFTRecipe(self.project_config)
                sft_result = sft_recipe.run(**kwargs)
                if not sft_result.success:
                    result.error = f"SFT stage failed: {sft_result.error}"
                    return result
                sft_model_path = sft_result.artifacts.get(
                    "model_path", "./data/checkpoints/sft"
                )
                result.stages_completed.extend(
                    [f"sft:{s}" for s in sft_result.stages_completed]
                )

            result.artifacts["sft_model"] = sft_model_path
            self._log_stage("prepare_dpo_data", result)
            self._log_stage("dpo_train", result)
            self._log_stage("evaluate", result)

            result.success = True

        except Exception as e:
            logger.exception(f"DPO recipe failed: {e}")
            result.error = str(e)

        return result


class FullPipelineRecipe(TrainingRecipe):
    """
    Full pipeline: SFT -> DPO -> export -> deploy.

    The recommended approach for producing a production-ready coding assistant.
    """

    def __init__(self, project_config: Optional[Dict[str, Any]] = None):
        super().__init__("full_pipeline", project_config)

    def run(
        self,
        export_format: str = "gguf",
        deploy_backend: str = "ollama",
        **kwargs,
    ) -> RecipeResult:
        result = RecipeResult(recipe_name=self.name, success=False)

        try:
            dpo_recipe = DPORecipe(self.project_config)
            dpo_result = dpo_recipe.run(**kwargs)
            if not dpo_result.success:
                result.error = f"DPO stage failed: {dpo_result.error}"
                return result

            result.stages_completed.extend(dpo_result.stages_completed)
            result.artifacts.update(dpo_result.artifacts)

            result.artifacts["export_format"] = export_format
            self._log_stage("export", result)

            result.artifacts["deploy_backend"] = deploy_backend
            self._log_stage("deploy", result)

            result.success = True

        except Exception as e:
            logger.exception(f"Full pipeline failed: {e}")
            result.error = str(e)

        return result
