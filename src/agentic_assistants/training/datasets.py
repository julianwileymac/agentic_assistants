"""
Training dataset management.

This module provides classes for managing datasets used in LLM training,
including instruction datasets, preference datasets, and data preparation utilities.
"""

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class DatasetFormat(str, Enum):
    """Supported training dataset formats."""
    ALPACA = "alpaca"        # instruction, input, output
    SHAREGPT = "sharegpt"    # conversations with roles
    OPENAI = "openai"        # messages format
    DOLLY = "dolly"          # instruction, context, response
    CUSTOM = "custom"        # user-defined format
    
    # Preference formats
    DPO = "dpo"              # prompt, chosen, rejected
    RLHF = "rlhf"            # prompt, response, reward
    COMPARISON = "comparison" # prompt, response_a, response_b, preference


@dataclass
class DatasetColumn:
    """Definition of a dataset column."""
    name: str
    role: str  # instruction, input, output, system, prompt, chosen, rejected, etc.
    required: bool = True


@dataclass
class DatasetSchema:
    """Schema definition for a training dataset."""
    
    format: DatasetFormat
    columns: List[DatasetColumn]
    
    # Template for formatting (if applicable)
    instruction_template: Optional[str] = None
    system_prompt: Optional[str] = None
    
    @classmethod
    def alpaca(cls) -> "DatasetSchema":
        """Standard Alpaca format schema."""
        return cls(
            format=DatasetFormat.ALPACA,
            columns=[
                DatasetColumn("instruction", "instruction"),
                DatasetColumn("input", "input", required=False),
                DatasetColumn("output", "output"),
            ],
            instruction_template="### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{output}",
        )
    
    @classmethod
    def sharegpt(cls) -> "DatasetSchema":
        """ShareGPT conversation format schema."""
        return cls(
            format=DatasetFormat.SHAREGPT,
            columns=[
                DatasetColumn("conversations", "conversations"),
            ],
        )
    
    @classmethod
    def dpo(cls) -> "DatasetSchema":
        """DPO preference format schema."""
        return cls(
            format=DatasetFormat.DPO,
            columns=[
                DatasetColumn("prompt", "prompt"),
                DatasetColumn("chosen", "chosen"),
                DatasetColumn("rejected", "rejected"),
            ],
        )


