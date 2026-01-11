# Chunk: d5c1ea8ec7c5_0

- source: `.venv-lab/Lib/site-packages/pip/_internal/main.py`
- lines: 1-13
- chunk: 1/1

```
from __future__ import annotations


def main(args: list[str] | None = None) -> int:
    """This is preserved for old console scripts that may still be referencing
    it.

    For additional details, see https://github.com/pypa/pip/issues/7498.
    """
    from pip._internal.utils.entrypoints import _wrapper

    return _wrapper(args)
```
