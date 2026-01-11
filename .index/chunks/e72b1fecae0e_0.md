# Chunk: e72b1fecae0e_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/asyncio/staggered.pyi`
- lines: 1-13
- chunk: 1/1

```
import sys
from typing import Any, Awaitable, Callable, Iterable, List, Optional, Tuple

from . import events

if sys.version_info >= (3, 8):
    async def staggered_race(
        coro_fns: Iterable[Callable[[], Awaitable[Any]]],
        delay: Optional[float],
        *,
        loop: Optional[events.AbstractEventLoop] = ...,
    ) -> Tuple[Any, Optional[int], List[Optional[Exception]]]: ...
```
