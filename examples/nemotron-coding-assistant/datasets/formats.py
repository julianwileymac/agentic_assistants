"""
Output format converters for training datasets.

Converts processed samples into standard training formats:
Alpaca, ShareGPT, OpenAI Chat, and DPO preference pairs.
"""

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger
from .sources import DatasetSample

logger = get_logger(__name__)


class OutputFormat(str, Enum):
    ALPACA = "alpaca"
    SHAREGPT = "sharegpt"
    OPENAI = "openai"
    DPO = "dpo"
    CHATML = "chatml"


class DatasetFormatter:
    """
    Converts dataset samples into training-ready formats.

    Supports Alpaca, ShareGPT, OpenAI Chat, ChatML, and DPO pair formats.
    Can write output as JSONL, JSON, or Parquet.
    """

    def __init__(
        self,
        system_prompt: str = "",
        default_format: OutputFormat = OutputFormat.SHAREGPT,
    ):
        self.system_prompt = system_prompt
        self.default_format = default_format

    def format(
        self,
        samples: List[DatasetSample],
        output_format: Optional[OutputFormat] = None,
    ) -> List[Dict[str, Any]]:
        """Convert samples to the target format."""
        fmt = output_format or self.default_format

        if fmt == OutputFormat.ALPACA:
            return [self._to_alpaca(s) for s in samples]
        elif fmt == OutputFormat.SHAREGPT:
            return [self._to_sharegpt(s) for s in samples]
        elif fmt == OutputFormat.OPENAI:
            return [self._to_openai(s) for s in samples]
        elif fmt == OutputFormat.DPO:
            return self._to_dpo(samples)
        elif fmt == OutputFormat.CHATML:
            return [self._to_chatml(s) for s in samples]
        else:
            raise ValueError(f"Unknown format: {fmt}")

    def write(
        self,
        samples: List[DatasetSample],
        output_path: str,
        output_format: Optional[OutputFormat] = None,
        file_format: str = "jsonl",
    ) -> Dict[str, Any]:
        """Format and write samples to disk."""
        formatted = self.format(samples, output_format)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if file_format == "jsonl":
            with open(path, "w") as f:
                for item in formatted:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
        elif file_format == "json":
            with open(path, "w") as f:
                json.dump(formatted, f, indent=2, ensure_ascii=False)
        elif file_format == "parquet":
            try:
                import pyarrow as pa
                import pyarrow.parquet as pq
                table = pa.Table.from_pylist(formatted)
                pq.write_table(table, path)
            except ImportError:
                logger.error("pyarrow not installed, falling back to JSONL")
                return self.write(samples, output_path, output_format, "jsonl")
        else:
            raise ValueError(f"Unknown file format: {file_format}")

        logger.info(f"Wrote {len(formatted)} samples to {path}")
        return {
            "path": str(path),
            "format": (output_format or self.default_format).value,
            "file_format": file_format,
            "num_samples": len(formatted),
        }

    def _to_alpaca(self, sample: DatasetSample) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "instruction": sample.instruction,
            "output": sample.output,
        }
        if sample.input:
            result["input"] = sample.input
        if sample.system or self.system_prompt:
            result["system"] = sample.system or self.system_prompt
        return result

    def _to_sharegpt(self, sample: DatasetSample) -> Dict[str, Any]:
        conversations = []
        system = sample.system or self.system_prompt
        if system:
            conversations.append({"from": "system", "value": system})
        user_msg = sample.instruction
        if sample.input:
            user_msg += f"\n\n{sample.input}"
        conversations.append({"from": "human", "value": user_msg})
        conversations.append({"from": "gpt", "value": sample.output})
        return {"conversations": conversations}

    def _to_openai(self, sample: DatasetSample) -> Dict[str, Any]:
        messages = []
        system = sample.system or self.system_prompt
        if system:
            messages.append({"role": "system", "content": system})
        user_msg = sample.instruction
        if sample.input:
            user_msg += f"\n\n{sample.input}"
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": sample.output})
        return {"messages": messages}

    def _to_chatml(self, sample: DatasetSample) -> Dict[str, Any]:
        parts = []
        system = sample.system or self.system_prompt
        if system:
            parts.append(f"<|im_start|>system\n{system}<|im_end|>")
        user_msg = sample.instruction
        if sample.input:
            user_msg += f"\n\n{sample.input}"
        parts.append(f"<|im_start|>user\n{user_msg}<|im_end|>")
        parts.append(f"<|im_start|>assistant\n{sample.output}<|im_end|>")
        return {"text": "\n".join(parts)}

    def _to_dpo(self, samples: List[DatasetSample]) -> List[Dict[str, Any]]:
        """
        Convert samples to DPO format.

        Requires samples to have 'chosen' and 'rejected' in metadata,
        or falls back to generating placeholder pairs.
        """
        pairs = []
        for sample in samples:
            chosen = sample.metadata.get("chosen", sample.output)
            rejected = sample.metadata.get("rejected", "")
            if not rejected:
                continue
            pairs.append({
                "prompt": sample.instruction,
                "chosen": chosen,
                "rejected": rejected,
            })
        return pairs
