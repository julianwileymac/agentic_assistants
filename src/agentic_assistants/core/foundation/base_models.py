"""
Flexible base models and mixins for domain entities and API boundaries.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, Optional, Self, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

T = TypeVar("T")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AgenticBaseModel(BaseModel):
    """Root base model with shared serialization and validation behavior."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        ser_json_timedelta="iso8601",
        validate_default=True,
    )

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        return self.model_dump(**kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls.model_validate(data)

    def to_json(self, **kwargs: Any) -> str:
        return self.model_dump_json(**kwargs)

    @classmethod
    def from_json(cls, raw: str | bytes) -> Self:
        return cls.model_validate_json(raw)


class TimestampMixin(BaseModel):
    """Adds created_at / updated_at fields with UTC defaults."""

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def _set_updated_at_on_update(cls, values: Any) -> Any:
        if isinstance(values, dict) and values.get("id") is not None:
            values.setdefault("updated_at", _utcnow())
        return values


class UUIDMixin(BaseModel):
    """Adds UUIDv4 id."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)


class SlugMixin(BaseModel):
    """Adds a human-readable slug identifier."""

    slug: str = Field(default="", max_length=256)


class SoftDeleteMixin(BaseModel):
    """Marks records as logically deleted."""

    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None


class AuditMixin(TimestampMixin):
    """Adds user-level audit fields."""

    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class TagsMixin(BaseModel):
    """Adds a list of tags for indexing and filtering."""

    tags: list[str] = Field(default_factory=list)


class MetadataMixin(BaseModel):
    """Adds free-form metadata with alias compatibility."""

    metadata: dict[str, Any] = Field(default_factory=dict, alias="extra_metadata")


class AgenticEntity(UUIDMixin, TimestampMixin, AgenticBaseModel):
    """Default entity base (id + timestamps + serialization helpers)."""


class AgenticAuditEntity(UUIDMixin, AuditMixin, AgenticBaseModel):
    """Entity base with audit trail fields."""


class AgenticSlugEntity(UUIDMixin, SlugMixin, TimestampMixin, AgenticBaseModel):
    """Entity base with slug support."""


class VersionedMixin(BaseModel):
    """Tracks model version for optimistic concurrency."""

    version: int = Field(default=1, ge=1)

    def bump_version(self) -> int:
        self.version = self.version + 1
        return self.version


class EntityStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StatusMixin(BaseModel):
    """Adds a generalized status field."""

    status: str = Field(default=EntityStatus.ACTIVE.value)


class ErrorDetail(AgenticBaseModel):
    """Structured error details for API and runtime boundaries."""

    message: str
    code: Optional[str] = None
    field: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)


class PaginatedResponse(AgenticBaseModel, Generic[T]):
    """Generic paginated response container."""

    items: list[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 50
    page_count: int = 1
    has_next: bool = False
    has_prev: bool = False

    @model_validator(mode="after")
    def _compute_flags(self) -> Self:
        safe_page_size = max(1, self.page_size)
        page_count = max(1, (self.total + safe_page_size - 1) // safe_page_size)
        object.__setattr__(self, "page_count", page_count)
        object.__setattr__(self, "has_next", self.page < page_count)
        object.__setattr__(self, "has_prev", self.page > 1)
        return self


class Envelope(AgenticBaseModel, Generic[T]):
    """Generic response envelope with optional data and errors."""

    data: Optional[T] = None
    errors: list[ErrorDetail] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


class ErrorResponse(AgenticBaseModel):
    """Compatibility error payload used in API and CLI paths."""

    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    field: Optional[str] = None
    errors: list[ErrorDetail] = Field(default_factory=list)


class HealthCheck(AgenticBaseModel):
    """Standard health-check response model."""

    status: str = "ok"
    version: str = ""
    uptime_seconds: float = 0.0
    components: dict[str, str] = Field(default_factory=dict)


__all__ = [
    "AgenticBaseModel",
    "TimestampMixin",
    "UUIDMixin",
    "SlugMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    "TagsMixin",
    "MetadataMixin",
    "AgenticEntity",
    "AgenticAuditEntity",
    "AgenticSlugEntity",
    "VersionedMixin",
    "StatusMixin",
    "EntityStatus",
    "ErrorDetail",
    "PaginatedResponse",
    "Envelope",
    "ErrorResponse",
    "HealthCheck",
]

