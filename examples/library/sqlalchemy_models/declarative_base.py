# requires: sqlalchemy>=2

"""
SQLAlchemy 2.0 declarative style with typed ``Mapped`` columns and relationships.

Key ideas:

- ``Mapped[T]`` + ``mapped_column()`` give mypy/pyright-friendly models.
- ``relationship()`` expresses graph navigation; ``back_populates`` keeps both
  sides consistent without implicit magic.
- Prefer ``select()`` + ``Session.scalars()`` over legacy ``query()`` APIs.
"""

from __future__ import annotations

from typing import List

from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    """Application-wide declarative base."""


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    books: Mapped[List["Book"]] = relationship(back_populates="author")


# --- Design notes -----------------------------------------------------------
# ``relationship()`` defaults can hide N+1 queries — prefer explicit ``selectin`` loading.
# SQLite is great for demos; swap DSN only after patterns are understood.
# Alembic migrations should be generated from these models in real services.
# ---------------------------------------------------------------------------


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Author] = relationship(back_populates="books")


def main() -> None:
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False)

    with Session() as session:
        king = Author(name="Stephen King")
        session.add_all(
            [
                king,
                Book(title="The Shining", author=king),
                Book(title="Pet Sematary", author=king),
            ]
        )
        session.commit()

    with Session() as session:
        stmt = select(Author).where(Author.name == "Stephen King")
        author = session.scalars(stmt).one()
        titles = session.scalars(select(Book.title).where(Book.author_id == author.id)).all()
        print("author:", author.name)
        print("books:", titles)

        # ``scalars()`` returns a ``ScalarResult`` of scalar values or ORM rows.
        count = session.scalars(select(Book.id).where(Book.author_id == author.id)).all()
        print("book count:", len(count))

        joined = session.execute(
            select(Book.title, Author.name).join(Book.author).order_by(Book.title)
        ).all()
        print("joined rows (title, author):", joined)


if __name__ == "__main__":
    main()
