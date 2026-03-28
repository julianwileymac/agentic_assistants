"""
Repository contracts and default implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable, Generic, Hashable, Literal, Optional, Sequence, TypeVar

from pydantic import BaseModel

from agentic_assistants.core.foundation.base_models import AgenticBaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)
IDT = TypeVar("IDT", bound=Hashable)
FilterOperator = Literal[
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "contains",
    "icontains",
    "startswith",
    "endswith",
    "isnull",
]


class FilterSpec(AgenticBaseModel):
    """Declarative filter specification for repository queries."""

    field: str
    op: FilterOperator = "eq"
    value: Any = None


class SortSpec(AgenticBaseModel):
    """Sort specification."""

    field: str
    descending: bool = False


class PaginationSpec(AgenticBaseModel):
    """Pagination parameters."""

    page: int = 1
    page_size: int = 50

    @property
    def offset(self) -> int:
        return max(0, (self.page - 1) * self.page_size)


class AbstractRepository(ABC, Generic[ModelT, IDT]):
    """Abstract async repository with CRUD + query operations."""

    model_type: type[ModelT]
    id_field: str

    @abstractmethod
    async def create(self, data: ModelT) -> ModelT:
        ...

    @abstractmethod
    async def create_many(self, data: Sequence[ModelT]) -> list[ModelT]:
        ...

    @abstractmethod
    async def get(self, id: IDT) -> Optional[ModelT]:
        ...

    async def get_one(self, id: IDT) -> ModelT:
        result = await self.get(id)
        if result is None:
            raise LookupError(f"{self.model_type.__name__} with {self.id_field}={id!r} not found")
        return result

    @abstractmethod
    async def get_by_field(self, field: str, value: Any) -> Optional[ModelT]:
        ...

    @abstractmethod
    async def list(
        self,
        filters: Optional[list[FilterSpec]] = None,
        sort: Optional[list[SortSpec]] = None,
        pagination: Optional[PaginationSpec] = None,
    ) -> list[ModelT]:
        ...

    @abstractmethod
    async def update(self, id: IDT, data: dict[str, Any]) -> Optional[ModelT]:
        ...

    @abstractmethod
    async def update_many(self, items: Sequence[tuple[IDT, dict[str, Any]]]) -> list[ModelT]:
        ...

    @abstractmethod
    async def upsert(self, data: ModelT) -> ModelT:
        ...

    @abstractmethod
    async def delete(self, id: IDT) -> bool:
        ...

    @abstractmethod
    async def delete_many(self, ids: Sequence[IDT]) -> int:
        ...

    @abstractmethod
    async def count(self, filters: Optional[list[FilterSpec]] = None) -> int:
        ...

    @abstractmethod
    async def exists(self, id: IDT) -> bool:
        ...


class InMemoryRepository(AbstractRepository[ModelT, IDT]):
    """In-memory repository for tests and lightweight workflows."""

    def __init__(
        self,
        model_type: type[ModelT],
        *,
        id_field: str = "id",
        id_getter: Optional[Callable[[ModelT], IDT]] = None,
    ) -> None:
        self.model_type = model_type
        self.id_field = id_field
        self._id_getter = id_getter
        self._store: dict[IDT, ModelT] = {}

    def _get_id(self, item: ModelT) -> IDT:
        if self._id_getter is not None:
            return self._id_getter(item)
        id_value = getattr(item, self.id_field, None)
        if id_value is None:
            raise ValueError(f"Model must define '{self.id_field}'")
        return id_value

    @staticmethod
    def _touch_updated_at(item: ModelT, update: dict[str, Any]) -> dict[str, Any]:
        if hasattr(item, "updated_at") and "updated_at" not in update:
            update = dict(update)
            update["updated_at"] = datetime.now(timezone.utc)
        return update

    async def create(self, data: ModelT) -> ModelT:
        id_val = self._get_id(data)
        self._store[id_val] = data
        return data

    async def create_many(self, data: Sequence[ModelT]) -> list[ModelT]:
        return [await self.create(item) for item in data]

    async def get(self, id: IDT) -> Optional[ModelT]:
        return self._store.get(id)

    async def get_by_field(self, field: str, value: Any) -> Optional[ModelT]:
        for item in self._store.values():
            if getattr(item, field, None) == value:
                return item
        return None

    def _apply_filter(self, item: ModelT, spec: FilterSpec) -> bool:
        current = getattr(item, spec.field, None)
        op = spec.op
        expected = spec.value
        if op == "eq":
            return current == expected
        if op == "ne":
            return current != expected
        if op == "gt":
            return current > expected
        if op == "gte":
            return current >= expected
        if op == "lt":
            return current < expected
        if op == "lte":
            return current <= expected
        if op == "in":
            return current in expected
        if op == "contains":
            return str(expected) in str(current)
        if op == "icontains":
            return str(expected).lower() in str(current).lower()
        if op == "startswith":
            return str(current).startswith(str(expected))
        if op == "endswith":
            return str(current).endswith(str(expected))
        if op == "isnull":
            should_be_null = bool(expected)
            return (current is None) if should_be_null else (current is not None)
        return False

    async def list(
        self,
        filters: Optional[list[FilterSpec]] = None,
        sort: Optional[list[SortSpec]] = None,
        pagination: Optional[PaginationSpec] = None,
    ) -> list[ModelT]:
        items = list(self._store.values())
        if filters:
            for spec in filters:
                items = [item for item in items if self._apply_filter(item, spec)]
        if sort:
            for spec in reversed(sort):
                items.sort(
                    key=lambda row: getattr(row, spec.field, None),
                    reverse=spec.descending,
                )
        if pagination:
            items = items[pagination.offset : pagination.offset + pagination.page_size]
        return items

    async def update(self, id: IDT, data: dict[str, Any]) -> Optional[ModelT]:
        current = self._store.get(id)
        if current is None:
            return None
        update_payload = self._touch_updated_at(current, data)
        updated = current.model_copy(update=update_payload)
        self._store[id] = updated
        return updated

    async def update_many(self, items: Sequence[tuple[IDT, dict[str, Any]]]) -> list[ModelT]:
        updated: list[ModelT] = []
        for id_val, payload in items:
            item = await self.update(id_val, payload)
            if item is not None:
                updated.append(item)
        return updated

    async def upsert(self, data: ModelT) -> ModelT:
        id_val = self._get_id(data)
        self._store[id_val] = data
        return data

    async def delete(self, id: IDT) -> bool:
        return self._store.pop(id, None) is not None

    async def delete_many(self, ids: Sequence[IDT]) -> int:
        deleted = 0
        for id_val in ids:
            if await self.delete(id_val):
                deleted += 1
        return deleted

    async def count(self, filters: Optional[list[FilterSpec]] = None) -> int:
        return len(await self.list(filters=filters))

    async def exists(self, id: IDT) -> bool:
        return id in self._store


class SQLAlchemyRepository(AbstractRepository[ModelT, IDT]):
    """Repository backed by SQLAlchemy async sessions."""

    def __init__(
        self,
        model_type: type[ModelT],
        session_factory: Callable[[], Any],
        *,
        id_field: str = "id",
        table: Any = None,
        table_resolver: Optional[Callable[[type[ModelT]], Any]] = None,
    ) -> None:
        self.model_type = model_type
        self.id_field = id_field
        self._session_factory = session_factory
        self._table = table
        self._table_resolver = table_resolver

    def _resolve_table(self) -> Any:
        if self._table is not None:
            return self._table
        if self._table_resolver is not None:
            self._table = self._table_resolver(self.model_type)
            return self._table
        table = getattr(self.model_type, "__table__", None)
        if table is not None:
            self._table = table
            return table
        raise RuntimeError(
            "SQLAlchemyRepository requires `table`, `table_resolver`, "
            "or model.__table__ to be defined."
        )

    def _apply_filter_clause(self, stmt: Any, table: Any, spec: FilterSpec) -> Any:
        col = getattr(table.c, spec.field)
        op = spec.op
        value = spec.value
        if op == "eq":
            return stmt.where(col == value)
        if op == "ne":
            return stmt.where(col != value)
        if op == "gt":
            return stmt.where(col > value)
        if op == "gte":
            return stmt.where(col >= value)
        if op == "lt":
            return stmt.where(col < value)
        if op == "lte":
            return stmt.where(col <= value)
        if op == "in":
            return stmt.where(col.in_(value))
        if op == "contains":
            return stmt.where(col.contains(value))
        if op == "icontains":
            return stmt.where(col.ilike(f"%{value}%"))
        if op == "startswith":
            return stmt.where(col.startswith(value))
        if op == "endswith":
            return stmt.where(col.endswith(value))
        if op == "isnull":
            return stmt.where(col.is_(None) if value else col.is_not(None))
        return stmt

    async def create(self, data: ModelT) -> ModelT:
        try:
            from sqlalchemy import insert
        except ImportError as exc:
            raise ImportError("sqlalchemy is required for SQLAlchemyRepository") from exc
        table = self._resolve_table()
        payload = data.model_dump(mode="python")
        async with self._session_factory() as session:
            await session.execute(insert(table).values(**payload))
            await session.commit()
        return data

    async def create_many(self, data: Sequence[ModelT]) -> list[ModelT]:
        try:
            from sqlalchemy import insert
        except ImportError as exc:
            raise ImportError("sqlalchemy is required for SQLAlchemyRepository") from exc
        table = self._resolve_table()
        rows = [item.model_dump(mode="python") for item in data]
        async with self._session_factory() as session:
            await session.execute(insert(table), rows)
            await session.commit()
        return list(data)

    async def get(self, id: IDT) -> Optional[ModelT]:
        try:
            from sqlalchemy import select
        except ImportError as exc:
            raise ImportError("sqlalchemy is required for SQLAlchemyRepository") from exc
        table = self._resolve_table()
        col = getattr(table.c, self.id_field)
        async with self._session_factory() as session:
            result = await session.execute(select(table).where(col == id))
            row = result.mappings().first()
        if row is None:
            return None
        return self.model_type.model_validate(dict(row))

    async def get_by_field(self, field: str, value: Any) -> Optional[ModelT]:
        try:
            from sqlalchemy import select
        except ImportError as exc:
            raise ImportError("sqlalchemy is required for SQLAlchemyRepository") from exc
        table = self._resolve_table()
        col = getattr(table.c, field)
        async with self._session_factory() as session:
            result = await session.execute(select(table).where(col == value))
            row = result.mappings().first()
        if row is None:
            return None
        return self.model_type.model_validate(dict(row))

    async def list(
        self,
        filters: Optional[list[FilterSpec]] = None,
        sort: Optional[list[SortSpec]] = None,
        pagination: Optional[PaginationSpec] = None,
    ) -> list[ModelT]:
        try:
            from sqlalchemy import select
        except ImportError as exc:
            raise ImportError("sqlalchemy is required for SQLAlchemyRepository") from exc
        table = self._resolve_table()
        stmt = select(table)
        if filters:
            for spec in filters:
                stmt = self._apply_filter_clause(stmt, table, spec)
        if sort:
            for spec in sort:
                col = getattr(table.c, spec.field)
                stmt = stmt.order_by(col.desc() if spec.descending else col.asc())
        if pagination:
            stmt = stmt.offset(pagination.offset).limit(pagination.page_size)
        async with self._session_factory() as session:
            result = await session.execute(stmt)
            rows = result.mappings().all()
        return [self.model_type.model_validate(dict(row)) for row in rows]

    async def update(self, id: IDT, data: dict[str, Any]) -> Optional[ModelT]:
        try:
            from sqlalchemy import update
        except ImportError as exc:
            raise ImportError("sqlalchemy is required for SQLAlchemyRepository") from exc
        table = self._resolve_table()
        payload = dict(data)
        if "updated_at" in table.c and "updated_at" not in payload:
            payload["updated_at"] = datetime.now(timezone.utc)
        col = getattr(table.c, self.id_field)
        async with self._session_factory() as session:
            await session.execute(update(table).where(col == id).values(**payload))
            await session.commit()
        return await self.get(id)

    async def update_many(self, items: Sequence[tuple[IDT, dict[str, Any]]]) -> list[ModelT]:
        updated: list[ModelT] = []
        for id_val, payload in items:
            row = await self.update(id_val, payload)
            if row is not None:
                updated.append(row)
        return updated

    async def upsert(self, data: ModelT) -> ModelT:
        id_value = getattr(data, self.id_field)
        if await self.exists(id_value):
            payload = data.model_dump(mode="python", exclude={self.id_field})
            await self.update(id_value, payload)
            return data
        return await self.create(data)

    async def delete(self, id: IDT) -> bool:
        try:
            from sqlalchemy import delete
        except ImportError as exc:
            raise ImportError("sqlalchemy is required for SQLAlchemyRepository") from exc
        table = self._resolve_table()
        col = getattr(table.c, self.id_field)
        async with self._session_factory() as session:
            result = await session.execute(delete(table).where(col == id))
            await session.commit()
        return bool(getattr(result, "rowcount", 0))

    async def delete_many(self, ids: Sequence[IDT]) -> int:
        deleted = 0
        for id_val in ids:
            if await self.delete(id_val):
                deleted += 1
        return deleted

    async def count(self, filters: Optional[list[FilterSpec]] = None) -> int:
        try:
            from sqlalchemy import func, select
        except ImportError as exc:
            raise ImportError("sqlalchemy is required for SQLAlchemyRepository") from exc
        table = self._resolve_table()
        stmt = select(func.count()).select_from(table)
        if filters:
            for spec in filters:
                stmt = self._apply_filter_clause(stmt, table, spec)
        async with self._session_factory() as session:
            result = await session.execute(stmt)
            return int(result.scalar() or 0)

    async def exists(self, id: IDT) -> bool:
        return await self.get(id) is not None


__all__ = [
    "AbstractRepository",
    "FilterSpec",
    "SortSpec",
    "PaginationSpec",
    "InMemoryRepository",
    "SQLAlchemyRepository",
]

