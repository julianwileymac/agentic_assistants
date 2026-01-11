# Chunk: de84fdd4c7a7_0

- source: `src/agentic_assistants/training/frameworks/llama_factory.py`
- lines: 1-100
- chunk: 1/8

```
"""
Llama Factory training framework adapter.

This module provides integration with Llama Factory for LLM training.
Llama Factory supports efficient fine-tuning with LoRA, QLoRA, and full fine-tuning.

Reference: https://github.com/hiyouga/LLaMA-Factory
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.training.config import (
    TrainingConfig,
    TrainingMethod,
    LoRAConfig,
    QLoRAConfig,
)
from agentic_assistants.training.frameworks.base import BaseTrainingFramework, TrainingResult
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class LlamaFactoryAdapter(BaseTrainingFramework):
    """
    Adapter for Llama Factory training framework.
    
    Llama Factory provides efficient fine-tuning for LLMs with support for:
    - Full fine-tuning
    - LoRA (Low-Rank Adaptation)
    - QLoRA (Quantized LoRA)
    - RLHF/DPO training
    
    This adapter translates our TrainingConfig into Llama Factory's configuration
    format and manages the training process.
    """
    
    def __init__(self, llama_factory_path: Optional[str] = None):
        """
        Initialize the Llama Factory adapter.
        
        Args:
            llama_factory_path: Path to Llama Factory installation
        """
        self._llama_factory_path = llama_factory_path
        self._version = self._detect_version()
    
    @property
    def name(self) -> str:
        return "llama_factory"
    
    @property
    def version(self) -> str:
        return self._version
    
    def _detect_version(self) -> str:
        """Detect Llama Factory version."""
        try:
            # Try to import and get version
            result = subprocess.run(
                [sys.executable, "-c", "import llamafactory; print(llamafactory.__version__)"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"
    
    def is_available(self) -> bool:
        """Check if Llama Factory is available."""
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import llamafactory"],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def validate_config(self, config: TrainingConfig) -> List[str]:
        """Validate training configuration."""
        errors = []
        
        if not config.base_model:
            errors.append("base_model is required")
        
        if not config.output_name:
```
