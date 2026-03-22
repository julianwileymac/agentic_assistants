"""
Dataset processing pipelines.

Provides cleaning, deduplication, quality filtering, and
tokenization-aware processing for coding datasets.
"""

import hashlib
from typing import Any, Callable, Dict, List, Optional, Set

from agentic_assistants.utils.logging import get_logger
from .sources import DatasetSample

logger = get_logger(__name__)


class DatasetProcessor:
    """
    Processes raw dataset samples through configurable pipeline steps.

    Supports deduplication, length filtering, language filtering,
    quality scoring, and custom transform functions.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._seen_hashes: Set[str] = set()

    def process(
        self,
        samples: List[DatasetSample],
        steps: Optional[List[str]] = None,
    ) -> List[DatasetSample]:
        """Run the processing pipeline on a list of samples."""
        steps = steps or ["dedup", "length_filter", "quality_filter"]
        result = samples

        for step in steps:
            before = len(result)
            if step == "dedup":
                result = self.deduplicate(result)
            elif step == "length_filter":
                result = self.filter_by_length(result)
            elif step == "language_filter":
                result = self.filter_by_language(result)
            elif step == "quality_filter":
                result = self.filter_by_quality(result)
            elif step == "normalize":
                result = self.normalize(result)
            logger.info(f"Step '{step}': {before} -> {len(result)} samples")

        return result

    def deduplicate(
        self,
        samples: List[DatasetSample],
        strategy: Optional[str] = None,
        threshold: Optional[float] = None,
    ) -> List[DatasetSample]:
        """Remove duplicate samples."""
        strategy = strategy or self.config.get("dedup_strategy", "exact_hash")
        threshold = threshold or self.config.get("dedup_threshold", 0.85)

        if strategy == "exact_hash":
            return self._dedup_exact(samples)
        elif strategy == "minhash":
            return self._dedup_minhash(samples, threshold)
        return samples

    def filter_by_length(
        self,
        samples: List[DatasetSample],
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> List[DatasetSample]:
        """Filter samples by text length."""
        min_len = min_length or self.config.get("min_length", 50)
        max_len = max_length or self.config.get("max_length", 8192)

        result = []
        for s in samples:
            total_len = len(s.instruction) + len(s.output)
            if min_len <= total_len <= max_len:
                result.append(s)
        return result

    def filter_by_language(
        self,
        samples: List[DatasetSample],
        allowed_languages: Optional[List[str]] = None,
    ) -> List[DatasetSample]:
        """Filter samples to only include specified programming languages."""
        allowed = allowed_languages or self.config.get("language_filter", [])
        if not allowed:
            return samples

        allowed_set = {lang.lower() for lang in allowed}
        result = []
        for s in samples:
            detected = self._detect_language(s.instruction + "\n" + s.output)
            if detected.lower() in allowed_set or detected == "unknown":
                result.append(s)
        return result

    def filter_by_quality(
        self,
        samples: List[DatasetSample],
        threshold: Optional[float] = None,
    ) -> List[DatasetSample]:
        """Filter by a heuristic quality score."""
        threshold = threshold or self.config.get("quality_threshold", 0.6)
        result = []
        for s in samples:
            score = self._compute_quality_score(s)
            if score >= threshold:
                s.metadata["quality_score"] = score
                result.append(s)
        return result

    def normalize(self, samples: List[DatasetSample]) -> List[DatasetSample]:
        """Normalize whitespace and formatting."""
        result = []
        for s in samples:
            normalized = DatasetSample(
                instruction=s.instruction.strip(),
                input=s.input.strip(),
                output=s.output.strip(),
                system=s.system.strip(),
                metadata=s.metadata,
            )
            result.append(normalized)
        return result

    def apply_transform(
        self,
        samples: List[DatasetSample],
        transform_fn: Callable[[DatasetSample], Optional[DatasetSample]],
    ) -> List[DatasetSample]:
        """Apply a custom transform function to each sample."""
        result = []
        for s in samples:
            transformed = transform_fn(s)
            if transformed is not None:
                result.append(transformed)
        return result

    def _dedup_exact(self, samples: List[DatasetSample]) -> List[DatasetSample]:
        seen: Set[str] = set()
        result = []
        for s in samples:
            content = s.instruction + "|" + s.output
            h = hashlib.md5(content.encode()).hexdigest()
            if h not in seen:
                seen.add(h)
                result.append(s)
        return result

    def _dedup_minhash(
        self, samples: List[DatasetSample], threshold: float
    ) -> List[DatasetSample]:
        """Approximate dedup using character n-gram shingling."""
        def shingle(text: str, n: int = 5) -> Set[str]:
            return {text[i:i + n] for i in range(max(len(text) - n + 1, 1))}

        def jaccard(a: Set[str], b: Set[str]) -> float:
            if not a or not b:
                return 0.0
            return len(a & b) / len(a | b)

        result = []
        shingles_list: List[Set[str]] = []

        for s in samples:
            content = s.instruction + " " + s.output
            s_shingles = shingle(content)

            is_dup = False
            for existing in shingles_list:
                if jaccard(s_shingles, existing) >= threshold:
                    is_dup = True
                    break

            if not is_dup:
                result.append(s)
                shingles_list.append(s_shingles)

        return result

    def _detect_language(self, text: str) -> str:
        indicators = {
            "python": ["def ", "import ", "class ", "self."],
            "javascript": ["function ", "const ", "let ", "=>"],
            "typescript": ["interface ", ": string", ": number"],
            "rust": ["fn ", "let mut", "impl ", "pub fn"],
            "go": ["func ", "package ", "import ("],
            "java": ["public class", "void main"],
            "c": ["#include", "int main(", "printf("],
            "cpp": ["#include", "std::", "cout <<"],
        }
        text_lower = text.lower()
        for lang, keywords in indicators.items():
            if any(kw.lower() in text_lower for kw in keywords):
                return lang
        return "unknown"

    def _compute_quality_score(self, sample: DatasetSample) -> float:
        score = 1.0

        if len(sample.instruction) < 10:
            score -= 0.3
        if len(sample.output) < 20:
            score -= 0.3
        if "```" in sample.output:
            score += 0.1
        if not sample.output.strip():
            score -= 0.5

        inst_lower = sample.instruction.lower()
        if any(w in inst_lower for w in ["write", "create", "implement", "build", "fix"]):
            score += 0.05

        return max(0.0, min(1.0, score))
