# Chunk: fcd61ae4c7b1_4

- source: `.venv-lab/Lib/site-packages/jupyter_client/consoleapp.py`
- lines: 290-367
- chunk: 5/6

```
       self.kernel_manager = None
            return
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # Create a KernelManager and start a kernel.
        try:
            self.kernel_manager = self.kernel_manager_class(
                ip=self.ip,
                session=self.session,
                transport=self.transport,
                shell_port=self.shell_port,
                iopub_port=self.iopub_port,
                stdin_port=self.stdin_port,
                hb_port=self.hb_port,
                control_port=self.control_port,
                connection_file=self.connection_file,
                kernel_name=self.kernel_name,
                parent=self,
                data_dir=self.data_dir,
            )
            # access kernel_spec to ensure the NoSuchKernel error is raised
            # if it's going to be
            kernel_spec = self.kernel_manager.kernel_spec  # noqa: F841
        except NoSuchKernel:
            self.log.critical("Could not find kernel %r", self.kernel_name)
            self.exit(1)  # type:ignore[attr-defined]

        self.kernel_manager = t.cast(KernelManager, self.kernel_manager)
        self.kernel_manager.client_factory = self.kernel_client_class
        kwargs = {}
        kwargs["extra_arguments"] = self.kernel_argv
        self.kernel_manager.start_kernel(**kwargs)
        atexit.register(self.kernel_manager.cleanup_ipc_files)

        if self.sshserver:
            # ssh, write new connection file
            self.kernel_manager.write_connection_file()

        # in case KM defaults / ssh writing changes things:
        km = self.kernel_manager
        self.shell_port = km.shell_port
        self.iopub_port = km.iopub_port
        self.stdin_port = km.stdin_port
        self.hb_port = km.hb_port
        self.control_port = km.control_port
        self.connection_file = km.connection_file

        atexit.register(self.kernel_manager.cleanup_connection_file)

    def init_kernel_client(self) -> None:
        """Initialize the kernel client."""
        if self.kernel_manager is not None:
            self.kernel_client = self.kernel_manager.client()
        else:
            self.kernel_client = self.kernel_client_class(
                session=self.session,
                ip=self.ip,
                transport=self.transport,
                shell_port=self.shell_port,
                iopub_port=self.iopub_port,
                stdin_port=self.stdin_port,
                hb_port=self.hb_port,
                control_port=self.control_port,
                connection_file=self.connection_file,
                parent=self,
            )

        self.kernel_client.start_channels()

    def initialize(self, argv: object = None) -> None:
        """
        Classes which mix this class in should call:
               JupyterConsoleApp.initialize(self,argv)
        """
        if getattr(self, "_dispatching", False):
            return
        self.init_connection_file()
```
