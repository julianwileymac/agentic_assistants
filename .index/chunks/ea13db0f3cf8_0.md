# Chunk: ea13db0f3cf8_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2/getopt.pyi`
- lines: 1-13
- chunk: 1/1

```
from typing import List, Tuple

class GetoptError(Exception):
    opt: str
    msg: str
    def __init__(self, msg: str, opt: str = ...) -> None: ...
    def __str__(self) -> str: ...

error = GetoptError

def getopt(args: List[str], shortopts: str, longopts: List[str] = ...) -> Tuple[List[Tuple[str, str]], List[str]]: ...
def gnu_getopt(args: List[str], shortopts: str, longopts: List[str] = ...) -> Tuple[List[Tuple[str, str]], List[str]]: ...
```
