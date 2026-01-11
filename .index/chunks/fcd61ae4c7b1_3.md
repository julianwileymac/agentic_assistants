# Chunk: fcd61ae4c7b1_3

- source: `.venv-lab/Lib/site-packages/jupyter_client/consoleapp.py`
- lines: 220-299
- chunk: 4/6

```
f not self.existing or (not self.sshserver and not self.sshkey):
            return
        self.load_connection_file()

        transport = self.transport
        ip = self.ip

        if transport != "tcp":
            self.log.error("Can only use ssh tunnels with TCP sockets, not %s", transport)
            sys.exit(-1)

        if self.sshkey and not self.sshserver:
            # specifying just the key implies that we are connecting directly
            self.sshserver = ip
            ip = localhost()

        # build connection dict for tunnels:
        info: KernelConnectionInfo = {
            "ip": ip,
            "shell_port": self.shell_port,
            "iopub_port": self.iopub_port,
            "stdin_port": self.stdin_port,
            "hb_port": self.hb_port,
            "control_port": self.control_port,
        }

        self.log.info("Forwarding connections to %s via %s", ip, self.sshserver)

        # tunnels return a new set of ports, which will be on localhost:
        self.ip = localhost()
        try:
            newports = tunnel_to_kernel(info, self.sshserver, self.sshkey)
        except:  # noqa
            # even catch KeyboardInterrupt
            self.log.error("Could not setup tunnels", exc_info=True)
            self.exit(1)  # type:ignore[attr-defined]

        (
            self.shell_port,
            self.iopub_port,
            self.stdin_port,
            self.hb_port,
            self.control_port,
        ) = newports

        cf = self.connection_file
        root, ext = os.path.splitext(cf)
        self.connection_file = root + "-ssh" + ext
        self.write_connection_file()  # write the new connection file
        self.log.info("To connect another client via this tunnel, use:")
        self.log.info("--existing %s", os.path.basename(self.connection_file))

    def _new_connection_file(self) -> str:
        cf = ""
        while not cf:
            # we don't need a 128b id to distinguish kernels, use more readable
            # 48b node segment (12 hex chars).  Users running more than 32k simultaneous
            # kernels can subclass.
            ident = str(uuid.uuid4()).split("-")[-1]
            runtime_dir = self.runtime_dir  # type:ignore[attr-defined]
            cf = os.path.join(runtime_dir, "kernel-%s.json" % ident)
            # only keep if it's actually new.  Protect against unlikely collision
            # in 48b random search space
            cf = cf if not os.path.exists(cf) else ""
        return cf

    def init_kernel_manager(self) -> None:
        """Initialize the kernel manager."""
        # Don't let Qt or ZMQ swallow KeyboardInterupts.
        if self.existing:
            self.kernel_manager = None
            return
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # Create a KernelManager and start a kernel.
        try:
            self.kernel_manager = self.kernel_manager_class(
                ip=self.ip,
                session=self.session,
```
