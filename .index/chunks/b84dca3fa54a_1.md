# Chunk: b84dca3fa54a_1

- source: `.venv-lab/Lib/site-packages/jupyter_console/app.py`
- lines: 86-157
- chunk: 2/2

```
examples

    classes = [ZMQTerminalInteractiveShell] + JupyterConsoleApp.classes  # type:ignore[operator]
    flags = Dict(flags)  # type:ignore[assignment]
    aliases = Dict(aliases)  # type:ignore[assignment]
    frontend_aliases = Any(frontend_aliases)
    frontend_flags = Any(frontend_flags)

    subcommands = Dict()

    force_interact = True

    def parse_command_line(self, argv=None):
        super(ZMQTerminalIPythonApp, self).parse_command_line(argv)
        self.build_kernel_argv(self.extra_args)

    def init_shell(self):
        JupyterConsoleApp.initialize(self)
        # relay sigint to kernel
        signal.signal(signal.SIGINT, self.handle_sigint)
        self.shell = ZMQTerminalInteractiveShell.instance(parent=self,
                        manager=self.kernel_manager,
                        client=self.kernel_client,
                        confirm_exit=self.confirm_exit,
        )
        self.shell.own_kernel = not self.existing

    def init_gui_pylab(self):
        # no-op, because we don't want to import matplotlib in the frontend.
        pass

    def handle_sigint(self, *args):
        if self.shell._executing:
            if self.kernel_manager:
                self.kernel_manager.interrupt_kernel()
            else:
                print("ERROR: Cannot interrupt kernels we didn't start.",
                      file = sys.stderr)
        else:
            # raise the KeyboardInterrupt if we aren't waiting for execution,
            # so that the interact loop advances, and prompt is redrawn, etc.
            raise KeyboardInterrupt

    @catch_config_error
    def initialize(self, argv=None):
        """Do actions after construct, but before starting the app."""
        super(ZMQTerminalIPythonApp, self).initialize(argv)
        if self._dispatching:
            return
        # create the shell
        self.init_shell()
        # and draw the banner
        self.init_banner()

    def init_banner(self):
        """optionally display the banner"""
        self.shell.show_banner()

    def start(self):
        # JupyterApp.start dispatches on NoStart
        super(ZMQTerminalIPythonApp, self).start()
        self.log.debug("Starting the jupyter console mainloop...")
        self.shell.mainloop()


main = launch_new_instance = ZMQTerminalIPythonApp.launch_instance


if __name__ == '__main__':
    main()
```
