# Chunk: f0ddc4ffbba8_1

- source: `.venv-lab/Lib/site-packages/jupyter_client/adapter.py`
- lines: 94-184
- chunk: 2/6

```
"msg_type"], None)
        if handler is None:
            return msg

        # handle status=error replies separately (no change, at present)
        if msg["content"].get("status", None) in {"error", "aborted"}:
            return self.handle_reply_status_error(msg)
        return handler(msg)


def _version_str_to_list(version: str) -> list[int]:
    """convert a version string to a list of ints

    non-int segments are excluded
    """
    v = []
    for part in version.split("."):
        try:
            v.append(int(part))
        except ValueError:
            pass
    return v


class V5toV4(Adapter):
    """Adapt msg protocol v5 to v4"""

    version = "4.1"

    msg_type_map = {
        "execute_result": "pyout",
        "execute_input": "pyin",
        "error": "pyerr",
        "inspect_request": "object_info_request",
        "inspect_reply": "object_info_reply",
    }

    def update_header(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Update the header."""
        msg["header"].pop("version", None)
        msg["parent_header"].pop("version", None)
        return msg

    # shell channel

    def kernel_info_reply(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle a kernel info reply."""
        v4c = {}
        content = msg["content"]
        for key in ("language_version", "protocol_version"):
            if key in content:
                v4c[key] = _version_str_to_list(content[key])
        if content.get("implementation", "") == "ipython" and "implementation_version" in content:
            v4c["ipython_version"] = _version_str_to_list(content["implementation_version"])
        language_info = content.get("language_info", {})
        language = language_info.get("name", "")
        v4c.setdefault("language", language)
        if "version" in language_info:
            v4c.setdefault("language_version", _version_str_to_list(language_info["version"]))
        msg["content"] = v4c
        return msg

    def execute_request(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle an execute request."""
        content = msg["content"]
        content.setdefault("user_variables", [])
        return msg

    def execute_reply(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle an execute reply."""
        content = msg["content"]
        content.setdefault("user_variables", {})
        # TODO: handle payloads
        return msg

    def complete_request(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle a complete request."""
        content = msg["content"]
        code = content["code"]
        cursor_pos = content["cursor_pos"]
        line, cursor_pos = code_to_line(code, cursor_pos)

        new_content = msg["content"] = {}
        new_content["text"] = ""
        new_content["line"] = line
        new_content["block"] = None
        new_content["cursor_pos"] = cursor_pos
        return msg

    def complete_reply(self, msg: dict[str, Any]) -> dict[str, Any]:
```
