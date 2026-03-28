# requires: msgspec fastapi sqlalchemy>=2

"""
Bridging ``msgspec`` with FastAPI responses and SQLAlchemy row materialization.

FastAPI does not natively treat ``msgspec.Struct`` like ``BaseModel``; returning
pre-encoded bytes with an explicit media type keeps types strict and fast.

For larger teams, consider wrapping this pattern in a small helper or
``JSONResponse`` subclass so routes do not repeat encoder calls. When you need
OpenAPI models, generate parallel Pydantic schemas or document raw JSON shapes
explicitly.
"""

from __future__ import annotations

from typing import Any

import msgspec
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient
from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class UserStruct(msgspec.Struct, rename="camel"):
    id: int
    display_name: str


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    display_name: Mapped[str] = mapped_column(String(120))


def row_to_struct(row: UserRow) -> UserStruct:
    """Explicit boundary: ORM entity in, immutable API struct out."""
    return UserStruct(id=row.id, display_name=row.display_name)


def build_app() -> FastAPI:
    # In-memory SQLite needs a shared pool or each connection sees a different empty file.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False)
    with Session() as session:
        session.add(UserRow(display_name="Ada"))
        session.commit()

    app = FastAPI()

    @app.get("/users/{user_id}")
    def get_user(user_id: int) -> Response:
        with Session() as session:
            row = session.scalars(select(UserRow).where(UserRow.id == user_id)).one()
            payload = row_to_struct(row)
        # ``msgspec`` produces compact UTF-8 JSON without an intermediate ``dict``.
        return Response(
            content=msgspec.json.encode(payload),
            media_type="application/json",
        )

    return app


def sqlalchemy_to_msgspec_bulk(session: Any) -> bytes:
    """Batch path: decode rows into structs and encode as a JSON array."""
    rows = session.scalars(select(UserRow)).all()
    structs = [row_to_struct(r) for r in rows]
    return msgspec.json.encode(structs)


def main() -> None:
    app = build_app()
    with TestClient(app) as client:
        res = client.get("/users/1")
        print("status:", res.status_code, "body:", res.json())

    engine2 = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(engine2)
    Session = sessionmaker(engine2, expire_on_commit=False)
    with Session() as session:
        session.add(UserRow(display_name="Grace"))
        session.commit()
        blob = sqlalchemy_to_msgspec_bulk(session)
        print("bulk json:", blob.decode())


if __name__ == "__main__":
    main()
