"""
State mutation and projection helpers.
"""

from __future__ import annotations

from typing import Any, Mapping


def deep_merge_state(base: Mapping[str, Any], update: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in update.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge_state(merged[key], value)
        elif key in merged and isinstance(merged[key], list) and isinstance(value, list):
            merged[key] = merged[key] + value
        else:
            merged[key] = value
    return merged


def append_step(state: dict[str, Any], step_name: str) -> dict[str, Any]:
    steps = state.setdefault("__steps__", [])
    steps.append(step_name)
    return state


def project_state(state: Mapping[str, Any], keys: list[str]) -> dict[str, Any]:
    return {key: state[key] for key in keys if key in state}

