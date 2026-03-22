"""
Dataset source definitions.

Provides abstractions for loading coding datasets from local files,
HuggingFace Hub, remote URLs, and S3-compatible storage.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DatasetSample:
    """A single sample from a dataset source."""
    instruction: str = ""
    input: str = ""
    output: str = ""
    system: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class DatasetSource(ABC):
    """Base class for dataset sources."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}

    @abstractmethod
    def load(self, sample_size: Optional[int] = None) -> List[DatasetSample]:
        """Load samples from the source."""
        ...

    @abstractmethod
    def stream(self) -> Iterator[DatasetSample]:
        """Stream samples from the source."""
        ...

    def get_info(self) -> Dict[str, Any]:
        """Return metadata about the source."""
        return {"name": self.name, "type": self.__class__.__name__, "config": self.config}


class HuggingFaceSource(DatasetSource):
    """Load datasets from HuggingFace Hub."""

    def __init__(
        self,
        name: str,
        path: str,
        subset: Optional[str] = None,
        split: str = "train",
        format: str = "alpaca",
        filters: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)
        self.path = path
        self.subset = subset
        self.split = split
        self.format = format
        self.filters = filters or {}

    def load(self, sample_size: Optional[int] = None) -> List[DatasetSample]:
        try:
            from datasets import load_dataset
        except ImportError:
            logger.error("datasets library not installed")
            return []

        logger.info(f"Loading HuggingFace dataset: {self.path}")
        kwargs: Dict[str, Any] = {"split": self.split}
        if self.subset:
            kwargs["name"] = self.subset

        dataset = load_dataset(self.path, **kwargs)

        if sample_size and len(dataset) > sample_size:
            dataset = dataset.select(range(sample_size))

        samples = []
        for row in dataset:
            sample = self._convert_row(row)
            if self._passes_filters(sample):
                samples.append(sample)

        logger.info(f"Loaded {len(samples)} samples from {self.path}")
        return samples

    def stream(self) -> Iterator[DatasetSample]:
        try:
            from datasets import load_dataset
        except ImportError:
            return

        kwargs: Dict[str, Any] = {"split": self.split, "streaming": True}
        if self.subset:
            kwargs["name"] = self.subset

        dataset = load_dataset(self.path, **kwargs)
        for row in dataset:
            sample = self._convert_row(row)
            if self._passes_filters(sample):
                yield sample

    def _convert_row(self, row: Dict[str, Any]) -> DatasetSample:
        if self.format == "alpaca":
            return DatasetSample(
                instruction=row.get("instruction", ""),
                input=row.get("input", ""),
                output=row.get("output", ""),
                metadata={"source": self.path, "format": "alpaca"},
            )
        elif self.format == "sharegpt":
            conversations = row.get("conversations", [])
            instruction = ""
            output = ""
            system = ""
            for msg in conversations:
                role = msg.get("from", msg.get("role", ""))
                value = msg.get("value", msg.get("content", ""))
                if role in ("human", "user"):
                    instruction = value
                elif role in ("gpt", "assistant"):
                    output = value
                elif role == "system":
                    system = value
            return DatasetSample(
                instruction=instruction, output=output, system=system,
                metadata={"source": self.path, "format": "sharegpt"},
            )
        else:
            text = row.get("text", row.get("content", str(row)))
            return DatasetSample(
                instruction=text,
                metadata={"source": self.path, "format": "raw"},
            )

    def _passes_filters(self, sample: DatasetSample) -> bool:
        if "category" in self.filters:
            expected = self.filters["category"]
            if sample.metadata.get("category") != expected:
                text = (sample.instruction + sample.output).lower()
                if expected.lower() not in text:
                    return False
        return True


