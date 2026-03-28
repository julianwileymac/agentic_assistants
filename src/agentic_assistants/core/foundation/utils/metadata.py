"""
Metadata utility helpers.
"""

from __future__ import annotations

from typing import Any


def merge_metadata(*items: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for item in items:
        for key, value in item.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = merge_metadata(merged[key], value)
            else:
                merged[key] = value
    return merged


def select_metadata(metadata: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    return {key: metadata[key] for key in keys if key in metadata}

