# Chunk: bd8295b5dadd_0

- source: `.venv-lab/Lib/site-packages/setuptools/compat/py312.py`
- lines: 1-14
- chunk: 1/1

```
from __future__ import annotations

import sys

if sys.version_info >= (3, 12, 4):
    # Python 3.13 should support `.pth` files encoded in UTF-8
    # See discussion in https://github.com/python/cpython/issues/77102
    PTH_ENCODING: str | None = "utf-8"
else:
    from .py39 import LOCALE_ENCODING

    # PTH_ENCODING = "locale"
    PTH_ENCODING = LOCALE_ENCODING
```
