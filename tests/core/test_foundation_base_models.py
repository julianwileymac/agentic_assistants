from __future__ import annotations

import uuid

from agentic_assistants.core.foundation import AgenticEntity, Envelope, ErrorDetail, PaginatedResponse


class Project(AgenticEntity):
    name: str


def test_agentic_entity_defaults() -> None:
    project = Project(name="demo")
    assert isinstance(project.id, uuid.UUID)
    assert project.created_at is not None


def test_paginated_response_flags() -> None:
    payload = PaginatedResponse[Project](
        items=[Project(name="a"), Project(name="b")],
        total=20,
        page=1,
        page_size=10,
    )
    assert payload.has_next is True
    assert payload.has_prev is False
    assert payload.page_count == 2


def test_envelope_success_and_errors() -> None:
    ok = Envelope[str](data="done")
    bad = Envelope[str](errors=[ErrorDetail(message="failed")])
    assert ok.success is True
    assert bad.success is False

