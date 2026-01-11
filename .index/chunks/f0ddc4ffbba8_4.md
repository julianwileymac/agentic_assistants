# Chunk: f0ddc4ffbba8_4

- source: `.venv-lab/Lib/site-packages/jupyter_client/adapter.py`
- lines: 319-404
- chunk: 5/6

```
 indicates that start == end (accounts for no -0).
        content = msg["content"]
        new_content = msg["content"] = {"status": "ok"}
        new_content["matches"] = content["matches"]
        if content["matched_text"]:
            new_content["cursor_start"] = -len(content["matched_text"])
        else:
            # no -0, use None to indicate that start == end
            new_content["cursor_start"] = None
        new_content["cursor_end"] = None
        new_content["metadata"] = {}
        return msg

    def inspect_request(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle an inspect request."""
        content = msg["content"]
        name = content["oname"]

        new_content = msg["content"] = {}
        new_content["code"] = name
        new_content["cursor_pos"] = len(name)
        new_content["detail_level"] = content["detail_level"]
        return msg

    def inspect_reply(self, msg: dict[str, Any]) -> dict[str, Any]:
        """inspect_reply can't be easily backward compatible"""
        content = msg["content"]
        new_content = msg["content"] = {"status": "ok"}
        found = new_content["found"] = content["found"]
        new_content["data"] = data = {}
        new_content["metadata"] = {}
        if found:
            lines = []
            for key in ("call_def", "init_definition", "definition"):
                if content.get(key, False):
                    lines.append(content[key])
                    break
            for key in ("call_docstring", "init_docstring", "docstring"):
                if content.get(key, False):
                    lines.append(content[key])
                    break
            if not lines:
                lines.append("<empty docstring>")
            data["text/plain"] = "\n".join(lines)
        return msg

    # iopub channel

    def stream(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle a stream message."""
        content = msg["content"]
        content["text"] = content.pop("data")
        return msg

    def display_data(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle display data."""
        content = msg["content"]
        content.pop("source", None)
        data = content["data"]
        if "application/json" in data:
            try:
                data["application/json"] = json.loads(data["application/json"])
            except Exception:
                # warn?
                pass
        return msg

    # stdin channel

    def input_request(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Handle an input request."""
        msg["content"].setdefault("password", False)
        return msg


def adapt(msg: dict[str, Any], to_version: int = protocol_version_info[0]) -> dict[str, Any]:
    """Adapt a single message to a target version

    Parameters
    ----------

    msg : dict
        A Jupyter message.
    to_version : int, optional
        The target major version.
```
