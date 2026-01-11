# Chunk: cc4c3c8aea41_2

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/kernels/kernelmanager.py`
- lines: 173-238
- chunk: 3/14

```
"""White list of allowed kernel message types.
        When the list is empty, all message types are allowed.
        """,
    )

    allow_tracebacks = Bool(
        True, config=True, help=("Whether to send tracebacks to clients on exceptions.")
    )

    traceback_replacement_message = Unicode(
        "An exception occurred at runtime, which is not shown due to security reasons.",
        config=True,
        help=("Message to print when allow_tracebacks is False, and an exception occurs"),
    )

    # -------------------------------------------------------------------------
    # Methods for managing kernels and sessions
    # -------------------------------------------------------------------------

    def _handle_kernel_died(self, kernel_id):
        """notice that a kernel died"""
        self.log.warning("Kernel %s died, removing from map.", kernel_id)
        self.remove_kernel(kernel_id)

    def cwd_for_path(self, path, **kwargs):
        """Turn API path into absolute OS path."""
        os_path = to_os_path(path, self.root_dir)
        # in the case of documents and kernels not being on the same filesystem,
        # walk up to root_dir if the paths don't exist
        while not os.path.isdir(os_path) and os_path != self.root_dir:
            os_path = os.path.dirname(os_path)
        return os_path

    async def _remove_kernel_when_ready(self, kernel_id, kernel_awaitable):
        """Remove a kernel when it is ready."""
        await super()._remove_kernel_when_ready(kernel_id, kernel_awaitable)
        self._kernel_connections.pop(kernel_id, None)
        self._kernel_ports.pop(kernel_id, None)

    # TODO: DEC 2022: Revise the type-ignore once the signatures have been changed upstream
    # https://github.com/jupyter/jupyter_client/pull/905
    async def _async_start_kernel(  # type:ignore[override]
        self, *, kernel_id: str | None = None, path: ApiPath | None = None, **kwargs: str
    ) -> str:
        """Start a kernel for a session and return its kernel_id.

        Parameters
        ----------
        kernel_id : uuid (str)
            The uuid to associate the new kernel with. If this
            is not None, this kernel will be persistent whenever it is
            requested.
        path : API path
            The API path (unicode, '/' delimited) for the cwd.
            Will be transformed to an OS path relative to root_dir.
        kernel_name : str
            The name identifying which kernel spec to launch. This is ignored if
            an existing kernel is returned, but it may be checked in the future.
        """
        if kernel_id is None or kernel_id not in self:
            if path is not None:
                kwargs["cwd"] = self.cwd_for_path(path, env=kwargs.get("env", {}))
            if kernel_id is not None:
                assert kernel_id is not None, "Never Fail, but necessary for mypy "
                kwargs["kernel_id"] = kernel_id
```
