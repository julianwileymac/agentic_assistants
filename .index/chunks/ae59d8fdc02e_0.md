# Chunk: ae59d8fdc02e_0

- source: `.venv-lab/Lib/site-packages/jupyter_server_terminals/base.py`
- lines: 1-18
- chunk: 1/1

```
"""Base classes."""
from __future__ import annotations

from typing import TYPE_CHECKING

from jupyter_server.extension.handler import ExtensionHandlerMixin

if TYPE_CHECKING:
    from jupyter_server_terminals.terminalmanager import TerminalManager


class TerminalsMixin(ExtensionHandlerMixin):
    """An extension mixin for terminals."""

    @property
    def terminal_manager(self) -> TerminalManager:
        return self.settings["terminal_manager"]  # type:ignore[no-any-return]
```
