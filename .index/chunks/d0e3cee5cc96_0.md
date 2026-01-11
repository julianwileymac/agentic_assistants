# Chunk: d0e3cee5cc96_0

- source: `.venv-lab/Lib/site-packages/lark/__init__.py`
- lines: 1-40
- chunk: 1/1

```
from .exceptions import (
    GrammarError,
    LarkError,
    LexError,
    ParseError,
    UnexpectedCharacters,
    UnexpectedEOF,
    UnexpectedInput,
    UnexpectedToken,
)
from .lark import Lark
from .lexer import Token
from .tree import ParseTree, Tree
from .utils import logger, TextSlice
from .visitors import Discard, Transformer, Transformer_NonRecursive, Visitor, v_args

__version__: str = "1.3.1"

__all__ = (
    "GrammarError",
    "LarkError",
    "LexError",
    "ParseError",
    "UnexpectedCharacters",
    "UnexpectedEOF",
    "UnexpectedInput",
    "UnexpectedToken",
    "Lark",
    "Token",
    "ParseTree",
    "Tree",
    "logger",
    "Discard",
    "Transformer",
    "Transformer_NonRecursive",
    "TextSlice",
    "Visitor",
    "v_args",
)
```
