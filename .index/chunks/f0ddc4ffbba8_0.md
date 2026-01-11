# Chunk: f0ddc4ffbba8_0

- source: `.venv-lab/Lib/site-packages/jupyter_client/adapter.py`
- lines: 1-104
- chunk: 1/6

```
"""Adapters for Jupyter msg spec versions."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import json
import re
from typing import Any

from ._version import protocol_version_info


def code_to_line(code: str, cursor_pos: int) -> tuple[str, int]:
    """Turn a multiline code block and cursor position into a single line
    and new cursor position.

    For adapting ``complete_`` and ``object_info_request``.
    """
    if not code:
        return "", 0
    for line in code.splitlines(True):
        n = len(line)
        if cursor_pos > n:
            cursor_pos -= n
        else:
            break
    return line, cursor_pos


_match_bracket = re.compile(r"\([^\(\)]+\)", re.UNICODE)
_end_bracket = re.compile(r"\([^\(]*$", re.UNICODE)
_identifier = re.compile(r"[a-z_][0-9a-z._]*", re.I | re.UNICODE)


def extract_oname_v4(code: str, cursor_pos: int) -> str:
    """Reimplement token-finding logic from IPython 2.x javascript

    for adapting object_info_request from v5 to v4
    """

    line, _ = code_to_line(code, cursor_pos)

    oldline = line
    line = _match_bracket.sub("", line)
    while oldline != line:
        oldline = line
        line = _match_bracket.sub("", line)

    # remove everything after last open bracket
    line = _end_bracket.sub("", line)
    matches = _identifier.findall(line)
    if matches:
        return matches[-1]
    else:
        return ""


class Adapter:
    """Base class for adapting messages

    Override message_type(msg) methods to create adapters.
    """

    msg_type_map: dict[str, str] = {}

    def update_header(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Update the header."""
        return msg

    def update_metadata(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Update the metadata."""
        return msg

    def update_msg_type(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Update the message type."""
        header = msg["header"]
        msg_type = header["msg_type"]
        if msg_type in self.msg_type_map:
            msg["msg_type"] = header["msg_type"] = self.msg_type_map[msg_type]
        return msg

    def handle_reply_status_error(self, msg: dict[str, Any]) -> dict[str, Any]:
        """This will be called *instead of* the regular handler

        on any reply with status != ok
        """
        return msg

    def __call__(self, msg: dict[str, Any]) -> dict[str, Any]:
        msg = self.update_header(msg)
        msg = self.update_metadata(msg)
        msg = self.update_msg_type(msg)
        header = msg["header"]

        handler = getattr(self, header["msg_type"], None)
        if handler is None:
            return msg

        # handle status=error replies separately (no change, at present)
        if msg["content"].get("status", None) in {"error", "aborted"}:
            return self.handle_reply_status_error(msg)
        return handler(msg)
```
