# Chunk: fd1dae8ba823_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/jinja2/meta.pyi`
- lines: 1-13
- chunk: 1/1

```
from typing import Any

from jinja2.compiler import CodeGenerator

class TrackingCodeGenerator(CodeGenerator):
    undeclared_identifiers: Any
    def __init__(self, environment) -> None: ...
    def write(self, x): ...
    def pull_locals(self, frame): ...

def find_undeclared_variables(ast): ...
def find_referenced_templates(ast): ...
```
