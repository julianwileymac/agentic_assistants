# Chunk: b5ede3c9fca2_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/werkzeug/filesystem.pyi`
- lines: 1-8
- chunk: 1/1

```
from typing import Any

has_likely_buggy_unicode_filesystem: Any

class BrokenFilesystemWarning(RuntimeWarning, UnicodeWarning): ...

def get_filesystem_encoding(): ...
```
