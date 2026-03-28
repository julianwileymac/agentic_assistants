"""
Service-layer abstractions with lifecycle hooks and optional domain events.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Generic, Optional, Protocol, Sequence, TypeVar

from pydantic import BaseModel, Field

from agentic_assistants.core.foundation.base_models import AgenticBaseModel
from agentic_assistants.core.foundation.repository import (
    AbstractRepository,
    FilterSpec,
    PaginationSpec,
    SortSpec,
)

logger = logging.getLogger(__name__)

ModelT = TypeVar("ModelT", bound=BaseModel)


class DomainEvent(AgenticBaseModel):
    """Structured event emitted by services during lifecycle transitions."""

    event_type: str
    entity_type: str
    entity_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)


class EventPublisher(Protocol):
    """Protocol for event publishers/buses."""

    async def publish(self, event: DomainEvent) -> None:
        ...


class BaseService(Generic[ModelT]):
    """Service layer that wraps a repository with lifecycle hooks."""

    def __init__(
        self,
        repository: AbstractRepository[ModelT, Any],
        *,
        event_publisher: Optional[EventPublisher] = None,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    async def before_create(self, data: ModelT) -> ModelT:
        return data

    async def after_create(self, data: ModelT) -> None:
        return None

    async def before_update(self, id: Any, data: dict[str, Any]) -> dict[str, Any]:
        return data

    async def after_update(self, item: ModelT) -> None:
        return None

    async def before_delete(self, id: Any) -> None:
        return None

    async def after_delete(self, id: Any) -> None:
        return None

    async def before_upsert(self, data: ModelT) -> ModelT:
        return data

    async def after_upsert(self, data: ModelT) -> None:
        return None

    async def emit_event(
        self,
        *,
        event_type: str,
        entity_type: str,
        entity_id: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> None:
        if self.event_publisher is None:
            return
        await self.event_publisher.publish(
            DomainEvent(
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                payload=payload or {},
            )
        )

    async def create(self, data: ModelT) -> ModelT:
        processed = await self.before_create(data)
        result = await self.repository.create(processed)
        await self.after_create(result)
        entity_id = str(getattr(result, "id", ""))
        await self.emit_event(
            event_type="created",
            entity_type=type(result).__name__,
            entity_id=entity_id,
            payload={"source": "service.create"},
        )
        logger.debug("Created %s", type(result).__name__)
        return result

    async def create_many(self, data: Sequence[ModelT]) -> list[ModelT]:
        processed = [await self.before_create(item) for item in data]
        results = await self.repository.create_many(processed)
        for item in results:
            await self.after_create(item)
            await self.emit_event(
                event_type="created",
                entity_type=type(item).__name__,
                entity_id=str(getattr(item, "id", "")),
                payload={"source": "service.create_many"},
            )
        return results

    async def get(self, id: Any) -> Optional[ModelT]:
        return await self.repository.get(id)

    async def get_one(self, id: Any) -> ModelT:
        return await self.repository.get_one(id)

    async def get_by_field(self, field: str, value: Any) -> Optional[ModelT]:
        return await self.repository.get_by_field(field, value)

    async def list(
        self,
        filters: Optional[list[FilterSpec]] = None,
        sort: Optional[list[SortSpec]] = None,
        pagination: Optional[PaginationSpec] = None,
    ) -> list[ModelT]:
        return await self.repository.list(filters=filters, sort=sort, pagination=pagination)

    async def update(self, id: Any, data: dict[str, Any]) -> Optional[ModelT]:
        payload = await self.before_update(id, data)
        result = await self.repository.update(id, payload)
        if result is not None:
            await self.after_update(result)
            await self.emit_event(
                event_type="updated",
                entity_type=type(result).__name__,
                entity_id=str(getattr(result, "id", id)),
                payload={"source": "service.update"},
            )
        return result

    async def upsert(self, data: ModelT) -> ModelT:
        payload = await self.before_upsert(data)
        result = await self.repository.upsert(payload)
        await self.after_upsert(result)
        await self.emit_event(
            event_type="upserted",
            entity_type=type(result).__name__,
            entity_id=str(getattr(result, "id", "")),
            payload={"source": "service.upsert"},
        )
        return result

    async def delete(self, id: Any) -> bool:
        await self.before_delete(id)
        success = await self.repository.delete(id)
        if success:
            await self.after_delete(id)
            await self.emit_event(
                event_type="deleted",
                entity_type=self.repository.model_type.__name__,
                entity_id=str(id),
                payload={"source": "service.delete"},
            )
        return success

    async def delete_many(self, ids: Sequence[Any]) -> int:
        for id_val in ids:
            await self.before_delete(id_val)
        count = await self.repository.delete_many(ids)
        for id_val in ids:
            await self.after_delete(id_val)
        return count

    async def count(self, filters: Optional[list[FilterSpec]] = None) -> int:
        return await self.repository.count(filters=filters)

    async def exists(self, id: Any) -> bool:
        return await self.repository.exists(id)


class AuditedService(BaseService[ModelT]):
    """Service that stamps audit fields on create/update using current user."""

    def __init__(
        self,
        repository: AbstractRepository[ModelT, Any],
        *,
        current_user: Optional[str] = None,
        event_publisher: Optional[EventPublisher] = None,
    ) -> None:
        super().__init__(repository, event_publisher=event_publisher)
        self.current_user = current_user

    async def before_create(self, data: ModelT) -> ModelT:
        if self.current_user and hasattr(data, "created_by"):
            data = data.model_copy(update={"created_by": self.current_user})
        return data

    async def before_update(self, id: Any, data: dict[str, Any]) -> dict[str, Any]:
        if self.current_user:
            updated = dict(data)
            updated["updated_by"] = self.current_user
            return updated
        return data


__all__ = [
    "DomainEvent",
    "BaseService",
    "AuditedService",
]

