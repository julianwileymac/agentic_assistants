"""
Reusable Pydantic validators and custom Annotated types.

Provides pre-built validation functions and constrained types that can be
used across models via ``Annotated[str, ...]`` patterns.
"""

from __future__ import annotations

import json
import re
from typing import Annotated, Any

from pydantic import AfterValidator, BeforeValidator, Field
from pydantic.functional_validators import PlainValidator


def _validate_non_empty_str(v: str) -> str:
    if not v or not v.strip():
        raise ValueError("String must not be empty or whitespace-only")
    return v.strip()


def _validate_url(v: str) -> str:
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    if not re.match(pattern, v, re.IGNORECASE):
        raise ValueError(f"Invalid URL: {v}")
    return v


def _validate_json_string(v: str) -> str:
    try:
        json.loads(v)
    except (json.JSONDecodeError, TypeError):
        raise ValueError("String must be valid JSON")
    return v


def _validate_semver(v: str) -> str:
    pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$"
    if not re.match(pattern, v):
        raise ValueError(f"Invalid semver: {v}")
    return v


def _validate_slug(v: str) -> str:
    pattern = r"^[a-z0-9]+(-[a-z0-9]+)*$"
    if not re.match(pattern, v):
        raise ValueError(f"Invalid slug: {v}. Use lowercase letters, numbers, and hyphens.")
    return v


def _validate_cron_expression(v: str) -> str:
    parts = v.strip().split()
    if len(parts) not in (5, 6):
        raise ValueError(f"Invalid cron expression: expected 5-6 fields, got {len(parts)}")
    return v


def _coerce_to_str(v: Any) -> str:
    if isinstance(v, (int, float)):
        return str(v)
    if not isinstance(v, str):
        raise ValueError(f"Expected string, got {type(v).__name__}")
    return v


NonEmptyStr = Annotated[str, AfterValidator(_validate_non_empty_str)]

HttpUrl = Annotated[str, AfterValidator(_validate_url)]

JsonStr = Annotated[str, AfterValidator(_validate_json_string)]

SemVer = Annotated[str, AfterValidator(_validate_semver)]

Slug = Annotated[str, AfterValidator(_validate_slug)]

CronExpression = Annotated[str, AfterValidator(_validate_cron_expression)]

CoercedStr = Annotated[str, BeforeValidator(_coerce_to_str)]

PositiveFloat = Annotated[float, Field(gt=0)]

NonNegativeFloat = Annotated[float, Field(ge=0)]

PositiveInt = Annotated[int, Field(gt=0)]

NonNegativeInt = Annotated[int, Field(ge=0)]

Percentage = Annotated[float, Field(ge=0.0, le=100.0)]

UnitFloat = Annotated[float, Field(ge=0.0, le=1.0)]

FilePathStr = Annotated[str, AfterValidator(_validate_non_empty_str)]


__all__ = [
    "NonEmptyStr",
    "HttpUrl",
    "JsonStr",
    "SemVer",
    "Slug",
    "CronExpression",
    "CoercedStr",
    "PositiveFloat",
    "NonNegativeFloat",
    "PositiveInt",
    "NonNegativeInt",
    "Percentage",
    "UnitFloat",
    "FilePathStr",
]
