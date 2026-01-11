# Chunk: 74bddb2df6fd_20

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1443-1520
- chunk: 21/33

```
_pid():
                        msg = "You are about to kill the current process."
                    else:
                        msg = "You are about to kill process %d." % pid
                    if self.ask_user(msg):
                        self.kill_process(pid)
                else:
                    if self.lastEvent is not None and tid == self.lastEvent.get_tid():
                        msg = "You are about to kill the current thread."
                    else:
                        msg = "You are about to kill thread %d." % tid
                    if self.ask_user(msg):
                        self.kill_thread(tid)
            else:
                if self.lastEvent is None:
                    raise CmdError("no current process set")
                pid = self.lastEvent.get_pid()
                if self.ask_user("You are about to kill the current process."):
                    self.kill_process(pid)

    # TODO: create hidden threads using undocumented API calls.
    def do_modload(self, arg):
        """
        [~process] modload <filename.dll> - load a DLL module
        """
        filename = self.split_tokens(arg, 1, 1)[0]
        process = self.get_process_from_prefix()
        try:
            process.inject_dll(filename, bWait=False)
        except RuntimeError:
            print("Can't inject module: %r" % filename)

    # TODO: modunload

    def do_stack(self, arg):
        """
        [~thread] k - show the stack trace
        [~thread] stack - show the stack trace
        """
        if arg:  # XXX TODO add depth parameter
            raise CmdError("too many arguments")
        pid, tid = self.get_process_and_thread_ids_from_prefix()
        process = self.get_process(pid)
        thread = process.get_thread(tid)
        try:
            stack_trace = thread.get_stack_trace_with_labels()
            if stack_trace:
                print(
                    CrashDump.dump_stack_trace_with_labels(stack_trace),
                )
            else:
                print("No stack trace available for thread (%d)" % tid)
        except WindowsError:
            print("Can't get stack trace for thread (%d)" % tid)

    do_k = do_stack

    def do_break(self, arg):
        """
        break - force a debug break in all debugees
        break <process> [process...] - force a debug break
        """
        debug = self.debug
        system = debug.system
        targets = self.input_process_list(self.split_tokens(arg))
        if not targets:
            targets = debug.get_debugee_pids()
            targets.sort()
        if self.lastEvent:
            current = self.lastEvent.get_pid()
        else:
            current = None
        for pid in targets:
            if pid != current and debug.is_debugee(pid):
                process = system.get_process(pid)
                try:
                    process.debug_break()
```
