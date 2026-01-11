# Chunk: 74bddb2df6fd_4

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 317-395
- chunk: 5/33

```
d = self.input_integer(token)
                if not system.has_thread(tid):
                    raise CmdError("thread not found (%d)" % tid)
                targets.add(tid)
            except ValueError:
                found = set()
                for process in system.iter_processes():
                    found.update(system.find_threads_by_name(token))
                if not found:
                    raise CmdError("thread not found (%s)" % token)
                for thread in found:
                    targets.add(thread.get_tid())
        targets = list(targets)
        targets.sort()
        return targets

    # Token is a process ID or name.
    def input_process(self, token):
        targets = self.input_process_list([token])
        if len(targets) == 0:
            raise CmdError("missing process name or ID")
        if len(targets) > 1:
            msg = "more than one process with that name:\n"
            for pid in targets:
                msg += "\t%d\n" % pid
            msg = msg[: -len("\n")]
            raise CmdError(msg)
        return targets[0]

    # Token list is a list of process IDs or names.
    def input_process_list(self, token_list):
        targets = set()
        system = self.debug.system
        for token in token_list:
            try:
                pid = self.input_integer(token)
                if not system.has_process(pid):
                    raise CmdError("process not found (%d)" % pid)
                targets.add(pid)
            except ValueError:
                found = system.find_processes_by_filename(token)
                if not found:
                    raise CmdError("process not found (%s)" % token)
                for process, _ in found:
                    targets.add(process.get_pid())
        targets = list(targets)
        targets.sort()
        return targets

    # Token is a command line to execute.
    def input_command_line(self, command_line):
        argv = self.debug.system.cmdline_to_argv(command_line)
        if not argv:
            raise CmdError("missing command line to execute")
        fname = argv[0]
        if not os.path.exists(fname):
            try:
                fname, _ = win32.SearchPath(None, fname, ".exe")
            except WindowsError:
                raise CmdError("file not found: %s" % fname)
            argv[0] = fname
            command_line = self.debug.system.argv_to_cmdline(argv)
        return command_line

    # Token is an integer.
    # Only hexadecimal format is supported.
    def input_hexadecimal_integer(self, token):
        return int(token, 0x10)

    # Token is an integer.
    # It can be in any supported format.
    def input_integer(self, token):
        return HexInput.integer(token)

    # #    input_integer = input_hexadecimal_integer

    # Token is an address.
    # The address can be a integer, a label or a register.
```
