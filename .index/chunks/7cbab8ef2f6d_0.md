# Chunk: 7cbab8ef2f6d_0

- source: `src/agentic_assistants/data/training/quality.py`
- lines: 1-99
- chunk: 1/6

```
"""
Data quality metrics and checking for training datasets.

This module provides utilities for assessing the quality of training data.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import re

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DataQualityMetrics:
    """Quality metrics for a dataset or data sample."""
    
    # Completeness metrics
    completeness_score: float = 1.0  # 0-1, ratio of non-empty fields
    missing_fields: List[str] = field(default_factory=list)
    
    # Length metrics
    avg_length: float = 0.0
    min_length: int = 0
    max_length: int = 0
    length_variance: float = 0.0
    
    # Content metrics
    unique_ratio: float = 1.0  # Ratio of unique samples
    duplicate_count: int = 0
    
    # Format metrics
    format_valid: bool = True
    format_errors: List[str] = field(default_factory=list)
    
    # Text quality metrics
    avg_word_count: float = 0.0
    vocabulary_size: int = 0
    
    # Language metrics
    detected_language: Optional[str] = None
    language_consistency: float = 1.0
    
    # Custom metrics
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "completeness_score": self.completeness_score,
            "missing_fields": self.missing_fields,
            "avg_length": self.avg_length,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "length_variance": self.length_variance,
            "unique_ratio": self.unique_ratio,
            "duplicate_count": self.duplicate_count,
            "format_valid": self.format_valid,
            "format_errors": self.format_errors,
            "avg_word_count": self.avg_word_count,
            "vocabulary_size": self.vocabulary_size,
            "detected_language": self.detected_language,
            "language_consistency": self.language_consistency,
            **self.custom_metrics,
        }
    
    @property
    def overall_score(self) -> float:
        """Calculate overall quality score."""
        scores = [
            self.completeness_score,
            self.unique_ratio,
            1.0 if self.format_valid else 0.5,
            self.language_consistency,
        ]
        return sum(scores) / len(scores)


class DataQualityChecker:
    """
    Check and compute quality metrics for training data.
    
    Supports:
    - Instruct datasets (instruction, input, output)
    - Preference datasets (prompt, chosen, rejected)
    - General text datasets
    """
    
    def __init__(self):
        """Initialize the quality checker."""
        pass
    
    def check_instruct_dataset(
        self,
        samples: List[Dict[str, Any]],
        instruction_field: str = "instruction",
```
