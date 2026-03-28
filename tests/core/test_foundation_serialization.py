from __future__ import annotations

from pydantic import BaseModel

from agentic_assistants.core.foundation import (
    JsonSerializer,
    PydanticSerializer,
    get_serializer,
    register_serializer,
)


class Payload(BaseModel):
    value: int


class _EchoSerializer:
    def encode(self, obj):
        return b"echo"

    def decode(self, data, target_type=None):
        return {"raw": data}


def test_json_serializer_round_trip() -> None:
    serializer = JsonSerializer()
    encoded = serializer.encode({"a": 1})
    decoded = serializer.decode(encoded)
    assert decoded == {"a": 1}


def test_pydantic_serializer_round_trip() -> None:
    serializer = PydanticSerializer()
    encoded = serializer.encode(Payload(value=3))
    decoded = serializer.decode(encoded, target_type=Payload)
    assert isinstance(decoded, Payload)
    assert decoded.value == 3


def test_register_serializer() -> None:
    register_serializer("echo", _EchoSerializer)
    serializer = get_serializer("echo")
    assert serializer.decode(serializer.encode({"x": 1})) == {"raw": b"echo"}

