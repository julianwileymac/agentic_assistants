"""
Nemotron Coding Assistant Starter Project.

Train, fine-tune, and evaluate nemotron-nano models on custom curated
datasets for coding assistance.

Example:
    >>> from examples.nemotron_coding_assistant import NemotronProject
    >>> project = NemotronProject()
    >>> project.fetch_model()
    >>> project.prepare_dataset("code-alpaca")
    >>> project.train(method="qlora")
    >>> results = project.evaluate()
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)

__version__ = "0.1.0"
__author__ = "Agentic Assistants Team"

DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.yaml"


class NemotronProject:
    """
    Main interface for the Nemotron coding assistant project.

    Orchestrates model fetching, dataset curation, training, evaluation,
    and serving of nemotron-nano models fine-tuned for coding assistance.

    Example:
        >>> project = NemotronProject()
        >>>
        >>> # Fetch and prepare
        >>> project.fetch_model()
        >>> project.prepare_dataset("code-alpaca")
        >>>
        >>> # Train
        >>> project.train(method="qlora")
        >>>
        >>> # Evaluate and serve
        >>> results = project.evaluate()
        >>> project.serve_model()
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.project_id = project_id or "nemotron-coding-assistant"

        self._config = self._load_config()

        paths = self._config.get("paths", {})
        self.data_dir = Path(paths.get("data_dir", "./data"))
        self.models_dir = Path(paths.get("models_dir", "./data/models"))
        self.datasets_dir = Path(paths.get("datasets_dir", "./data/datasets"))
        self.checkpoints_dir = Path(paths.get("checkpoints_dir", "./data/checkpoints"))
        self.exports_dir = Path(paths.get("exports_dir", "./data/exports"))

        for d in [self.data_dir, self.models_dir, self.datasets_dir,
                  self.checkpoints_dir, self.exports_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self._model_manager = None
        self._dataset_catalog = None
        self._training_manager = None
        self._serving_manager = None
        self._knowledge_base = None
        self._agents: Dict[str, Any] = {}

        logger.info(f"NemotronProject initialized: {self.config_path}")

    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {}

    @property
    def nemotron_config(self) -> Dict[str, Any]:
        return self._config.get("nemotron", {})

    @property
    def model_manager(self):
        if self._model_manager is None:
            from agentic_assistants.integrations.nemotron import NemotronModelManager
            self._model_manager = NemotronModelManager(
                cache_dir=str(self.models_dir),
                default_model=self.nemotron_config.get(
                    "base_model", "nvidia/Llama-3.1-Nemotron-Nano-8B-v1"
                ),
            )
        return self._model_manager

    @property
    def dataset_catalog(self):
        if self._dataset_catalog is None:
            from agentic_assistants.datasources.dataset_catalog import DatasetCatalog
            self._dataset_catalog = DatasetCatalog(
                project_id=self.project_id,
                data_dir=str(self.datasets_dir),
            )
        return self._dataset_catalog

    @property
    def training_manager(self):
        if self._training_manager is None:
            from agentic_assistants.training.jobs import TrainingJobManager
            self._training_manager = TrainingJobManager()
        return self._training_manager

    @property
    def serving_manager(self):
        if self._serving_manager is None:
            from agentic_assistants.serving.manager import ServingManager
            self._serving_manager = ServingManager()
        return self._serving_manager

    @property
    def knowledge_base(self):
        if self._knowledge_base is None:
            from agentic_assistants.vectordb import get_vector_store
            vdb_config = self._config.get("vector_db", {})
            self._knowledge_base = get_vector_store(
                backend=vdb_config.get("backend", "lancedb"),
                path=vdb_config.get("path", str(self.data_dir / "vectordb")),
            )
        return self._knowledge_base

    def get_agent(self, agent_type: str):
        if agent_type not in self._agents:
            agent_config = self._config.get("agents", {}).get(agent_type, {})
            if agent_type == "coding_agent":
                from .agents.coding_agent import NemotronCodingAgent
                self._agents[agent_type] = NemotronCodingAgent(
                    config=agent_config,
                    model_manager=self.model_manager,
                    knowledge_base=self.knowledge_base,
                )
            elif agent_type == "dataset_curator":
                from .agents.dataset_curator import DatasetCuratorAgent
                self._agents[agent_type] = DatasetCuratorAgent(
                    config=agent_config,
                    dataset_catalog=self.dataset_catalog,
                )
            elif agent_type == "eval_agent":
                from .agents.eval_agent import EvaluationAgent
                self._agents[agent_type] = EvaluationAgent(
                    config=agent_config,
                    model_manager=self.model_manager,
                )
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
            logger.info(f"Agent '{agent_type}' initialized")
        return self._agents[agent_type]

    def fetch_model(
        self,
        model_id: Optional[str] = None,
        revision: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Download model weights from HuggingFace."""
        model_id = model_id or self.nemotron_config.get(
            "base_model", "nvidia/Llama-3.1-Nemotron-Nano-8B-v1"
        )
        revision = revision or self.nemotron_config.get("revision", "main")
        logger.info(f"Fetching model: {model_id} (revision: {revision})")
        return self.model_manager.fetch_weights(model_id, revision=revision)

    def serve_model(
        self,
        model_path: Optional[str] = None,
        backend: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Deploy the model for inference."""
        backend = backend or self.nemotron_config.get("serving", {}).get(
            "preferred_backend", "vllm"
        )
        model_path = model_path or str(self.models_dir / "base")
        logger.info(f"Serving model via {backend}: {model_path}")
        return self.model_manager.deploy(model_path, backend=backend)

    def prepare_dataset(
        self,
        source_name: Optional[str] = None,
        output_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Prepare a dataset for training from configured sources."""
        sources = self._config.get("datasets", {}).get("sources", [])
        processing = self._config.get("datasets", {}).get("processing", {})
        output = self._config.get("datasets", {}).get("output", {})
        output_format = output_format or output.get("default_format", "sharegpt")

        if source_name:
            sources = [s for s in sources if s.get("name") == source_name]
            if not sources:
                raise ValueError(f"Source not found: {source_name}")

        results = []
        for source in sources:
            if not source.get("enabled", True):
                continue
            logger.info(f"Processing dataset source: {source['name']}")
            entry = self.dataset_catalog.register(
                name=source["name"],
                source_type=source["type"],
                source_path=source.get("path", ""),
                format=source.get("format", "jsonl"),
                project_id=self.project_id,
            )
            results.append({"source": source["name"], "entry_id": entry.id})

        return {
            "sources_processed": len(results),
            "output_format": output_format,
            "results": results,
        }

    def train(
        self,
        method: Optional[str] = None,
        dataset_name: Optional[str] = None,
        **overrides,
    ) -> Dict[str, Any]:
        """Launch a training run."""
        method = method or self._config.get("training", {}).get("default_method", "qlora")
        logger.info(f"Starting training with method: {method}")

        from .training.configs import get_training_config
        config = get_training_config(
            method=method,
            project_config=self._config,
            **overrides,
        )

        job = self.training_manager.create_job(config)
        return {"job_id": job.job_id, "method": method, "status": job.status.value}

    def evaluate(
        self,
        model_path: Optional[str] = None,
        benchmarks: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Run evaluation benchmarks."""
        from .evaluation.benchmarks import BenchmarkRunner
        eval_config = self._config.get("evaluation", {})
        runner = BenchmarkRunner(config=eval_config)
        model_path = model_path or str(self.models_dir / "latest")
        return runner.run(model_path=model_path, benchmarks=benchmarks)

    def run_experiment(
        self,
        experiment_name: str,
        dataset_sources: Optional[List[str]] = None,
        training_method: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run an end-to-end experiment: prepare, train, evaluate."""
        logger.info(f"Starting experiment: {experiment_name}")

        dataset_result = self.prepare_dataset()
        train_result = self.train(method=training_method)
        eval_result = self.evaluate()

        return {
            "experiment": experiment_name,
            "dataset": dataset_result,
            "training": train_result,
            "evaluation": eval_result,
        }

    def export_model(
        self,
        model_path: str,
        export_format: str = "gguf",
        quantization: str = "q4_k_m",
    ) -> Dict[str, Any]:
        """Export the trained model to a deployable format."""
        logger.info(f"Exporting model to {export_format}: {model_path}")
        return self.model_manager.export(
            model_path=model_path,
            format=export_format,
            quantization=quantization,
            output_dir=str(self.exports_dir),
        )

    def get_stats(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "config_path": str(self.config_path),
            "model": self.nemotron_config.get("base_model"),
            "datasets_registered": len(self.dataset_catalog.list()),
        }


def create_project(
    config_path: Optional[str] = None,
    project_id: Optional[str] = None,
) -> NemotronProject:
    return NemotronProject(config_path=config_path, project_id=project_id)


__all__ = [
    "NemotronProject",
    "create_project",
]
