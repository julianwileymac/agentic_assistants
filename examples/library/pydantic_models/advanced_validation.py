# requires: pydantic>=2

"""
Advanced Pydantic v2 validation patterns for production schemas.

Demonstrates field validators, model validators, computed fields, ``Annotated``
constraints, ``BeforeValidator`` / ``AfterValidator``, and JSON Schema export.

Computed fields appear in ``model_dump`` and schema output; use them for derived
values that should stay in sync with source fields without manual bookkeeping.
Model validators run after field validators, making them ideal for invariants
that involve multiple attributes.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Annotated, Any

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
    model_validator,
)


def _strip_and_lower(v: Any) -> str:
    """Normalize arbitrary input to a clean lowercase string."""
    if isinstance(v, str):
        return v.strip().lower()
    return str(v).strip().lower()


def _must_be_positive_money(v: Decimal) -> Decimal:
    if v <= 0:
        raise ValueError("amount must be positive")
    return v.quantize(Decimal("0.01"))


Username = Annotated[
    str,
    StringConstraints(min_length=3, max_length=32, pattern=r"^[a-z0-9_]+$"),
    BeforeValidator(_strip_and_lower),
]


class InvoiceLine(BaseModel):
    """Single invoice line with constrained numeric fields."""

    model_config = ConfigDict(str_strip_whitespace=True)

    sku: str = Field(min_length=1, max_length=64)
    quantity: Annotated[int, Field(gt=0, le=10_000)]
    unit_price: Annotated[Decimal, AfterValidator(_must_be_positive_money)]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def line_total(self) -> Decimal:
        """Derived total; included in serialization and JSON Schema as read-only."""
        return (self.quantity * self.unit_price).quantize(Decimal("0.01"))

    @field_validator("sku")
    @classmethod
    def sku_uppercase(cls, v: str) -> str:
        """Keep SKUs in a canonical display form."""
        return v.upper()


class Invoice(BaseModel):
    """Invoice with cross-field consistency enforced at the model level."""

    model_config = ConfigDict(extra="forbid")

    customer: Username
    lines: list[InvoiceLine] = Field(min_length=1)

    @model_validator(mode="after")
    def at_least_one_nonzero_line(self) -> Invoice:
        """Reject empty-looking invoices after per-field validation runs."""
        if all(line.quantity == 0 for line in self.lines):
            raise ValueError("invoice must contain at least one line with quantity > 0")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def grand_total(self) -> Decimal:
        return sum((line.line_total for line in self.lines), start=Decimal("0"))


def main() -> None:
    inv = Invoice(
        customer="  Alice_1 ",
        lines=[
            InvoiceLine(sku="widget", quantity=2, unit_price=Decimal("19.995")),
        ],
    )
    print("validated:", inv.model_dump())
    schema = inv.model_json_schema()
    print("json schema (excerpt):", json.dumps({k: schema[k] for k in ("title", "properties")}, indent=2))


if __name__ == "__main__":
    main()
