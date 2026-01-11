# Chunk: f82f0e2bbaf1_0

- source: `.venv-lab/Lib/site-packages/pip/_vendor/rich/_stack.py`
- lines: 1-17
- chunk: 1/1

```
from typing import List, TypeVar

T = TypeVar("T")


class Stack(List[T]):
    """A small shim over builtin list."""

    @property
    def top(self) -> T:
        """Get top of stack."""
        return self[-1]

    def push(self, item: T) -> None:
        """Push an item on to the stack (append in stack nomenclature)."""
        self.append(item)
```
