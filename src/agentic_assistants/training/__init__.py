"""
LLM/SLM Training Module.

This module provides infrastructure for training, fine-tuning, and managing
custom language models using various frameworks (Llama Factory, Unsloth, Axolotl).

Key components:
- TrainingConfig: Configuration for training jobs
- TrainingJobManager: Job queue and status tracking
- BaseTrainingFramework: Abstract adapter for training frameworks
- LlamaFactoryAdapter: Primary training framework integration

Example:
    >>> from agentic_assistants.training import TrainingConfig, TrainingJobManager
    >>> from agentic_assistants.training.frameworks import LlamaFactoryAdapter
    >>> 
    >>> config = TrainingConfig(
    ...     base_model="meta-llama/Llama-3.2-1B",
    ...     method="lora",
    ...     dataset_id="my-instruct-dataset",
    ... )
    >>> adapter = LlamaFactoryAdapter()
    >>> job_manager = TrainingJobManager()
    >>> job = job_manager.create_job(config, adapter)
    >>> job_manager.start_job(job.id)
"""

from agentic_assistants.training.config import (
    TrainingConfig,
    LoRAConfig,
    QLoRAConfig,
    FullFinetuneConfig,
    QuantizationConfig,
    TrainingMethod,
    QuantizationType,
)
from agentic_assistants.training.jobs import (
    TrainingJob,
    TrainingJobManager,
    TrainingJobStatus,
)
from agentic_assistants.training.datasets import (
    TrainingDataset,
    InstructDataset,
    PreferenceDataset,
    DatasetFormat,
)
from agentic_assistants.training.export import (
    ModelExporter,
    ExportFormat,
)

__all__ = [
    # Config
    "TrainingConfig",
    "LoRAConfig",
    "QLoRAConfig",
    "FullFinetuneConfig",
    "QuantizationConfig",
    "TrainingMethod",
    "QuantizationType",
    # Jobs
    "TrainingJob",
    "TrainingJobManager",
    "TrainingJobStatus",
    # Datasets
    "TrainingDataset",
    "InstructDataset",
    "PreferenceDataset",
    "DatasetFormat",
    # Export
    "ModelExporter",
    "ExportFormat",
]
