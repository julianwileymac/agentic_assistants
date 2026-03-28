# requires: litestar>=2 pydantic>=2

"""
DTOs as API boundaries: hide persistence fields from wire formats.

``DataclassDTO`` and ``PydanticDTO`` wrap internal models with include / exclude
rules so route signatures stay explicit and clients see stable shapes.

Why separate ``UserCreate`` from ``UserRecord``? Incoming payloads should not
declare server fields (``id``, ``password_hash``). Outgoing DTOs then strip
secrets and apply naming policies (camelCase, snake_case) independent of storage.
``PydanticDTO`` lives under ``litestar.plugins.pydantic`` — ensure the Pydantic
plugin is enabled if you customize the application container.
"""

from __future__ import annotations

from dataclasses import dataclass

from litestar import Litestar, post
from litestar.dto import DataclassDTO, DTOConfig
from litestar.plugins.pydantic.dto import PydanticDTO
from litestar.testing import TestClient
from pydantic import BaseModel, ConfigDict, Field


@dataclass
class UserCreate:
    """Public fields accepted on create — no server-assigned ``id`` yet."""

    email: str
    display_name: str


@dataclass
class UserRecord:
    """Internal representation (e.g. loaded from a database row)."""

    id: int
    email: str
    password_hash: str
    display_name: str


class UserCreateDTO(DataclassDTO[UserCreate]):
    """Validate and rename incoming JSON before the handler runs."""

    config = DTOConfig(rename_strategy="camel")


class UserResponseDTO(DataclassDTO[UserRecord]):
    """Responses omit secrets and rename for JSON clients."""

    config = DTOConfig(
        exclude={"password_hash"},
        rename_strategy="camel",
    )


class NotePayload(BaseModel):
    """Pydantic-backed body model for another style of DTO."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=3)
    body: str


class NoteModel(BaseModel):
    id: int
    title: str
    body: str
    owner_id: int


class NoteResponseDTO(PydanticDTO[NoteModel]):
    config = DTOConfig(exclude={"owner_id"})


# --- Design notes when porting this pattern ---------------------------------
# 1. Keep DTO types next to route modules for discoverability.
# 2. Prefer ``rename_strategy`` over manual alias fields when naming policies are uniform.
# 3. For nested bodies, compose multiple DTO classes instead of one giant model.
# 4. Integration tests should assert both accepted JSON and rejected field sets.
# -----------------------------------------------------------------------------


def create_app() -> Litestar:
    store: dict[int, UserRecord] = {}
    next_id = 1

    @post("/users", dto=UserCreateDTO, return_dto=UserResponseDTO)
    async def create_user(data: UserCreate) -> UserRecord:
        nonlocal next_id
        user = UserRecord(
            id=next_id,
            email=data.email,
            password_hash="hashed-secret",
            display_name=data.display_name,
        )
        store[user.id] = user
        next_id += 1
        return user

    @post("/notes", return_dto=NoteResponseDTO)
    async def create_note(data: NotePayload) -> NoteModel:
        return NoteModel(id=99, title=data.title, body=data.body, owner_id=1)

    return Litestar(route_handlers=[create_user, create_note])


def main() -> None:
    app = create_app()
    with TestClient(app=app) as client:
        res = client.post("/users", json={"email": "a@b.com", "displayName": "Ada"})
        print("user status:", res.status_code, res.json())
        note = client.post("/notes", json={"title": "Hello", "body": "world"})
        print("note json (owner hidden):", note.json())


if __name__ == "__main__":
    main()
