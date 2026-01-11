# Chunk: f0ddc4ffbba8_2

- source: `.venv-lab/Lib/site-packages/jupyter_client/adapter.py`
- lines: 174-263
- chunk: 3/6

```
ode, cursor_pos)

        new_content = msg["content"] = {}
        new_content["text"] = ""
        new_content["line"] = line
        new_content["block"] = None
        new_content["cursor_pos"] = cursor_pos
        return msg

    def complete_reply(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle a complete reply."""
        content = msg["content"]
        cursor_start = content.pop("cursor_start")
        cursor_end = content.pop("cursor_end")
        match_len = cursor_end - cursor_start
        content["matched_text"] = content["matches"][0][:match_len]
        content.pop("metadata", None)
        return msg

    def object_info_request(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle an object info request."""
        content = msg["content"]
        code = content["code"]
        cursor_pos = content["cursor_pos"]
        _line, _ = code_to_line(code, cursor_pos)

        new_content = msg["content"] = {}
        new_content["oname"] = extract_oname_v4(code, cursor_pos)
        new_content["detail_level"] = content["detail_level"]
        return msg

    def object_info_reply(self, msg: dict[str, Any]) -> dict[str, Any]:
        """inspect_reply can't be easily backward compatible"""
        msg["content"] = {"found": False, "oname": "unknown"}
        return msg

    # iopub channel

    def stream(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle a stream message."""
        content = msg["content"]
        content["data"] = content.pop("text")
        return msg

    def display_data(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle a display data message."""
        content = msg["content"]
        content.setdefault("source", "display")
        data = content["data"]
        if "application/json" in data:
            try:
                data["application/json"] = json.dumps(data["application/json"])
            except Exception:
                # warn?
                pass
        return msg

    # stdin channel

    def input_request(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle an input request."""
        msg["content"].pop("password", None)
        return msg


class V4toV5(Adapter):
    """Convert msg spec V4 to V5"""

    version = "5.0"

    # invert message renames above
    msg_type_map = {v: k for k, v in V5toV4.msg_type_map.items()}

    def update_header(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Update the header."""
        msg["header"]["version"] = self.version
        if msg["parent_header"]:
            msg["parent_header"]["version"] = self.version
        return msg

    # shell channel

    def kernel_info_reply(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle a kernel info reply."""
        content = msg["content"]
        for key in ("protocol_version", "ipython_version"):
            if key in content:
                content[key] = ".".join(map(str, content[key]))
```
