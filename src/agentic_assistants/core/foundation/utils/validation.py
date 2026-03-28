"""
Small validation helper functions for runtime guardrails.
"""

from __future__ import annotations

from typing import Any, Mapping


def ensure_required_keys(payload: Mapping[str, Any], required_keys: list[str]) -> None:
    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise ValueError(f"Missing required keys: {missing}")


def ensure_within_range(value: float, *, min_value: float, max_value: float, name: str) -> None:
    if value < min_value or value > max_value:
        raise ValueError(f"{name} must be in range [{min_value}, {max_value}], got {value}")

