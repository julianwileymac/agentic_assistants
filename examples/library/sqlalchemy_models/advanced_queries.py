# requires: sqlalchemy>=2

"""
CTEs, window functions, ``hybrid_property``, custom types, and bulk APIs.

Common Table Expressions (``cte()``) clarify multi-step SQL without string
concatenation. Window functions answer ranking questions in-database.
``hybrid_property`` lets one Python attribute map to both instance-level logic
and SQL expressions. ``TypeDecorator`` keeps odd persistence formats out of
domain code.
"""

from __future__ import annotations

from typing import Any, cast

from sqlalchemy import Integer, String, func, insert, select, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.types import String as SAString, TypeDecorator
from sqlalchemy import create_engine


class Base(DeclarativeBase):
    pass


class UpperString(TypeDecorator[str]):
    """Persist uppercase text while exposing Python ``str``."""

    impl = SAString(64)
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect: Any) -> str | None:
        return value.upper() if value is not None else None

    def process_result_value(self, value: str | None, dialect: Any) -> str | None:
        return value


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    region: Mapped[str] = mapped_column(UpperString)
    amount: Mapped[int] = mapped_column(Integer)

    @hybrid_property
    def amount_k(self) -> float:
        """Python-side convenience (rows loaded as ORM objects)."""
        return self.amount / 1000.0

    @amount_k.expression  # type: ignore[no-redef]
    def amount_k(cls):  # noqa: N805
        """SQL expression counterpart for queries."""
        return cast(Any, cls.amount) / 1000.0


def main() -> None:
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False)

    with Session() as session:
        session.execute(
            insert(Sale),
            [
                {"region": "east", "amount": 100},
                {"region": "east", "amount": 200},
                {"region": "west", "amount": 150},
            ],
        )
        session.commit()

    with Session() as session:
        # Common Table Expression aggregating per region.
        regional = (
            select(Sale.region, func.sum(Sale.amount).label("total"))
            .group_by(Sale.region)
            .cte("regional")
        )
        stmt = select(regional.c.region, regional.c.total).where(regional.c.total > 120)
        print("cte totals:", session.execute(stmt).all())

        # Window function: rank regions by total sale amount.
        ranked = (
            select(
                Sale.region,
                Sale.amount,
                func.rank().over(partition_by=Sale.region, order_by=Sale.amount.desc()).label("rk"),
            )
        )
        print("window sample:", session.execute(ranked).first())

        # Hybrid property in SQL.
        hybrid_rows = session.scalars(select(Sale).where(Sale.amount_k > 0.12)).all()
        print("hybrid filter count:", len(hybrid_rows))

    # Core bulk ORM update (SQLite supports RETURNING in recent versions; keep portable).
    with Session() as session:
        count = session.execute(text("UPDATE sales SET amount = amount + 1 WHERE region = 'EAST'"))
        session.commit()
        print("bulk-style update rowcount:", count.rowcount)


if __name__ == "__main__":
    main()
