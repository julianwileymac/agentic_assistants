# Chunk: c0ba9f7de58d_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/markdown/extensions/fenced_code.pyi`
- lines: 1-17
- chunk: 1/1

```
from typing import Any, Pattern

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

class FencedCodeExtension(Extension): ...

class FencedBlockPreprocessor(Preprocessor):
    FENCED_BLOCK_RE: Pattern
    CODE_WRAP: str = ...
    LANG_TAG: str = ...
    checked_for_codehilite: bool = ...
    codehilite_conf: Any
    def __init__(self, md) -> None: ...

def makeExtension(**kwargs): ...
```
