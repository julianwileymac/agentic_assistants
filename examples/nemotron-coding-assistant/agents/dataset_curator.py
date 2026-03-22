"""
Dataset Curator Agent.

Assists in curating, filtering, and annotating training data
for the nemotron fine-tuning pipeline.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class QualityReport:
    """Quality assessment of a dataset sample."""
    score: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CurationResult:
    """Result of a dataset curation operation."""
    total_samples: int
    accepted: int
    rejected: int
    quality_distribution: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DatasetCuratorAgent:
    """
    Agent that assists in curating training datasets.

    Evaluates sample quality, detects duplicates, annotates examples
    with metadata, and provides recommendations for dataset improvement.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        dataset_catalog: Optional[Any] = None,
    ):
        self.config = config or {}
        self.dataset_catalog = dataset_catalog
        self.llm_config = self.config.get("llm", {})

    def assess_quality(
        self,
        samples: List[Dict[str, Any]],
        criteria: Optional[Dict[str, Any]] = None,
    ) -> List[QualityReport]:
        """Assess quality of dataset samples."""
        criteria = criteria or {
            "min_instruction_length": 10,
            "min_response_length": 50,
            "max_response_length": 8192,
            "require_code_block": True,
        }

        reports = []
        for sample in samples:
            score, issues, suggestions = self._evaluate_sample(sample, criteria)
            reports.append(QualityReport(
                score=score, issues=issues, suggestions=suggestions,
                metadata={"sample_id": sample.get("id", "")},
            ))

        return reports

    def filter_dataset(
        self,
        samples: List[Dict[str, Any]],
        min_quality: float = 0.6,
        criteria: Optional[Dict[str, Any]] = None,
    ) -> CurationResult:
        """Filter a dataset by quality threshold."""
        reports = self.assess_quality(samples, criteria)

        accepted = 0
        rejected = 0
        distribution = {"high": 0, "medium": 0, "low": 0}

        for report in reports:
            if report.score >= min_quality:
                accepted += 1
            else:
                rejected += 1

            if report.score >= 0.8:
                distribution["high"] += 1
            elif report.score >= 0.5:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1

        return CurationResult(
            total_samples=len(samples),
            accepted=accepted,
            rejected=rejected,
            quality_distribution=distribution,
        )

    def annotate_samples(
        self,
        samples: List[Dict[str, Any]],
        annotation_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Add metadata annotations to samples."""
        annotation_types = annotation_types or ["language", "difficulty", "topic"]
        annotated = []

        for sample in samples:
            annotations = {}
            text = sample.get("instruction", "") + " " + sample.get("output", "")

            if "language" in annotation_types:
                annotations["detected_language"] = self._detect_programming_language(text)
            if "difficulty" in annotation_types:
                annotations["estimated_difficulty"] = self._estimate_difficulty(text)
            if "topic" in annotation_types:
                annotations["topic"] = self._classify_topic(text)

            annotated_sample = {**sample, "annotations": annotations}
            annotated.append(annotated_sample)

        return annotated

    def suggest_improvements(
        self,
        dataset_stats: Dict[str, Any],
    ) -> List[str]:
        """Suggest improvements for the dataset based on statistics."""
        suggestions = []

        total = dataset_stats.get("total_samples", 0)
        if total < 1000:
            suggestions.append(
                f"Dataset has only {total} samples. Consider adding more sources "
                "for better generalization."
            )

        lang_dist = dataset_stats.get("language_distribution", {})
        if lang_dist:
            dominant = max(lang_dist.values()) / max(sum(lang_dist.values()), 1)
            if dominant > 0.7:
                suggestions.append(
                    "Dataset is heavily skewed toward one language. "
                    "Consider balancing language distribution."
                )

        avg_length = dataset_stats.get("avg_response_length", 0)
        if avg_length < 100:
            suggestions.append("Average response length is short. Add more detailed examples.")

        return suggestions

    def _evaluate_sample(
        self,
        sample: Dict[str, Any],
        criteria: Dict[str, Any],
    ) -> tuple:
        """Evaluate a single sample against quality criteria."""
        score = 1.0
        issues = []
        suggestions = []

        instruction = sample.get("instruction", "")
        output = sample.get("output", sample.get("response", ""))

        min_inst_len = criteria.get("min_instruction_length", 10)
        if len(instruction) < min_inst_len:
            score -= 0.3
            issues.append(f"Instruction too short ({len(instruction)} chars)")

        min_resp_len = criteria.get("min_response_length", 50)
        max_resp_len = criteria.get("max_response_length", 8192)
        if len(output) < min_resp_len:
            score -= 0.3
            issues.append(f"Response too short ({len(output)} chars)")
        elif len(output) > max_resp_len:
            score -= 0.1
            issues.append(f"Response very long ({len(output)} chars)")
            suggestions.append("Consider splitting into multiple examples")

        if criteria.get("require_code_block") and "```" not in output:
            score -= 0.2
            suggestions.append("Response lacks code blocks")

        return max(0.0, score), issues, suggestions

    def _detect_programming_language(self, text: str) -> str:
        lang_keywords = {
            "python": ["def ", "import ", "class ", "self.", "print("],
            "javascript": ["function ", "const ", "let ", "var ", "=>"],
            "typescript": ["interface ", ": string", ": number", "type "],
            "rust": ["fn ", "let mut", "impl ", "pub fn", "->"],
            "go": ["func ", "package ", "import (", "fmt."],
            "java": ["public class", "System.out", "void main"],
        }
        text_lower = text.lower()
        scores = {}
        for lang, keywords in lang_keywords.items():
            scores[lang] = sum(1 for kw in keywords if kw.lower() in text_lower)
        if not scores or max(scores.values()) == 0:
            return "unknown"
        return max(scores, key=scores.get)

    def _estimate_difficulty(self, text: str) -> str:
        length = len(text)
        if length < 200:
            return "easy"
        elif length < 1000:
            return "medium"
        return "hard"

    def _classify_topic(self, text: str) -> str:
        topic_keywords = {
            "algorithms": ["sort", "search", "tree", "graph", "dynamic programming"],
            "web": ["http", "api", "rest", "html", "css", "react", "flask", "django"],
            "data": ["dataframe", "csv", "json", "sql", "database", "pandas"],
            "ml": ["model", "train", "predict", "neural", "tensorflow", "pytorch"],
            "devops": ["docker", "kubernetes", "ci/cd", "deploy", "container"],
            "testing": ["test", "assert", "mock", "fixture", "pytest"],
        }
        text_lower = text.lower()
        scores = {}
        for topic, keywords in topic_keywords.items():
            scores[topic] = sum(1 for kw in keywords if kw in text_lower)
        if not scores or max(scores.values()) == 0:
            return "general"
        return max(scores, key=scores.get)
