# Chunk: fcd61ae4c7b1_1

- source: `.venv-lab/Lib/site-packages/jupyter_client/consoleapp.py`
- lines: 77-167
- chunk: 2/6

```
 "control": "JupyterConsoleApp.control_port",
    "existing": "JupyterConsoleApp.existing",
    "f": "JupyterConsoleApp.connection_file",
    "kernel": "JupyterConsoleApp.kernel_name",
    "ssh": "JupyterConsoleApp.sshserver",
    "sshkey": "JupyterConsoleApp.sshkey",
}
aliases.update(app_aliases)

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

classes: t.List[t.Type[t.Any]] = [KernelManager, KernelRestarter, Session]


class JupyterConsoleApp(ConnectionFileMixin):
    """The base Jupyter console application."""

    name: t.Union[str, Unicode] = "jupyter-console-mixin"

    description: t.Union[str, Unicode] = """
        The Jupyter Console Mixin.

        This class contains the common portions of console client (QtConsole,
        ZMQ-based terminal console, etc).  It is not a full console, in that
        launched terminal subprocesses will not be able to accept input.

        The Console using this mixing supports various extra features beyond
        the single-process Terminal IPython shell, such as connecting to
        existing kernel, via:

            jupyter console <appname> --existing

        as well as tunnel via SSH

    """

    classes = classes
    flags = Dict(flags)
    aliases = Dict(aliases)
    kernel_manager_class = Type(
        default_value=KernelManager,
        config=True,
        help="The kernel manager class to use.",
    )
    kernel_client_class = BlockingKernelClient

    kernel_argv = List(Unicode())

    # connection info:

    sshserver = Unicode("", config=True, help="""The SSH server to use to connect to the kernel.""")
    sshkey = Unicode(
        "",
        config=True,
        help="""Path to the ssh key to use for logging in to the ssh server.""",
    )

    def _connection_file_default(self) -> str:
        return "kernel-%i.json" % os.getpid()

    existing = CUnicode("", config=True, help="""Connect to an already running kernel""")

    kernel_name = Unicode(
        "python", config=True, help="""The name of the default kernel to start."""
    )

    confirm_exit = CBool(
        True,
        config=True,
        help="""
        Set to display confirmation dialog on exit. You can always use 'exit' or 'quit',
        to force a direct exit without any confirmation.""",
    )

    def build_kernel_argv(self, argv: object = None) -> None:
        """build argv to be passed to kernel subprocess

        Override in subclasses if any args should be passed to the kernel
        """
        self.kernel_argv = self.extra_args  # type:ignore[attr-defined]

    def init_connection_file(self) -> None:
        """find the connection file, and load the info if found.

        The current working directory and the current profile's security
        directory will be searched for the file if it is not given by
        absolute path.
```
