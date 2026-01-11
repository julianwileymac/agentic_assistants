# Chunk: 5b8cda1f1fb8_0

- source: `.venv-lab/Lib/site-packages/ipykernel/control.py`
- lines: 1-12
- chunk: 1/1

```
"""A thread for a control channel."""

from .thread import CONTROL_THREAD_NAME, BaseThread


class ControlThread(BaseThread):
    """A thread for a control channel."""

    def __init__(self, **kwargs):
        """Initialize the thread."""
        super().__init__(name=CONTROL_THREAD_NAME, **kwargs)
```
