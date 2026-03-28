# requires: sqlalchemy>=2

"""
Composable ORM mixins: UUID primary keys, auditing, soft delete, and slugs.

Mixins are plain classes that contribute columns or helpers to declarative models
through multiple inheritance. Keep them cohesive (one concern per mixin) and put
shared ``Base`` metadata last in the MRO so SQLAlchemy picks up ``__tablename__``
and mapper configuration from the concrete model.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, String, Uuid, create_engine, event, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.orm import sessionmaker


class Base(DeclarativeBase):
    """Shared registry for all concrete models below."""


class UUIDMixin:
    """UUID primary key stored as string-friendly UUID type (SQLite-friendly)."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class AuditMixin:
    """Automatically stamped timestamps; hook ensures ``updated_at`` changes."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class SoftDeleteMixin:
    """Hide rows instead of physical deletes — filter in queries as needed."""

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)


class SlugMixin:
    """Human-readable unique slug for URLs (filled by app logic or ORM events)."""

    slug: Mapped[str | None] = mapped_column(String(160), unique=True, index=True, default=None)


class Article(UUIDMixin, AuditMixin, SoftDeleteMixin, SlugMixin, Base):
    """Demonstrates multiple inheritance composition of cross-cutting concerns."""

    __tablename__ = "articles"

    title: Mapped[str] = mapped_column(String(200))


# --- Design notes -----------------------------------------------------------
# Listeners are powerful but easy to overuse — prefer explicit service functions when possible.
# Soft deletes need query filters everywhere; consider database views for reporting.
# UUIDs as PKs simplify sharded systems but widen indexes versus integers.
# ---------------------------------------------------------------------------


@event.listens_for(Article, "before_insert", propagate=True)
def _ensure_slug(mapper: Any, connection: Any, target: Article) -> None:
    if not target.slug:
        target.slug = target.title.lower().replace(" ", "-")[:120]


def main() -> None:
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False)

    with Session() as session:
        art = Article(title="Mixins In Practice")
        session.add(art)
        session.commit()
        session.refresh(art)
        print("slug:", art.slug)
        art.deleted_at = datetime.now(UTC)
        session.commit()

    with Session() as session:
        visible = session.scalars(select(Article).where(Article.deleted_at.is_(None))).all()
        print("visible count (soft-deleted hidden in this query):", len(visible))


if __name__ == "__main__":
    main()
