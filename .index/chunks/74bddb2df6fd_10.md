# Chunk: 74bddb2df6fd_10

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 727-802
- chunk: 11/33

```
process_from_prefix(self):
        pid = self.get_process_id_from_prefix()
        return self.get_process(pid)

    # Get the thread from the prefix or the last event.
    def get_thread_from_prefix(self):
        tid = self.get_thread_id_from_prefix()
        return self.get_thread(tid)

    # Get the process and thread IDs from the prefix or the last event.
    def get_process_and_thread_ids_from_prefix(self):
        if self.cmdprefix:
            try:
                pid = self.input_process(self.cmdprefix)
                tid = None
            except CmdError:
                try:
                    tid = self.input_thread(self.cmdprefix)
                    pid = self.debug.system.get_thread(tid).get_pid()
                except CmdError:
                    msg = "unknown process or thread (%s)" % self.cmdprefix
                    raise CmdError(msg)
        else:
            if self.lastEvent is None:
                raise CmdError("no current process set")
            pid = self.lastEvent.get_pid()
            tid = self.lastEvent.get_tid()
        return pid, tid

    # Get the process and thread from the prefix or the last event.
    def get_process_and_thread_from_prefix(self):
        pid, tid = self.get_process_and_thread_ids_from_prefix()
        process = self.get_process(pid)
        thread = self.get_thread(tid)
        return process, thread

    # Get the process object.
    def get_process(self, pid=None):
        if pid is None:
            if self.lastEvent is None:
                raise CmdError("no current process set")
            process = self.lastEvent.get_process()
        elif self.lastEvent is not None and pid == self.lastEvent.get_pid():
            process = self.lastEvent.get_process()
        else:
            try:
                process = self.debug.system.get_process(pid)
            except KeyError:
                raise CmdError("process not found (%d)" % pid)
        return process

    # Get the thread object.
    def get_thread(self, tid=None):
        if tid is None:
            if self.lastEvent is None:
                raise CmdError("no current process set")
            thread = self.lastEvent.get_thread()
        elif self.lastEvent is not None and tid == self.lastEvent.get_tid():
            thread = self.lastEvent.get_thread()
        else:
            try:
                thread = self.debug.system.get_thread(tid)
            except KeyError:
                raise CmdError("thread not found (%d)" % tid)
        return thread

    # Read the process memory.
    def read_memory(self, address, size, pid=None):
        process = self.get_process(pid)
        try:
            data = process.peek(address, size)
        except WindowsError:
            orig_address = HexOutput.integer(address)
            next_address = HexOutput.integer(address + size)
            msg = "error reading process %d, from %s to %s (%d bytes)"
```
