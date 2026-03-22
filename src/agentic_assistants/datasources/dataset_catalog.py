"""
Dataset catalog for managing curated training datasets.

Provides registration, versioning, statistics, and lineage tracking
for datasets used in model fine-tuning pipelines.
"""

import json
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class DatasetEntry(BaseModel):
    """Metadata for a registered dataset."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    name: str
    version: str = "1.0.0"
    source_type: str = Field(description="local, huggingface, s3, url")
    source_path: str = ""
    format: str = "jsonl"
    schema_fields: List[str] = Field(default_factory=list)
    num_samples: int = 0
    size_bytes: int = 0
    tags: List[str] = Field(default_factory=list)
    lineage_id: Optional[str] = None
    project_id: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DatasetVersion(BaseModel):
    """A versioned snapshot of a dataset entry."""
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    dataset_id: str
    version_name: str
    snapshot_path: str = ""
    num_samples: int = 0
    created_at: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DatasetCatalog:
    """
    Manages a catalog of registered datasets with versioning and statistics.

    Datasets are persisted as JSON in a catalog directory. Each entry
    tracks source, format, size, and lineage metadata.

    Example:
        >>> catalog = DatasetCatalog(project_id="nemotron-coding")
        >>> entry = catalog.register("code-alpaca", "huggingface", "sahil2801/CodeAlpaca-20k")
        >>> entries = catalog.list()
        >>> stats = catalog.get_stats(entry.id)
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        data_dir: Optional[str] = None,
    ):
        self.project_id = project_id
        self.data_dir = Path(data_dir) if data_dir else Path("./data/datasets")
        self._catalog_file = self.data_dir / ".catalog.json"
        self._entries: Dict[str, DatasetEntry] = {}
        self._versions: Dict[str, List[DatasetVersion]] = {}
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_catalog()

    def _load_catalog(self) -> None:
        if self._catalog_file.exists():
            try:
                with open(self._catalog_file) as f:
                    data = json.load(f)
                for entry_data in data.get("entries", []):
                    entry = DatasetEntry(**entry_data)
                    self._entries[entry.id] = entry
                for vid, versions in data.get("versions", {}).items():
                    self._versions[vid] = [DatasetVersion(**v) for v in versions]
            except Exception as e:
                logger.warning(f"Failed to load catalog: {e}")

    def _save_catalog(self) -> None:
        data = {
            "entries": [e.model_dump() for e in self._entries.values()],
            "versions": {
                k: [v.model_dump() for v in vs]
                for k, vs in self._versions.items()
            },
        }
        with open(self._catalog_file, "w") as f:
            json.dump(data, f, indent=2)

    def register(
        self,
        name: str,
        source_type: str = "local",
        source_path: str = "",
        format: str = "jsonl",
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DatasetEntry:
        """Register a new dataset in the catalog."""
        existing = [e for e in self._entries.values() if e.name == name]
        if existing:
            entry = existing[0]
            entry.source_path = source_path or entry.source_path
            entry.updated_at = time.time()
            self._save_catalog()
            logger.info(f"Updated existing dataset entry: {name} ({entry.id})")
            return entry

        entry = DatasetEntry(
            name=name,
            source_type=source_type,
            source_path=source_path,
            format=format,
            project_id=project_id or self.project_id,
            tags=tags or [],
            metadata=metadata or {},
        )
        self._entries[entry.id] = entry
        self._save_catalog()
        logger.info(f"Registered dataset: {name} ({entry.id})")
        return entry

    def get(self, dataset_id: str) -> Optional[DatasetEntry]:
        return self._entries.get(dataset_id)

    def get_by_name(self, name: str) -> Optional[DatasetEntry]:
        for entry in self._entries.values():
            if entry.name == name:
                return entry
        return None

    def list(
        self,
        project_id: Optional[str] = None,
        source_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[DatasetEntry]:
        result = list(self._entries.values())
        if project_id:
            result = [e for e in result if e.project_id == project_id]
        if source_type:
            result = [e for e in result if e.source_type == source_type]
        if tags:
            tag_set = set(tags)
            result = [e for e in result if tag_set.issubset(set(e.tags))]
        return result

    def get_or_fetch(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Load dataset samples, fetching from source if needed."""
        entry = self.get(dataset_id)
        if not entry:
            entry = self.get_by_name(dataset_id)
        if not entry:
            logger.warning(f"Dataset not found: {dataset_id}")
            return []

        local_path = self.data_dir / f"{entry.name}.jsonl"
        if local_path.exists():
            return self._load_local(local_path)

        if entry.source_type == "huggingface":
            return self._fetch_huggingface(entry)
        elif entry.source_type in ("local", "file"):
            return self._load_local(Path(entry.source_path))

        return []

    def preview(self, dataset_id: str, n: int = 5) -> List[Dict[str, Any]]:
        samples = self.get_or_fetch(dataset_id)
        return samples[:n]

    def get_stats(self, dataset_id: str) -> Dict[str, Any]:
        """Compute statistics for a dataset."""
        samples = self.get_or_fetch(dataset_id)
        if not samples:
            return {"error": "No samples found"}

        lengths = [
            len(s.get("instruction", "")) + len(s.get("output", ""))
            for s in samples
        ]

        return {
            "num_samples": len(samples),
            "avg_length": sum(lengths) / max(len(lengths), 1),
            "min_length": min(lengths) if lengths else 0,
            "max_length": max(lengths) if lengths else 0,
            "fields": list(samples[0].keys()) if samples else [],
        }

    def version(
        self,
        dataset_id: str,
        version_name: str,
        snapshot_path: Optional[str] = None,
    ) -> DatasetVersion:
        """Create a versioned snapshot of a dataset."""
        entry = self.get(dataset_id)
        if not entry:
            raise ValueError(f"Dataset not found: {dataset_id}")

        ver = DatasetVersion(
            dataset_id=dataset_id,
            version_name=version_name,
            snapshot_path=snapshot_path or "",
            num_samples=entry.num_samples,
        )

        if dataset_id not in self._versions:
            self._versions[dataset_id] = []
        self._versions[dataset_id].append(ver)
        self._save_catalog()
        logger.info(f"Created version '{version_name}' for dataset {entry.name}")
        return ver

    def delete(self, dataset_id: str) -> bool:
        if dataset_id in self._entries:
            del self._entries[dataset_id]
            self._versions.pop(dataset_id, None)
            self._save_catalog()
            return True
        return False

    def _load_local(self, path: Path) -> List[Dict]:
        samples = []
        if not path.exists():
            return samples
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        samples.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
        return samples

    def _fetch_huggingface(self, entry: DatasetEntry) -> List[Dict]:
        try:
            from datasets import load_dataset
            ds = load_dataset(entry.source_path, split="train")
            samples = [dict(row) for row in ds]

            local_path = self.data_dir / f"{entry.name}.jsonl"
            with open(local_path, "w") as f:
                for s in samples:
                    f.write(json.dumps(s, ensure_ascii=False) + "\n")

            entry.num_samples = len(samples)
            entry.updated_at = time.time()
            self._save_catalog()
            return samples
        except Exception as e:
            logger.error(f"HuggingFace fetch failed: {e}")
            return []
