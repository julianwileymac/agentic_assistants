# Chunk: abde44ab0f94_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/encodings/__init__.pyi`
- lines: 1-8
- chunk: 1/1

```
import codecs
from typing import Any

def search_function(encoding: str) -> codecs.CodecInfo: ...

# Explicitly mark this package as incomplete.
def __getattr__(name: str) -> Any: ...
```
