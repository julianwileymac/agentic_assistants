# Chunk: 5ab9dda527ba_0

- source: `.venv-lab/Lib/site-packages/pip/_vendor/pygments/__main__.py`
- lines: 1-18
- chunk: 1/1

```
"""
    pygments.__main__
    ~~~~~~~~~~~~~~~~~

    Main entry point for ``python -m pygments``.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import sys
from pip._vendor.pygments.cmdline import main

try:
    sys.exit(main(sys.argv))
except KeyboardInterrupt:
    sys.exit(1)
```
