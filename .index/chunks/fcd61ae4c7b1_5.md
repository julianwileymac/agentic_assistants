# Chunk: fcd61ae4c7b1_5

- source: `.venv-lab/Lib/site-packages/jupyter_client/consoleapp.py`
- lines: 357-379
- chunk: 6/6

```
nnels()

    def initialize(self, argv: object = None) -> None:
        """
        Classes which mix this class in should call:
               JupyterConsoleApp.initialize(self,argv)
        """
        if getattr(self, "_dispatching", False):
            return
        self.init_connection_file()
        self.init_ssh()
        self.init_kernel_manager()
        self.init_kernel_client()


class IPythonConsoleApp(JupyterConsoleApp):
    """An app to manage an ipython console."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """Initialize the app."""
        warnings.warn("IPythonConsoleApp is deprecated. Use JupyterConsoleApp", stacklevel=2)
        super().__init__(*args, **kwargs)
```
