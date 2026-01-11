# Chunk: 5f7ce3ece3ce_0

- source: `.venv-lab/Lib/site-packages/ipykernel/thread.py`
- lines: 1-34
- chunk: 1/1

```
"""Base class for threads."""

from threading import Thread

from tornado.ioloop import IOLoop

CONTROL_THREAD_NAME = "Control"
SHELL_CHANNEL_THREAD_NAME = "Shell channel"


class BaseThread(Thread):
    """Base class for threads."""

    def __init__(self, **kwargs):
        """Initialize the thread."""
        super().__init__(**kwargs)
        self.io_loop = IOLoop(make_current=False)
        self.pydev_do_not_trace = True
        self.is_pydev_daemon_thread = True

    def run(self) -> None:
        """Run the thread."""
        try:
            self.io_loop.start()
        finally:
            self.io_loop.close()

    def stop(self) -> None:
        """Stop the thread.

        This method is threadsafe.
        """
        self.io_loop.add_callback(self.io_loop.stop)
```
