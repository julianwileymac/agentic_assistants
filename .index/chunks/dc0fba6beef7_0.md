# Chunk: dc0fba6beef7_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/boto/s3/bucketlogging.pyi`
- lines: 1-12
- chunk: 1/1

```
from typing import Any, Optional

class BucketLogging:
    target: Any
    prefix: Any
    grants: Any
    def __init__(self, target: Optional[Any] = ..., prefix: Optional[Any] = ..., grants: Optional[Any] = ...) -> None: ...
    def add_grant(self, grant): ...
    def startElement(self, name, attrs, connection): ...
    def endElement(self, name, value, connection): ...
    def to_xml(self): ...
```
