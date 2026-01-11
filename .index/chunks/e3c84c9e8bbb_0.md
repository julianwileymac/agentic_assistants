# Chunk: e3c84c9e8bbb_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/keyword.pyi`
- lines: 1-11
- chunk: 1/1

```
import sys
from typing import Sequence, Text

def iskeyword(s: Text) -> bool: ...

kwlist: Sequence[str]

if sys.version_info >= (3, 9):
    def issoftkeyword(s: str) -> bool: ...
    softkwlist: Sequence[str]
```
