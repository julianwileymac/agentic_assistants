# Chunk: 8cd7f2b9dbbc_2

- source: `.venv-lab/Lib/site-packages/jupyter_server/extension/handler.py`
- lines: 143-155
- chunk: 3/3

```
base = ""
        if include_host:
            base = self.request.protocol + "://" + self.request.host  # type:ignore[attr-defined]

        # Hijack settings dict to send extension templates to extension
        # static directory.
        settings = {
            "static_path": self.static_path,
            "static_url_prefix": self.static_url_prefix,
        }

        return base + cast(str, get_url(settings, path, **kwargs))
```
