"""
Data manipulation utilities for RAG, ETL, and general data processing.
"""

from __future__ import annotations

import json
import logging
import math
from typing import Any, Optional

logger = logging.getLogger(__name__)


def chunk_text(
    text: str,
    max_tokens: int = 512,
    overlap: int = 50,
    token_estimate_ratio: float = 4.0,
) -> list[str]:
    """Split text into overlapping chunks.

    Args:
        text: Input text.
        max_tokens: Approximate maximum tokens per chunk.
        overlap: Overlap in estimated tokens between consecutive chunks.
        token_estimate_ratio: Average characters per token (4 for English).

    Returns:
        List of text chunks.
    """
    max_chars = int(max_tokens * token_estimate_ratio)
    overlap_chars = int(overlap * token_estimate_ratio)

    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]

        if end < len(text):
            last_period = chunk.rfind(".")
            last_newline = chunk.rfind("\n")
            break_point = max(last_period, last_newline)
            if break_point > max_chars // 2:
                chunk = chunk[: break_point + 1]
                end = start + break_point + 1

        chunks.append(chunk.strip())
        start = end - overlap_chars

    return [c for c in chunks if c]


def merge_dicts_deep(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries. Override wins on conflicts."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts_deep(result[key], value)
        else:
            result[key] = value
    return result


def flatten_dict(
    d: dict[str, Any],
    separator: str = ".",
    prefix: str = "",
) -> dict[str, Any]:
    """Flatten a nested dictionary.

    >>> flatten_dict({"a": {"b": 1, "c": {"d": 2}}})
    {"a.b": 1, "a.c.d": 2}
    """
    items: dict[str, Any] = {}
    for key, value in d.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        if isinstance(value, dict):
            items.update(flatten_dict(value, separator, new_key))
        else:
            items[new_key] = value
    return items


def unflatten_dict(
    d: dict[str, Any],
    separator: str = ".",
) -> dict[str, Any]:
    """Unflatten a flat dictionary back into nested form."""
    result: dict[str, Any] = {}
    for key, value in d.items():
        parts = key.split(separator)
        current = result
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value
    return result


def safe_json_loads(s: str | bytes, default: Any = None) -> Any:
    """Parse JSON without raising, returning default on failure."""
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, **kwargs: Any) -> str:
    """Serialize to JSON, falling back to str() for non-serializable objects."""
    try:
        return json.dumps(obj, default=str, **kwargs)
    except (TypeError, ValueError):
        return str(obj)


def dataframe_to_documents(
    df: Any,
    content_column: str,
    metadata_columns: Optional[list[str]] = None,
    id_column: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Convert a pandas/polars DataFrame to a list of document dicts.

    Each row becomes a document with "content", "metadata", and optional "id".
    """
    documents = []
    metadata_columns = metadata_columns or []

    try:
        if hasattr(df, "to_pandas"):
            df = df.to_pandas()

        for _, row in df.iterrows():
            doc: dict[str, Any] = {
                "content": str(row[content_column]),
                "metadata": {col: row[col] for col in metadata_columns if col in row.index},
            }
            if id_column and id_column in row.index:
                doc["id"] = str(row[id_column])
            documents.append(doc)
    except Exception as e:
        logger.error("Failed to convert dataframe to documents: %s", e)

    return documents


def estimate_tokens(text: str, chars_per_token: float = 4.0) -> int:
    """Estimate token count from character length."""
    return math.ceil(len(text) / chars_per_token)


def truncate_text(text: str, max_tokens: int = 4096, suffix: str = "...") -> str:
    """Truncate text to approximate token limit."""
    max_chars = int(max_tokens * 4.0)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(suffix)] + suffix


__all__ = [
    "chunk_text",
    "merge_dicts_deep",
    "flatten_dict",
    "unflatten_dict",
    "safe_json_loads",
    "safe_json_dumps",
    "dataframe_to_documents",
    "estimate_tokens",
    "truncate_text",
]
