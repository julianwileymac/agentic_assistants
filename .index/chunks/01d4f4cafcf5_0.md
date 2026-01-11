# Chunk: 01d4f4cafcf5_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/werkzeug/contrib/wrappers.pyi`
- lines: 1-28
- chunk: 1/1

```
from typing import Any

def is_known_charset(charset): ...

class JSONRequestMixin:
    def json(self): ...

class ProtobufRequestMixin:
    protobuf_check_initialization: Any
    def parse_protobuf(self, proto_type): ...

class RoutingArgsRequestMixin:
    routing_args: Any
    routing_vars: Any

class ReverseSlashBehaviorRequestMixin:
    def path(self): ...
    def script_root(self): ...

class DynamicCharsetRequestMixin:
    default_charset: Any
    def unknown_charset(self, charset): ...
    def charset(self): ...

class DynamicCharsetResponseMixin:
    default_charset: Any
    charset: Any
```
