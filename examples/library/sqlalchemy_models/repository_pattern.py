# requires: sqlalchemy>=2

"""
Generic repository abstraction over SQLAlchemy 2.0 ``Session``.

Repositories encapsulate persistence rules (how to load, save, delete) so services
and HTTP layers stay focused on business rules. Type parameters preserve the
concrete mapped class across methods without casts.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import create_engine, Integer, String


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)


T = TypeVar("T", bound=Base)


# --- Design notes -----------------------------------------------------------
# Repositories should not own transactions spanning multiple aggregates — use units of work.
# Returning detached instances? Call ``session.expunge`` or pass DTOs instead.
# For complex filters, expose a narrow query method rather than leaking ``Session``.
# ---------------------------------------------------------------------------


class Repository(Generic[T]):
    """Small CRUD helper parameterized by mapped class."""

    def __init__(self, session_factory: sessionmaker, model: type[T]) -> None:
        self._session_factory = session_factory
        self._model = model

    def add(self, instance: T) -> T:
        with self._session_factory() as session:
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    def get(self, pk: Any) -> T | None:
        with self._session_factory() as session:
            return session.get(self._model, pk)

    def list_all(self) -> list[T]:
        with self._session_factory() as session:
            return list(session.scalars(select(self._model)).all())

    def delete(self, instance: T) -> None:
        with self._session_factory() as session:
            session.delete(session.merge(instance))
            session.commit()

    def update(self, pk: Any, **fields: Any) -> T | None:
        with self._session_factory() as session:
            obj = session.get(self._model, pk)
            if obj is None:
                return None
            for key, value in fields.items():
                setattr(obj, key, value)
            session.commit()
            session.refresh(obj)
            return obj


def main() -> None:
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False)
    products = Repository[Product](Session, Product)

    p1 = products.add(Product(name="mug", price_cents=900))
    p2 = products.add(Product(name="notebook", price_cents=450))
    print("created ids:", p1.id, p2.id)
    print("all:", [(p.name, p.price_cents) for p in products.list_all()])
    updated = products.update(p2.id, price_cents=400)
    print("updated price:", updated.price_cents if updated else None)
    products.delete(p1)
    print("after delete:", [p.name for p in products.list_all()])


if __name__ == "__main__":
    main()
