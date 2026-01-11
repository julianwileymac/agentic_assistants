# Chunk: 42d9bcef09ee_0

- source: `src/agentic_assistants/rl/adapters/trl_adapter.py`
- lines: 1-105
- chunk: 1/8

```
"""
TRL (Transformers Reinforcement Learning) adapter.

This adapter integrates with HuggingFace's TRL library for RLHF and DPO training.

Reference: https://github.com/huggingface/trl
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.rl.adapters.base import BaseRLAdapter, RLTrainingResult
from agentic_assistants.rl.config import RLConfig, RLMethod, DPOConfig, PPOConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class TRLAdapter(BaseRLAdapter):
    """
    Adapter for TRL (Transformers Reinforcement Learning).
    
    Supports:
    - DPO (Direct Preference Optimization)
    - PPO with reward models
    - Reward model training
    - ORPO and KTO (newer methods)
    """
    
    def __init__(self):
        """Initialize the TRL adapter."""
        self._version = self._detect_version()
    
    @property
    def name(self) -> str:
        return "trl"
    
    @property
    def supported_methods(self) -> List[RLMethod]:
        return [
            RLMethod.DPO,
            RLMethod.PPO,
            RLMethod.REWARD_MODEL,
            RLMethod.RLHF,
            RLMethod.ORPO,
            RLMethod.KTO,
        ]
    
    def _detect_version(self) -> str:
        """Detect TRL version."""
        try:
            import trl
            return trl.__version__
        except ImportError:
            return "not_installed"
        except Exception:
            return "unknown"
    
    def is_available(self) -> bool:
        """Check if TRL is available."""
        try:
            import trl
            return True
        except ImportError:
            return False
    
    async def train_dpo(
        self,
        config: RLConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """
        Train using Direct Preference Optimization.
        
        DPO directly optimizes the policy to prefer chosen over rejected responses
        without needing an explicit reward model.
        """
        if not self.is_available():
            return RLTrainingResult(
                success=False,
                error="TRL not installed. Install with: pip install trl",
            )
        
        errors = self.validate_config(config)
        if errors:
            return RLTrainingResult(
                success=False,
                error=f"Configuration errors: {', '.join(errors)}",
            )
        
        start_time = time.time()
        
        try:
            # Import TRL components
            from trl import DPOTrainer, DPOConfig as TRLDPOConfig
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from datasets import load_dataset
            
            import torch
            
```
