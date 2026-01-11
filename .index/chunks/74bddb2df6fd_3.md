# Chunk: 74bddb2df6fd_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 252-324
- chunk: 4/33

```
y the Debug object.
    def destroy_debugger(self, autodetach=True):
        debug = self.stop_using_debugger()
        if debug is not None:
            if not autodetach:
                debug.kill_all(bIgnoreExceptions=True)
                debug.lastEvent = None
            debug.stop()
        del debug

    @property
    def lastEvent(self):
        return self.debug.lastEvent

    def set_fake_last_event(self, process):
        if self.lastEvent is None:
            self.debug.lastEvent = DummyEvent(self.debug)
            self.debug.lastEvent._process = process
            self.debug.lastEvent._thread = process.get_thread(process.get_thread_ids()[0])
            self.debug.lastEvent._pid = process.get_pid()
            self.debug.lastEvent._tid = self.lastEvent._thread.get_tid()

    # ------------------------------------------------------------------------------
    # Input

    # TODO
    # * try to guess breakpoints when insufficient data is given
    # * child Cmd instances will have to be used for other prompts, for example
    #   when assembling or editing memory - it may also be a good idea to think
    #   if it's possible to make the main Cmd instance also a child, instead of
    #   the debugger itself - probably the same goes for the EventHandler, maybe
    #   it can be used as a contained object rather than a parent class.

    # Join a token list into an argument string.
    def join_tokens(self, token_list):
        return self.debug.system.argv_to_cmdline(token_list)

    # Split an argument string into a token list.
    def split_tokens(self, arg, min_count=0, max_count=None):
        token_list = self.debug.system.cmdline_to_argv(arg)
        if len(token_list) < min_count:
            raise CmdError("missing parameters.")
        if max_count and len(token_list) > max_count:
            raise CmdError("too many parameters.")
        return token_list

    # Token is a thread ID or name.
    def input_thread(self, token):
        targets = self.input_thread_list([token])
        if len(targets) == 0:
            raise CmdError("missing thread name or ID")
        if len(targets) > 1:
            msg = "more than one thread with that name:\n"
            for tid in targets:
                msg += "\t%d\n" % tid
            msg = msg[: -len("\n")]
            raise CmdError(msg)
        return targets[0]

    # Token list is a list of thread IDs or names.
    def input_thread_list(self, token_list):
        targets = set()
        system = self.debug.system
        for token in token_list:
            try:
                tid = self.input_integer(token)
                if not system.has_thread(tid):
                    raise CmdError("thread not found (%d)" % tid)
                targets.add(tid)
            except ValueError:
                found = set()
                for process in system.iter_processes():
```
