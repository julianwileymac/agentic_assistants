# requires: msgspec

"""
Validation with ``msgspec.Meta``, decode hooks, optional fields, and tagged unions.

``msgspec`` validates during decode; constraints attach to field annotations via
``Meta``. Custom conversions use ``dec_hook`` on ``Decoder`` / ``Encoder``.
"""

from __future__ import annotations

from typing import Annotated, Any

import msgspec


class User(msgspec.Struct, forbid_unknown_fields=True):
    name: Annotated[str, msgspec.Meta(min_length=1, max_length=40)]
    age: Annotated[int, msgspec.Meta(ge=0, le=130)] | None = None
    role: str = "member"


class EventV1(msgspec.Struct, tag=True):
    kind: str
    payload: str


class EventV2(msgspec.Struct, tag=True):
    kind: str
    payload: dict[str, str]


DecodedEvent = EventV1 | EventV2


class HexBlob(msgspec.Struct):
    """Hex payload transported as a string to avoid JSON binary encoding quirks."""

    data_hex: str

    def as_bytes(self) -> bytes:
        return bytes.fromhex(self.data_hex)


# --- Design notes -----------------------------------------------------------
# Keep dec_hooks small and fast — they run for every matching field during decode.
# Tagged unions need stable ``type`` discriminators; rename tags only with migration plans.
# Combine ``Meta`` constraints with integration tests for malformed producer payloads.
# ---------------------------------------------------------------------------


def main() -> None:
    # Decoders are reusable and thread-safe; construct them once per type in hot paths.
    dec = msgspec.json.Decoder(User)
    user = dec.decode(b'{"name":"Ada","age":36,"role":"admin"}')
    print("user:", user)

    bad = b'{"name":"","age":200}'
    try:
        dec.decode(bad)
    except msgspec.ValidationError as exc:
        print("validation error:", exc)

    blob = msgspec.json.decode(b'{"data_hex":"414243"}', type=HexBlob)
    print("hex -> ascii bytes:", blob.as_bytes())

    union_dec = msgspec.json.Decoder(DecodedEvent)
    v1 = union_dec.decode(b'{"type":"EventV1","kind":"ping","payload":"ok"}')
    v2 = union_dec.decode(b'{"type":"EventV2","kind":"log","payload":{"k":"v"}}')
    print("union members:", type(v1).__name__, type(v2).__name__)

    # Optional field omitted on the wire decodes as ``None`` / default.
    minimal = dec.decode(b'{"name":"Bob"}')
    print("defaults:", minimal.age, minimal.role)


if __name__ == "__main__":
    main()
