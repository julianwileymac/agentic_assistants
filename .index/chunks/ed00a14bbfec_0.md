# Chunk: ed00a14bbfec_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/boto/auth_handler.pyi`
- lines: 1-11
- chunk: 1/1

```
from typing import Any

from boto.plugin import Plugin

class NotReadyToAuthenticate(Exception): ...

class AuthHandler(Plugin):
    capability: Any
    def __init__(self, host, config, provider) -> None: ...
    def add_auth(self, http_request): ...
```