@dataclass
class TrainingDataset:
    """
    Base class for training datasets.
    
    Represents a dataset that can be used for training, including
    metadata, statistics, and data access methods.
    """
    
    id: str
    name: str
    description: str = ""
    
    # Format and schema
    format: DatasetFormat = DatasetFormat.ALPACA
    schema: Optional[DatasetSchema] = None
    
    # Storage
    filepath: Optional[str] = None
    hf_dataset_id: Optional[str] = None
    
    # Statistics
    num_samples: int = 0
    size_bytes: int = 0
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    
    # Quality metrics
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Lineage
    source_datasets: List[str] = field(default_factory=list)
    transformations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "format": self.format.value,
            "filepath": self.filepath,
            "hf_dataset_id": self.hf_dataset_id,
            "num_samples": self.num_samples,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": self.tags,
            "version": self.version,
            "quality_metrics": self.quality_metrics,
            "source_datasets": self.source_datasets,
            "transformations": self.transformations,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainingDataset":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            format=DatasetFormat(data.get("format", "alpaca")),
            filepath=data.get("filepath"),
            hf_dataset_id=data.get("hf_dataset_id"),
            num_samples=data.get("num_samples", 0),
            size_bytes=data.get("size_bytes", 0),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
            tags=data.get("tags", []),
            version=data.get("version", "1.0.0"),
            quality_metrics=data.get("quality_metrics", {}),
            source_datasets=data.get("source_datasets", []),
            transformations=data.get("transformations", []),
        )
    
    def load_samples(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load samples from the dataset."""
        if not self.filepath or not Path(self.filepath).exists():
            return []
        
        samples = []
        filepath = Path(self.filepath)
        
        try:
            if filepath.suffix == ".json":
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    samples = data if isinstance(data, list) else [data]
            elif filepath.suffix == ".jsonl":
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            samples.append(json.loads(line))
                            if limit and len(samples) >= limit:
                                break
        except Exception as e:
            logger.error(f"Failed to load samples from {filepath}: {e}")
        
        return samples[:limit] if limit else samples
    
    def validate(self) -> List[str]:
        """
        Validate dataset against its schema.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not self.filepath and not self.hf_dataset_id:
            errors.append("No data source specified (filepath or hf_dataset_id)")
            return errors
        
        if self.filepath and not Path(self.filepath).exists():
            errors.append(f"File not found: {self.filepath}")
            return errors
        
        # Check sample data
        samples = self.load_samples(limit=10)
        if not samples:
            errors.append("Dataset is empty or could not be loaded")
            return errors
        
        # Validate against schema if provided
        if self.schema:
            required_columns = [c.name for c in self.schema.columns if c.required]
            for sample in samples:
                for col in required_columns:
                    if col not in sample:
                        errors.append(f"Missing required column: {col}")
                        break
        
        return errors


@dataclass
class InstructDataset(TrainingDataset):
    """Dataset for instruction fine-tuning."""
    
    format: DatasetFormat = DatasetFormat.ALPACA
    
    # Additional instruction-specific fields
    system_prompt: Optional[str] = None
    instruction_column: str = "instruction"
    input_column: str = "input"
    output_column: str = "output"
    
    def to_alpaca_format(self) -> List[Dict[str, str]]:
        """Convert to standard Alpaca format."""
        samples = self.load_samples()
        converted = []
        
        for sample in samples:
            converted.append({
                "instruction": sample.get(self.instruction_column, ""),
                "input": sample.get(self.input_column, ""),
                "output": sample.get(self.output_column, ""),
            })
        
        return converted


@dataclass
class PreferenceDataset(TrainingDataset):
    """Dataset for preference learning (DPO, RLHF)."""
    
    format: DatasetFormat = DatasetFormat.DPO
    
    # Preference-specific columns
    prompt_column: str = "prompt"
    chosen_column: str = "chosen"
    rejected_column: str = "rejected"
    
    # For RLHF with explicit rewards
    reward_column: Optional[str] = None
    
    def to_dpo_format(self) -> List[Dict[str, str]]:
        """Convert to DPO format."""
        samples = self.load_samples()
        converted = []
        
        for sample in samples:
            converted.append({
                "prompt": sample.get(self.prompt_column, ""),
                "chosen": sample.get(self.chosen_column, ""),
                "rejected": sample.get(self.rejected_column, ""),
            })
        
        return converted


class TrainingDatasetManager:
    """
    Manager for training datasets.
    
    Handles dataset registration, storage, and retrieval.
    """
    
    def __init__(self, datasets_dir: Optional[str] = None):
        """
        Initialize the dataset manager.
        
        Args:
            datasets_dir: Directory to store dataset metadata
        """
        self.datasets_dir = Path(datasets_dir or "./data/training/datasets")
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        
        self._datasets: Dict[str, TrainingDataset] = {}
        self._load_datasets()
    
    def _load_datasets(self) -> None:
        """Load datasets from disk."""
        metadata_file = self.datasets_dir / "registry.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, "r") as f:
                    data = json.load(f)
                for ds_data in data.get("datasets", []):
                    ds = TrainingDataset.from_dict(ds_data)
                    self._datasets[ds.id] = ds
            except Exception as e:
                logger.warning(f"Failed to load dataset registry: {e}")
    
    def _save_registry(self) -> None:
        """Save dataset registry to disk."""
        metadata_file = self.datasets_dir / "registry.json"
        data = {
            "datasets": [ds.to_dict() for ds in self._datasets.values()]
        }
        with open(metadata_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def register(
        self,
        name: str,
        filepath: Optional[str] = None,
        hf_dataset_id: Optional[str] = None,
        format: DatasetFormat = DatasetFormat.ALPACA,
        description: str = "",
        tags: Optional[List[str]] = None,
    ) -> TrainingDataset:
        """
        Register a new training dataset.
        
        Args:
            name: Dataset name
            filepath: Local file path
            hf_dataset_id: HuggingFace dataset ID
            format: Dataset format
            description: Dataset description
            tags: Dataset tags
        
        Returns:
            Registered TrainingDataset
        """
        dataset_id = str(uuid.uuid4())
        
        # Determine num_samples and size
        num_samples = 0
        size_bytes = 0
        
        if filepath and Path(filepath).exists():
            size_bytes = Path(filepath).stat().st_size
            # Count samples
            try:
                if filepath.endswith(".json"):
                    with open(filepath, "r") as f:
                        data = json.load(f)
                        num_samples = len(data) if isinstance(data, list) else 1
                elif filepath.endswith(".jsonl"):
                    with open(filepath, "r") as f:
                        num_samples = sum(1 for line in f if line.strip())
            except Exception:
                pass
        
        dataset = TrainingDataset(
            id=dataset_id,
            name=name,
            description=description,
            format=format,
            filepath=filepath,
            hf_dataset_id=hf_dataset_id,
            num_samples=num_samples,
            size_bytes=size_bytes,
            tags=tags or [],
        )
        
        self._datasets[dataset_id] = dataset
        self._save_registry()
        
        logger.info(f"Registered dataset {name} with ID {dataset_id}")
        return dataset
    
    def get(self, dataset_id: str) -> Optional[TrainingDataset]:
        """Get a dataset by ID."""
        return self._datasets.get(dataset_id)
    
    def get_by_name(self, name: str) -> Optional[TrainingDataset]:
        """Get a dataset by name."""
        for ds in self._datasets.values():
            if ds.name == name:
                return ds
        return None
    
    def list(
        self,
        format: Optional[DatasetFormat] = None,
        tags: Optional[List[str]] = None,
    ) -> List[TrainingDataset]:
        """
        List datasets with optional filters.
        
        Args:
            format: Filter by format
            tags: Filter by tags (any match)
        
        Returns:
            List of matching datasets
        """
        datasets = list(self._datasets.values())
        
        if format:
            datasets = [ds for ds in datasets if ds.format == format]
        
        if tags:
            tag_set = set(tags)
            datasets = [ds for ds in datasets if tag_set & set(ds.tags)]
        
        return datasets
    
    def delete(self, dataset_id: str) -> bool:
        """Delete a dataset."""
        if dataset_id not in self._datasets:
            return False
        
        del self._datasets[dataset_id]
        self._save_registry()
        return True
    
    def update_tags(self, dataset_id: str, tags: List[str]) -> bool:
        """Update dataset tags."""
        dataset = self._datasets.get(dataset_id)
        if not dataset:
            return False
        
        dataset.tags = tags
        dataset.updated_at = datetime.utcnow().isoformat()
        self._save_registry()
        return True
    
    def create_from_samples(
        self,
        name: str,
        samples: List[Dict[str, Any]],
        format: DatasetFormat = DatasetFormat.ALPACA,
        description: str = "",
        tags: Optional[List[str]] = None,
    ) -> TrainingDataset:
        """
        Create a dataset from in-memory samples.
        
        Args:
            name: Dataset name
            samples: List of sample dictionaries
            format: Dataset format
            description: Dataset description
            tags: Dataset tags
        
        Returns:
            Created TrainingDataset
        """
        # Save samples to file
        dataset_id = str(uuid.uuid4())
        filepath = self.datasets_dir / f"{dataset_id}.jsonl"
        
        with open(filepath, "w", encoding="utf-8") as f:
            for sample in samples:
                f.write(json.dumps(sample, ensure_ascii=False) + "\n")
        
        return self.register(
            name=name,
            filepath=str(filepath),
            format=format,
            description=description,
            tags=tags,
        )
