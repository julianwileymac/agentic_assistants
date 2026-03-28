# requires: litestar>=2 msgspec

"""
High-performance ``msgspec`` structs wired through ``MsgspecDTO``.

Litestar reuses msgspec's fast JSON codec for request/response transfer models.
Compared to Pydantic DTOs, structs allocate less and validate during decode — a
good fit for internal services where OpenAPI can still be generated from route
signatures and plugins.
"""

from __future__ import annotations

from typing import Annotated

import msgspec
from litestar import Litestar, get, post
from litestar.dto import MsgspecDTO
from litestar.exceptions import ClientException
from litestar.testing import TestClient


class CreateItem(msgspec.Struct):
    """Request body validated by msgspec before your handler runs."""

    name: Annotated[str, msgspec.Meta(min_length=1, max_length=80)]
    qty: Annotated[int, msgspec.Meta(ge=1, le=999)]


class ItemView(msgspec.Struct):
    """Response DTO — separate from persistence models."""

    id: int
    name: str
    qty: int


class CreateItemDTO(MsgspecDTO[CreateItem]):
    """Litestar transfers structs through encode/decode with minimal overhead."""

    pass


class ItemViewDTO(MsgspecDTO[ItemView]):
    pass


# --- Design notes -----------------------------------------------------------
# Msgspec structs excel for internal APIs; pair with integration tests for schema drift.
# Use separate request/response structs so you can evolve persistence independently.
# When errors must be rich, map ``msgspec.ValidationError`` to your problem+json format.
# ---------------------------------------------------------------------------


def create_app() -> Litestar:
    store: dict[int, ItemView] = {}
    counter = 1

    @post(
        "/items",
        dto=CreateItemDTO,
        return_dto=ItemViewDTO,
    )
    async def create_item(data: CreateItem) -> ItemView:
        nonlocal counter
        entity = ItemView(id=counter, name=data.name, qty=data.qty)
        store[counter] = entity
        counter += 1
        return entity

    @get("/items/{item_id:int}", return_dto=ItemViewDTO)
    async def get_item(item_id: int) -> ItemView:
        try:
            return store[item_id]
        except KeyError as exc:  # pragma: no cover - demo path
            raise ClientException(detail="not found", status_code=404) from exc

    return Litestar(route_handlers=[create_item, get_item])


def main() -> None:
    app = create_app()
    with TestClient(app=app) as client:
        res = client.post("/items", json={"name": "mug", "qty": 3})
        print("create:", res.status_code, res.json())
        created_id = res.json()["id"]
        fetched = client.get(f"/items/{created_id}")
        print("get:", fetched.status_code, fetched.json())
        bad = client.post("/items", json={"name": "", "qty": 3})
        print("validation:", bad.status_code)


if __name__ == "__main__":
    main()
