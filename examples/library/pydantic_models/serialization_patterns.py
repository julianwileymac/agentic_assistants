# requires: pydantic>=2

"""
Serialization controls: aliases, JSON mode, exclusions, and schema metadata.

``model_dump`` mirrors Python objects, while ``mode="json"`` guarantees JSON-native
values (``datetime`` to ``str``, ``Enum`` to value, etc.). Combining ``by_alias``
with ``exclude`` lets you serve public wire formats without maintaining parallel
DTO classes for simple cases.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class Event(BaseModel):
    """Domain model with camelCase wire format and custom timestamp encoding."""

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {"eventId": "evt_01", "createdAt": "2024-01-01T00:00:00Z", "score": 1.5}
            ]
        },
    )

    event_id: str = Field(alias="eventId")
    created_at: datetime = Field(alias="createdAt")
    score: float
    internal_note: str | None = Field(default=None, exclude=True)

    @field_serializer("created_at")
    def iso_z(self, value: datetime) -> str:
        """Emit RFC 3339 timestamps with a ``Z`` suffix for JSON clients."""
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- Design notes -----------------------------------------------------------
# ``exclude=True`` fields still exist on the model — only dumps omit them.
# Prefer explicit serializers over ``json_encoders`` dicts (removed in v2).
# For dual internal/external shapes at scale, graduate to dedicated DTO models.
# ---------------------------------------------------------------------------


def round_trip_json(model: type[BaseModel], instance: BaseModel) -> dict[str, Any]:
    """Serialize to JSON-compatible dict, dump to string, parse back."""
    as_json = instance.model_dump(mode="json", by_alias=True)
    text = json.dumps(as_json)
    back = json.loads(text)
    round_trip = model.model_validate(back)
    return round_trip.model_dump(mode="json", by_alias=True)


def main() -> None:
    ev = Event(
        eventId="evt_42",
        createdAt=datetime(2024, 6, 1, 12, 0, tzinfo=UTC),
        score=2.25,
        internal_note="not for clients",
    )

    # ``mode="json"`` converts datetimes, decimals, etc. to JSON-native values.
    full = ev.model_dump()
    public = ev.model_dump(exclude={"internal_note"}, mode="json", by_alias=True)
    print("full (python keys, includes excluded fields in dict):", "internal_note" in full)
    print("public json view:", public)

    # Round-trip preserves alias-oriented client payloads.
    again = round_trip_json(Event, ev)
    print("round trip == public:", again == public)

    schema = Event.model_json_schema()
    print("schema title + properties:", schema.get("title"), list(schema.get("properties", {}).keys()))

    # ``model_dump_json`` is a fast path when you need a UTF-8 JSON string directly.
    wire = ev.model_dump_json(by_alias=True, exclude={"internal_note"})
    parsed = json.loads(wire)
    print("dump_json keys:", sorted(parsed.keys()))

    # ``model_validate`` accepts the same JSON-shaped dict clients send back.
    clone = Event.model_validate(parsed)
    print("revalidated event_id alias field:", clone.event_id)


if __name__ == "__main__":
    main()
