"""
RL framework adapters.

This module provides adapters for various RL frameworks:
- TRL (Transformers Reinforcement Learning) - HuggingFace native
- Ray RLlib - Distributed RL (optional)
"""

from agentic_assistants.rl.adapters.base import BaseRLAdapter, RLTrainingResult
from agentic_assistants.rl.adapters.trl_adapter import TRLAdapter

__all__ = [
    "BaseRLAdapter",
    "RLTrainingResult",
    "TRLAdapter",
]
