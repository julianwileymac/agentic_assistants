# Chunk: 57eeabe313db_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/curses/textpad.pyi`
- lines: 1-12
- chunk: 1/1

```
from _curses import _CursesWindow
from typing import Callable, Optional, Union

def rectangle(win: _CursesWindow, uly: int, ulx: int, lry: int, lrx: int) -> None: ...

class Textbox:
    stripspaces: bool
    def __init__(self, win: _CursesWindow, insert_mode: bool = ...) -> None: ...
    def edit(self, validate: Optional[Callable[[int], int]] = ...) -> str: ...
    def do_command(self, ch: Union[str, int]) -> None: ...
    def gather(self) -> str: ...
```
