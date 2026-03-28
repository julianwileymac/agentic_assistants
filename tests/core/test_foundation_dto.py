from __future__ import annotations

import pytest
from pydantic import BaseModel

from agentic_assistants.core.foundation import BaseDTO, DTOConfig


class User(BaseModel):
    id: str
    full_name: str
    email_address: str


class UserReadDTO(BaseDTO[User]):
    class Config(DTOConfig):
        exclude = {"id"}
        rename_strategy = "camel"


class StrictPatchDTO(BaseDTO[User]):
    class Config(DTOConfig):
        partial = True
        forbid_unknown_fields = True


def test_from_model_renames_and_excludes() -> None:
    user = User(id="u1", full_name="A User", email_address="a@example.com")
    payload = UserReadDTO.from_model(user)
    assert "id" not in payload
    assert payload["fullName"] == "A User"
    assert payload["emailAddress"] == "a@example.com"


def test_round_trip() -> None:
    user = User(id="u2", full_name="B User", email_address="b@example.com")
    mirrored = UserReadDTO.round_trip(user)
    assert mirrored.full_name == "B User"
    assert mirrored.email_address == "b@example.com"


def test_forbid_unknown_fields() -> None:
    with pytest.raises(ValueError):
        StrictPatchDTO.to_model({"not_a_field": 1})