class LocalFileSource(DatasetSource):
    """Load datasets from local files (JSONL, JSON, Parquet, CSV)."""

    def __init__(
        self,
        name: str,
        path: str,
        format: str = "jsonl",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)
        self.path = Path(path)
        self.format = format

    def load(self, sample_size: Optional[int] = None) -> List[DatasetSample]:
        if not self.path.exists():
            logger.warning(f"Path does not exist: {self.path}")
            return []

        files = []
        if self.path.is_dir():
            patterns = {"jsonl": "*.jsonl", "json": "*.json",
                        "parquet": "*.parquet", "csv": "*.csv"}
            pattern = patterns.get(self.format, f"*.{self.format}")
            files = list(self.path.glob(pattern))
        elif self.path.is_file():
            files = [self.path]

        samples = []
        for file_path in files:
            samples.extend(self._load_file(file_path))
            if sample_size and len(samples) >= sample_size:
                samples = samples[:sample_size]
                break

        logger.info(f"Loaded {len(samples)} samples from {self.path}")
        return samples

    def stream(self) -> Iterator[DatasetSample]:
        if not self.path.exists():
            return
        files = [self.path] if self.path.is_file() else list(
            self.path.glob(f"*.{self.format}")
        )
        for f in files:
            yield from self._load_file(f)

    def _load_file(self, file_path: Path) -> List[DatasetSample]:
        import json
        samples = []
        suffix = file_path.suffix.lower()

        try:
            if suffix == ".jsonl":
                with open(file_path) as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            row = json.loads(line)
                            samples.append(DatasetSample(
                                instruction=row.get("instruction", row.get("prompt", "")),
                                input=row.get("input", ""),
                                output=row.get("output", row.get("response", "")),
                                system=row.get("system", ""),
                                metadata={"source": str(file_path)},
                            ))
            elif suffix == ".json":
                with open(file_path) as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for row in data:
                        samples.append(DatasetSample(
                            instruction=row.get("instruction", row.get("prompt", "")),
                            input=row.get("input", ""),
                            output=row.get("output", row.get("response", "")),
                            system=row.get("system", ""),
                            metadata={"source": str(file_path)},
                        ))
            elif suffix == ".parquet":
                try:
                    import pyarrow.parquet as pq
                    table = pq.read_table(file_path)
                    for row in table.to_pylist():
                        samples.append(DatasetSample(
                            instruction=row.get("instruction", row.get("prompt", "")),
                            input=row.get("input", ""),
                            output=row.get("output", row.get("response", "")),
                            metadata={"source": str(file_path)},
                        ))
                except ImportError:
                    logger.warning("pyarrow not installed, skipping parquet file")
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")

        return samples


class RemoteURLSource(DatasetSource):
    """Load datasets from remote URLs."""

    def __init__(
        self,
        name: str,
        url: str,
        format: str = "jsonl",
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config)
        self.url = url
        self.format = format

    def load(self, sample_size: Optional[int] = None) -> List[DatasetSample]:
        import tempfile
        try:
            import httpx
            logger.info(f"Downloading dataset from {self.url}")
            response = httpx.get(self.url, follow_redirects=True, timeout=300)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(
                suffix=f".{self.format}", delete=False, mode="wb"
            ) as f:
                f.write(response.content)
                tmp_path = f.name

            local_source = LocalFileSource(
                name=self.name, path=tmp_path, format=self.format,
            )
            return local_source.load(sample_size=sample_size)
        except Exception as e:
            logger.error(f"Failed to download {self.url}: {e}")
            return []

    def stream(self) -> Iterator[DatasetSample]:
        samples = self.load()
        yield from samples


def create_source(source_config: Dict[str, Any]) -> DatasetSource:
    """Factory to create a DatasetSource from a config dict."""
    source_type = source_config.get("type", "local")
    name = source_config.get("name", "unnamed")

    if source_type == "huggingface":
        return HuggingFaceSource(
            name=name,
            path=source_config["path"],
            subset=source_config.get("subset"),
            format=source_config.get("format", "alpaca"),
            filters=source_config.get("filters"),
            config=source_config,
        )
    elif source_type == "local":
        return LocalFileSource(
            name=name,
            path=source_config["path"],
            format=source_config.get("format", "jsonl"),
            config=source_config,
        )
    elif source_type == "url":
        return RemoteURLSource(
            name=name,
            url=source_config["path"],
            format=source_config.get("format", "jsonl"),
            config=source_config,
        )
    else:
        raise ValueError(f"Unknown source type: {source_type}")
