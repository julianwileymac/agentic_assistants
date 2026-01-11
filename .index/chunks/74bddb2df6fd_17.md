# Chunk: 74bddb2df6fd_17

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1230-1314
- chunk: 18/33

```
 not targets:
            print("Error: missing parameters")
        else:
            debug = self.debug
            for pid in targets:
                try:
                    debug.attach(pid)
                    print("Attached to process (%d)" % pid)
                except Exception:
                    print("Error: can't attach to process (%d)" % pid)

    def do_detach(self, arg):
        """
        [~process] detach - detach from the current process
        detach - detach from the current process
        detach <target> [target...] - detach from the given process(es)
        """
        debug = self.debug
        token_list = self.split_tokens(arg)
        if self.cmdprefix:
            token_list.insert(0, self.cmdprefix)
        targets = self.input_process_list(token_list)
        if not targets:
            if self.lastEvent is None:
                raise CmdError("no current process set")
            targets = [self.lastEvent.get_pid()]
        for pid in targets:
            try:
                debug.detach(pid)
                print("Detached from process (%d)" % pid)
            except Exception:
                print("Error: can't detach from process (%d)" % pid)

    def do_windowed(self, arg):
        """
        windowed <target> [arguments...] - run a windowed program for debugging
        """
        if self.cmdprefix:
            raise CmdError("prefix not allowed")
        cmdline = self.input_command_line(arg)
        try:
            process = self.debug.execl(arg, bConsole=False, bFollow=self.options.follow)
            print("Spawned process (%d)" % process.get_pid())
        except Exception:
            raise CmdError("can't execute")
        self.set_fake_last_event(process)

    def do_console(self, arg):
        """
        console <target> [arguments...] - run a console program for debugging
        """
        if self.cmdprefix:
            raise CmdError("prefix not allowed")
        cmdline = self.input_command_line(arg)
        try:
            process = self.debug.execl(arg, bConsole=True, bFollow=self.options.follow)
            print("Spawned process (%d)" % process.get_pid())
        except Exception:
            raise CmdError("can't execute")
        self.set_fake_last_event(process)

    def do_continue(self, arg):
        """
        continue - continue execution
        g - continue execution
        go - continue execution
        """
        if self.cmdprefix:
            raise CmdError("prefix not allowed")
        if arg:
            raise CmdError("too many arguments")
        if self.debug.get_debugee_count() > 0:
            return True

    do_g = do_continue
    do_go = do_continue

    def do_gh(self, arg):
        """
        gh - go with exception handled
        """
        if self.cmdprefix:
            raise CmdError("prefix not allowed")
        if arg:
```
