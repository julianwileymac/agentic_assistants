# Chunk: aeab810a9fe0_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/boto/plugin.pyi`
- lines: 1-10
- chunk: 1/1

```
from typing import Any, Optional

class Plugin:
    capability: Any
    @classmethod
    def is_capable(cls, requested_capability): ...

def get_plugin(cls, requested_capability: Optional[Any] = ...): ...
def load_plugins(config): ...
```
