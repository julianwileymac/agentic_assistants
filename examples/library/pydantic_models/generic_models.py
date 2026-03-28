# requires: pydantic>=2

"""
Generic Pydantic models, discriminated unions, and ``TypeAdapter`` usage.

Generics let you define envelopes like ``ApiResponse[T]`` once and specialize ``T``
per endpoint. ``Field(discriminator=...)`` keeps unions efficient — pydantic does
not need to try every variant blindly. ``TypeAdapter`` extends the same machinery
to arbitrary annotated types, not only ``BaseModel`` subclasses.
"""

from __future__ import annotations

import json
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, Field, TypeAdapter

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API envelope carrying typed ``data``."""

    ok: bool = True
    data: T


class Container(BaseModel, Generic[T]):
    """Named box around a single value — useful for schema reuse."""

    name: str
    value: T


class Cat(BaseModel):
    pet_type: Literal["cat"] = "cat"
    lives: int = Field(ge=0, le=9)


class Dog(BaseModel):
    pet_type: Literal["dog"] = "dog"
    breed: str


# Discriminated union on ``pet_type`` keeps validation precise and fast.
Pet = Annotated[Cat | Dog, Field(discriminator="pet_type")]


class TaggedSuccess(BaseModel):
    status: Literal["success"] = "success"
    payload: str


class TaggedFailure(BaseModel):
    status: Literal["failure"] = "failure"
    code: int
    detail: str


Outcome = Annotated[TaggedSuccess | TaggedFailure, Field(discriminator="status")]


# --- Design notes -----------------------------------------------------------
# Prefer ``Literal`` tags over guessing union order — discriminators fail loudly.
# ``TypeAdapter`` is ideal for JSON columns or Celery payloads typed as ``dict``.
# Keep generics shallow; deeply nested ``ApiResponse[Container[T]]`` hurts readability.
# ---------------------------------------------------------------------------


def main() -> None:
    # Generic model: concrete schema depends on bound type argument.
    numbers = ApiResponse[list[int]](data=[1, 2, 3])
    print("api response:", numbers.model_dump())

    container = Container[float](name="pi", value=3.14159)
    print("container:", container.model_dump())

    pets = TypeAdapter(list[Pet])
    raw = [
        {"pet_type": "cat", "lives": 7},
        {"pet_type": "dog", "breed": "collie"},
    ]
    validated = pets.validate_python(raw)
    print("pets:", [p.model_dump() for p in validated])

    # TypeAdapter works for non-``BaseModel`` types (here: dict[str, Outcome]).
    outcomes_adapter = TypeAdapter(dict[str, Outcome])
    blob = json.dumps(
        {
            "a": {"status": "success", "payload": "done"},
            "b": {"status": "failure", "code": 404, "detail": "missing"},
        }
    )
    parsed = outcomes_adapter.validate_json(blob)
    print("outcomes:", {k: v.model_dump() for k, v in parsed.items()})

    print("union json schema keys:", list(TypeAdapter(Outcome).json_schema().keys()))

    # Adapters can also emit schemas for bare generics.
    adapter = TypeAdapter(ApiResponse[float])
    print("specialized response title:", adapter.json_schema().get("title"))


if __name__ == "__main__":
    main()
