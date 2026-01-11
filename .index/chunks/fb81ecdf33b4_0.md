# Chunk: fb81ecdf33b4_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/emoji/core.pyi`
- lines: 1-10
- chunk: 1/1

```
from typing import Dict, List, Optional, Pattern, Text, Tuple, Union

_DEFAULT_DELIMITER: str

def emojize(string: str, use_aliases: bool = ..., delimiters: Tuple[str, str] = ...) -> str: ...
def demojize(string: str, delimiters: Tuple[str, str] = ...) -> str: ...
def get_emoji_regexp() -> Pattern[Text]: ...
def emoji_lis(string: str) -> List[Dict[str, Union[int, str]]]: ...
def emoji_count(string: str) -> int: ...
```
