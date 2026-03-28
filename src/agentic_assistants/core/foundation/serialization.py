"""
Pluggable serializer backends for JSON, Pydantic, and msgspec.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _json_default(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


@runtime_checkable
class Serializer(Protocol):
    """Protocol for serializer implementations."""

    def encode(self, obj: Any) -> bytes:
        ...

    def decode(self, data: bytes | str, target_type: Optional[type[T]] = None) -> Any:
        ...


class JsonSerializer:
    """Standard JSON serializer based on the stdlib."""

    def __init__(self, indent: Optional[int] = None, sort_keys: bool = False) -> None:
        self._indent = indent
        self._sort_keys = sort_keys

    def encode(self, obj: Any) -> bytes:
        if isinstance(obj, BaseModel):
            return obj.model_dump_json().encode("utf-8")
        return json.dumps(
            obj,
            indent=self._indent,
            sort_keys=self._sort_keys,
            default=_json_default,
        ).encode("utf-8")

    def decode(self, data: bytes | str, target_type: Optional[type[T]] = None) -> Any:
        raw = data.decode("utf-8") if isinstance(data, bytes) else data
        parsed = json.loads(raw)
        if target_type is not None and issubclass(target_type, BaseModel):
            return target_type.model_validate(parsed)
        return parsed


class PydanticSerializer:
    """Serializer optimized for BaseModel payloads."""

    def encode(self, obj: Any) -> bytes:
        if isinstance(obj, BaseModel):
            return obj.model_dump_json().encode("utf-8")
        return json.dumps(obj, default=_json_default).encode("utf-8")

    def decode(self, data: bytes | str, target_type: Optional[type[T]] = None) -> Any:
        if target_type is not None and issubclass(target_type, BaseModel):
            raw = data if isinstance(data, (bytes, str)) else str(data)
            return target_type.model_validate_json(raw)
        raw = data.decode("utf-8") if isinstance(data, bytes) else data
        return json.loads(raw)


class MsgspecSerializer:
    """High-performance serializer using msgspec when available."""

    def __init__(self) -> None:
        self._available = False
        self._encoder: Any = None
        self._decoder: Any = None
        try:
            import msgspec.json as msgspec_json

            self._encoder = msgspec_json.Encoder()
            self._decoder = msgspec_json.Decoder()
            self._available = True
        except ImportError:
            logger.debug("msgspec not installed; using JSON fallback")

    def encode(self, obj: Any) -> bytes:
        if not self._available:
            return json.dumps(obj, default=_json_default).encode("utf-8")
        if isinstance(obj, BaseModel):
            return self._encoder.encode(obj.model_dump(mode="json"))
        return self._encoder.encode(obj)

    def decode(self, data: bytes | str, target_type: Optional[type[T]] = None) -> Any:
        if not self._available:
            raw = data.decode("utf-8") if isinstance(data, bytes) else data
            parsed = json.loads(raw)
            if target_type is not None and issubclass(target_type, BaseModel):
                return target_type.model_validate(parsed)
            return parsed

        raw = data if isinstance(data, bytes) else data.encode("utf-8")
        if target_type is not None:
            try:
                import msgspec.json as msgspec_json

                return msgspec_json.decode(raw, type=target_type)
            except Exception:
                decoded = self._decoder.decode(raw)
                if issubclass(target_type, BaseModel):
                    return target_type.model_validate(decoded)
                return decoded
        return self._decoder.decode(raw)


_SERIALIZERS: dict[str, type] = {
    "json": JsonSerializer,
    "pydantic": PydanticSerializer,
    "msgspec": MsgspecSerializer,
}


def get_serializer(backend: str = "json", **kwargs: Any) -> Serializer:
    """Factory for serializer instances."""
    serializer_cls = _SERIALIZERS.get(backend)
    if serializer_cls is None:
        raise ValueError(f"Unknown serializer backend: '{backend}'. Available: {sorted(_SERIALIZERS)}")
    return serializer_cls(**kwargs)


def register_serializer(name: str, cls: type) -> None:
    """Register a custom serializer class by name."""
    if not hasattr(cls, "encode") or not hasattr(cls, "decode"):
        raise TypeError("Serializer classes must define `encode` and `decode` methods")
    _SERIALIZERS[name] = cls


__all__ = [
    "Serializer",
    "JsonSerializer",
    "PydanticSerializer",
    "MsgspecSerializer",
    "get_serializer",
    "register_serializer",
]

