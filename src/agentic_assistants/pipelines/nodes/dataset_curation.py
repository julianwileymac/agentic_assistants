"""
Dataset curation pipeline nodes.

Provides BaseFlowNode subclasses for building dataset curation pipelines:
source loading, filtering, transformation, formatting, validation,
splitting, and export.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from agentic_assistants.pipelines.nodes.base import BaseFlowNode, NodeConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Configs
# ---------------------------------------------------------------------------

@dataclass
class DatasetSourceConfig(NodeConfig):
    source_type: str = "local"
    source_path: str = ""
    format: str = "jsonl"
    filters: Dict[str, Any] = field(default_factory=dict)
    sample_size: Optional[int] = None
    hf_subset: Optional[str] = None
    hf_split: str = "train"


@dataclass
class DatasetFilterConfig(NodeConfig):
    min_length: int = 50
    max_length: int = 8192
    language: Optional[str] = None
    dedup_strategy: str = "exact_hash"
    dedup_threshold: float = 0.85
    quality_threshold: float = 0.6


@dataclass
class DatasetTransformConfig(NodeConfig):
    transform_type: str = "column_mapping"
    column_mapping: Dict[str, str] = field(default_factory=dict)
    template: str = ""
    expression: str = ""


@dataclass
class DatasetFormatConfig(NodeConfig):
    output_format: str = "sharegpt"
    instruction_col: str = "instruction"
    input_col: str = "input"
    output_col: str = "output"
    system_prompt: str = ""


@dataclass
class DatasetValidationConfig(NodeConfig):
    required_fields: List[str] = field(default_factory=lambda: ["instruction", "output"])
    max_token_length: int = 8192
    tokenizer: Optional[str] = None
    schema: Dict[str, str] = field(default_factory=dict)


@dataclass
class DatasetSplitConfig(NodeConfig):
    train_ratio: float = 0.9
    val_ratio: float = 0.05
    test_ratio: float = 0.05
    stratify_by: Optional[str] = None
    seed: int = 42


@dataclass
class DatasetExportConfig(NodeConfig):
    output_path: str = "./data/datasets/output"
    file_format: str = "jsonl"
    push_to_hub: bool = False
    hub_repo_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

class DatasetSourceNode(BaseFlowNode):
    """Load data from registered sources (local, HuggingFace, API, S3)."""

    node_type = "dataset_source"
    config_class = DatasetSourceConfig

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        cfg: DatasetSourceConfig = self.config
        source_type = inputs.get("source_type", cfg.source_type)
        source_path = inputs.get("source_path", cfg.source_path)
        sample_size = inputs.get("sample_size", cfg.sample_size)

        logger.info(f"Loading dataset from {source_type}: {source_path}")
        samples: List[Dict[str, Any]] = []

        if source_type == "huggingface":
            samples = self._load_huggingface(source_path, sample_size)
        elif source_type in ("local", "file"):
            samples = self._load_local(source_path)
        elif source_type == "catalog":
            catalog_id = inputs.get("catalog_id", source_path)
            samples = self._load_from_catalog(catalog_id)
        else:
            logger.warning(f"Unknown source type: {source_type}")

        if sample_size and len(samples) > sample_size:
            samples = samples[:sample_size]

        self.emit_metric("samples_loaded", len(samples))
        return {"samples": samples, "count": len(samples)}

    def _load_huggingface(self, path: str, sample_size: Optional[int]) -> List[Dict]:
        try:
            from datasets import load_dataset
            cfg: DatasetSourceConfig = self.config
            kwargs: Dict[str, Any] = {"split": cfg.hf_split}
            if cfg.hf_subset:
                kwargs["name"] = cfg.hf_subset
            ds = load_dataset(path, **kwargs)
            if sample_size and len(ds) > sample_size:
                ds = ds.select(range(sample_size))
            return [dict(row) for row in ds]
        except Exception as e:
            logger.error(f"HuggingFace load failed: {e}")
            return []

    def _load_local(self, path: str) -> List[Dict]:
        p = Path(path)
        if not p.exists():
            return []
        samples = []
        files = [p] if p.is_file() else list(p.glob("*.jsonl")) + list(p.glob("*.json"))
        for f in files:
            try:
                if f.suffix == ".jsonl":
                    with open(f) as fh:
                        for line in fh:
                            line = line.strip()
                            if line:
                                samples.append(json.loads(line))
                elif f.suffix == ".json":
                    with open(f) as fh:
                        data = json.load(fh)
                    if isinstance(data, list):
                        samples.extend(data)
            except Exception as e:
                logger.error(f"Error loading {f}: {e}")
        return samples

    def _load_from_catalog(self, catalog_id: str) -> List[Dict]:
        try:
            from agentic_assistants.datasources.dataset_catalog import DatasetCatalog
            catalog = DatasetCatalog()
            return catalog.get_or_fetch(catalog_id)
        except Exception as e:
            logger.error(f"Catalog load failed: {e}")
            return []


class DatasetFilterNode(BaseFlowNode):
    """Filter samples by length, language, dedup, and quality."""

    node_type = "dataset_filter"
    config_class = DatasetFilterConfig

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        cfg: DatasetFilterConfig = self.config
        samples: List[Dict] = inputs.get("samples", [])
        original_count = len(samples)

        # Length filter
        samples = [
            s for s in samples
            if cfg.min_length <= self._text_length(s) <= cfg.max_length
        ]

        # Dedup
        if cfg.dedup_strategy == "exact_hash":
            samples = self._dedup_exact(samples)

        # Quality filter
        samples = [s for s in samples if self._quality_score(s) >= cfg.quality_threshold]

        removed = original_count - len(samples)
        self.emit_metric("samples_removed", removed)
        self.emit_metric("samples_remaining", len(samples))
        self.emit_rl_metric("filter_retention_rate", len(samples) / max(original_count, 1))
        return {"samples": samples, "count": len(samples), "removed": removed}

    def _text_length(self, sample: Dict) -> int:
        return len(sample.get("instruction", "")) + len(sample.get("output", ""))

    def _dedup_exact(self, samples: List[Dict]) -> List[Dict]:
        seen: Set[str] = set()
        result = []
        for s in samples:
            key = (s.get("instruction", "") + "|" + s.get("output", ""))
            h = hashlib.md5(key.encode()).hexdigest()
            if h not in seen:
                seen.add(h)
                result.append(s)
        return result

    def _quality_score(self, sample: Dict) -> float:
        score = 1.0
        if len(sample.get("instruction", "")) < 10:
            score -= 0.3
        if len(sample.get("output", "")) < 20:
            score -= 0.3
        if "```" in sample.get("output", ""):
            score += 0.1
        return max(0.0, min(1.0, score))


class DatasetTransformNode(BaseFlowNode):
    """Apply transformations: column mapping, templates, expressions."""

    node_type = "dataset_transform"
    config_class = DatasetTransformConfig

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        cfg: DatasetTransformConfig = self.config
        samples: List[Dict] = inputs.get("samples", [])

        if cfg.transform_type == "column_mapping" and cfg.column_mapping:
            samples = [self._remap_columns(s, cfg.column_mapping) for s in samples]
        elif cfg.transform_type == "template" and cfg.template:
            samples = [self._apply_template(s, cfg.template) for s in samples]

        self.emit_metric("samples_transformed", len(samples))
        return {"samples": samples, "count": len(samples)}

    def _remap_columns(self, sample: Dict, mapping: Dict[str, str]) -> Dict:
        result = dict(sample)
        for src, dst in mapping.items():
            if src in result:
                result[dst] = result.pop(src)
        return result

    def _apply_template(self, sample: Dict, template: str) -> Dict:
        try:
            text = template.format(**sample)
            sample["text"] = text
        except KeyError:
            pass
        return sample


class DatasetFormatNode(BaseFlowNode):
    """Convert samples to a target training format."""

    node_type = "dataset_format"
    config_class = DatasetFormatConfig

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        cfg: DatasetFormatConfig = self.config
        samples: List[Dict] = inputs.get("samples", [])
        fmt = inputs.get("output_format", cfg.output_format)

        formatted = []
        for s in samples:
            if fmt == "alpaca":
                formatted.append(self._to_alpaca(s, cfg))
            elif fmt == "sharegpt":
                formatted.append(self._to_sharegpt(s, cfg))
            elif fmt == "openai":
                formatted.append(self._to_openai(s, cfg))
            elif fmt == "dpo":
                item = self._to_dpo(s, cfg)
                if item:
                    formatted.append(item)
            else:
                formatted.append(s)

        self.emit_metric("samples_formatted", len(formatted))
        return {"samples": formatted, "count": len(formatted), "format": fmt}

    def _to_alpaca(self, s: Dict, cfg: DatasetFormatConfig) -> Dict:
        return {
            "instruction": s.get(cfg.instruction_col, ""),
            "input": s.get(cfg.input_col, ""),
            "output": s.get(cfg.output_col, ""),
        }

    def _to_sharegpt(self, s: Dict, cfg: DatasetFormatConfig) -> Dict:
        convos = []
        if cfg.system_prompt:
            convos.append({"from": "system", "value": cfg.system_prompt})
        user_msg = s.get(cfg.instruction_col, "")
        inp = s.get(cfg.input_col, "")
        if inp:
            user_msg += f"\n\n{inp}"
        convos.append({"from": "human", "value": user_msg})
        convos.append({"from": "gpt", "value": s.get(cfg.output_col, "")})
        return {"conversations": convos}

    def _to_openai(self, s: Dict, cfg: DatasetFormatConfig) -> Dict:
        messages = []
        if cfg.system_prompt:
            messages.append({"role": "system", "content": cfg.system_prompt})
        messages.append({"role": "user", "content": s.get(cfg.instruction_col, "")})
        messages.append({"role": "assistant", "content": s.get(cfg.output_col, "")})
        return {"messages": messages}

    def _to_dpo(self, s: Dict, cfg: DatasetFormatConfig) -> Optional[Dict]:
        chosen = s.get("chosen", s.get(cfg.output_col, ""))
        rejected = s.get("rejected", "")
        if not rejected:
            return None
        return {
            "prompt": s.get(cfg.instruction_col, ""),
            "chosen": chosen,
            "rejected": rejected,
        }


class DatasetValidationNode(BaseFlowNode):
    """Validate dataset samples against a schema and constraints."""

    node_type = "dataset_validation"
    config_class = DatasetValidationConfig

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        cfg: DatasetValidationConfig = self.config
        samples: List[Dict] = inputs.get("samples", [])

        valid = []
        errors: List[Dict[str, Any]] = []

        for i, s in enumerate(samples):
            sample_errors = []
            for field_name in cfg.required_fields:
                if not s.get(field_name):
                    sample_errors.append(f"Missing required field: {field_name}")

            total_len = sum(len(str(v)) for v in s.values())
            if total_len > cfg.max_token_length * 4:
                sample_errors.append(f"Sample too long: ~{total_len} chars")

            if sample_errors:
                errors.append({"index": i, "errors": sample_errors})
            else:
                valid.append(s)

        self.emit_metric("valid_samples", len(valid))
        self.emit_metric("invalid_samples", len(errors))
        return {"samples": valid, "count": len(valid), "errors": errors}


class DatasetSplitNode(BaseFlowNode):
    """Split dataset into train/validation/test sets."""

    node_type = "dataset_split"
    config_class = DatasetSplitConfig

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        import random

        cfg: DatasetSplitConfig = self.config
        samples: List[Dict] = inputs.get("samples", [])

        rng = random.Random(cfg.seed)
        shuffled = list(samples)
        rng.shuffle(shuffled)

        n = len(shuffled)
        n_train = int(n * cfg.train_ratio)
        n_val = int(n * cfg.val_ratio)

        train = shuffled[:n_train]
        val = shuffled[n_train:n_train + n_val]
        test = shuffled[n_train + n_val:]

        self.emit_metric("train_samples", len(train))
        self.emit_metric("val_samples", len(val))
        self.emit_metric("test_samples", len(test))

        return {
            "train": train,
            "val": val,
            "test": test,
            "counts": {"train": len(train), "val": len(val), "test": len(test)},
        }


class DatasetExportNode(BaseFlowNode):
    """Write dataset to disk or push to HuggingFace Hub."""

    node_type = "dataset_export"
    config_class = DatasetExportConfig

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        cfg: DatasetExportConfig = self.config
        samples: List[Dict] = inputs.get("samples", inputs.get("train", []))
        output_path = Path(inputs.get("output_path", cfg.output_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if cfg.file_format == "jsonl":
            with open(output_path, "w") as f:
                for s in samples:
                    f.write(json.dumps(s, ensure_ascii=False) + "\n")
        elif cfg.file_format == "json":
            with open(output_path, "w") as f:
                json.dump(samples, f, indent=2, ensure_ascii=False)
        elif cfg.file_format == "parquet":
            try:
                import pyarrow as pa
                import pyarrow.parquet as pq
                table = pa.Table.from_pylist(samples)
                pq.write_table(table, str(output_path))
            except ImportError:
                logger.warning("pyarrow not installed, falling back to JSONL")
                output_path = output_path.with_suffix(".jsonl")
                with open(output_path, "w") as f:
                    for s in samples:
                        f.write(json.dumps(s, ensure_ascii=False) + "\n")

        if cfg.push_to_hub and cfg.hub_repo_id:
            self._push_to_hub(str(output_path), cfg.hub_repo_id)

        self.emit_metric("samples_exported", len(samples))
        logger.info(f"Exported {len(samples)} samples to {output_path}")
        return {"path": str(output_path), "count": len(samples)}

    def _push_to_hub(self, path: str, repo_id: str) -> None:
        try:
            from huggingface_hub import HfApi
            api = HfApi()
            api.upload_file(path_or_fileobj=path, path_in_repo=Path(path).name, repo_id=repo_id)
            logger.info(f"Pushed to HuggingFace Hub: {repo_id}")
        except Exception as e:
            logger.error(f"Hub push failed: {e}")
