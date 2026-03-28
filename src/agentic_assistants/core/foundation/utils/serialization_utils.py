"""
Serialization helper functions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel


def _default(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def safe_json_dumps(value: Any, *, indent: int | None = None) -> str:
    return json.dumps(value, default=_default, indent=indent)


def safe_json_loads(raw: str | bytes) -> Any:
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    return json.loads(raw)


def ensure_bytes(value: Any) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    return safe_json_dumps(value).encode("utf-8")

