# Chunk: 336ff4bdb2fd_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/django-stubs/django-stubs/db/backends/base/client.pyi`
- lines: 1-10
- chunk: 1/1

```
from typing import Any

from django.db.backends.base.base import BaseDatabaseWrapper

class BaseDatabaseClient:
    executable_name: Any = ...
    connection: Any = ...
    def __init__(self, connection: BaseDatabaseWrapper) -> None: ...
    def runshell(self) -> None: ...
```
