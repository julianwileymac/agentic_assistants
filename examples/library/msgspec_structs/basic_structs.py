# requires: msgspec

"""
Core ``msgspec.Struct`` patterns: immutability, slots, and optional GC tracking.

Structs are compact data carriers — closer to C structs than full ORM models.
"""

from __future__ import annotations

import gc
from typing import ClassVar

import msgspec


class Point(msgspec.Struct, rename="camel"):
    """Field names serialize as camelCase on the wire."""

    x: float
    y: float


class VersionedPayload(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """
    ``frozen=True`` makes instances hashable and prevents accidental mutation.

    ``forbid_unknown_fields=True`` rejects extra keys when decoding JSON/MessagePack.
    """

    schema_version: int
    data: str


class CacheEntry(msgspec.Struct, frozen=True, gc=False):
    """
    ``gc=False`` opts the type out of tracked garbage collection (faster, but
    cycles involving this type may leak — avoid reference cycles).
    """

    key: str
    value: bytes


class Metric(msgspec.Struct):
    """Mutable struct with ``__slots__`` implied by msgspec (no ``__dict__``)."""

    name: str
    value: float
    tags: dict[str, str] = {}
    kind: ClassVar[str] = "gauge"


# --- Design notes -----------------------------------------------------------
# Prefer ``frozen=True`` for value objects passed across threads or stored in caches.
# ``rename`` maps Pythonic names to external APIs without duplicating models.
# Avoid mutable defaults on fields other than ``dict``/``list`` factories — same as dataclasses.
# ---------------------------------------------------------------------------


def main() -> None:
    p = Point(x=1.5, y=2.5)
    wire = msgspec.json.encode(p)
    print("point json:", wire.decode())
    # Round-trip decode enforces types and field names (respecting ``rename``).
    same = msgspec.json.decode(wire, type=Point)
    print("round trip x:", same.x)

    packed = msgspec.msgpack.encode(p)
    from_msgpack = msgspec.msgpack.decode(packed, type=Point)
    print("msgpack round trip:", from_msgpack)

    payload = VersionedPayload(schema_version=1, data="hello")
    try:
        payload.data = "nope"  # type: ignore[misc]
    except AttributeError as exc:
        print("frozen blocks mutation:", exc)

    before = len(gc.get_objects())
    entries = [CacheEntry(key=str(i), value=b"x") for i in range(200)]
    after = len(gc.get_objects())
    print("cache entries:", len(entries), "gc object delta (rough):", after - before)

    m = Metric(name="cpu", value=0.42, tags={"host": "a"})
    print("metric slots:", getattr(Metric, "__slots__", ()))


if __name__ == "__main__":
    main()
