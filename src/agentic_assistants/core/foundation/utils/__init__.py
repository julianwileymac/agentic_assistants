"""
Utility helpers for foundation-level state, metadata, and validation handling.
"""

from agentic_assistants.core.foundation.utils.metadata import merge_metadata, select_metadata
from agentic_assistants.core.foundation.utils.serialization_utils import (
    ensure_bytes,
    safe_json_dumps,
    safe_json_loads,
)
from agentic_assistants.core.foundation.utils.state import append_step, deep_merge_state, project_state
from agentic_assistants.core.foundation.utils.validation import ensure_required_keys, ensure_within_range

__all__ = [
    "merge_metadata",
    "select_metadata",
    "safe_json_dumps",
    "safe_json_loads",
    "ensure_bytes",
    "deep_merge_state",
    "append_step",
    "project_state",
    "ensure_required_keys",
    "ensure_within_range",
]

