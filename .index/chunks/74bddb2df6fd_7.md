# Chunk: 74bddb2df6fd_7

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 512-591
- chunk: 8/33

```
8_high[token]) & 0xFF00) >> 8

        return None

    # Token list contains an address or address range.
    # The prefix is also parsed looking for process and thread IDs.
    def input_full_address_range(self, token_list):
        pid, tid = self.get_process_and_thread_ids_from_prefix()
        address, size = self.input_address_range(token_list, pid, tid)
        return pid, tid, address, size

    # Token list contains a breakpoint.
    def input_breakpoint(self, token_list):
        pid, tid, address, size = self.input_full_address_range(token_list)
        if not self.debug.is_debugee(pid):
            raise CmdError("target process is not being debugged")
        return pid, tid, address, size

    # Token list contains a memory address, and optional size and process.
    # Sets the results as the default for the next display command.
    def input_display(self, token_list, default_size=64):
        pid, tid, address, size = self.input_full_address_range(token_list)
        if not size:
            size = default_size
        next_address = HexOutput.integer(address + size)
        self.default_display_target = next_address
        return pid, tid, address, size

    # ------------------------------------------------------------------------------
    # Output

    # Tell the user a module was loaded.
    def print_module_load(self, event):
        mod = event.get_module()
        base = mod.get_base()
        name = mod.get_filename()
        if not name:
            name = ""
        msg = "Loaded module (%s) %s"
        msg = msg % (HexDump.address(base), name)
        print(msg)

    # Tell the user a module was unloaded.
    def print_module_unload(self, event):
        mod = event.get_module()
        base = mod.get_base()
        name = mod.get_filename()
        if not name:
            name = ""
        msg = "Unloaded module (%s) %s"
        msg = msg % (HexDump.address(base), name)
        print(msg)

    # Tell the user a process was started.
    def print_process_start(self, event):
        pid = event.get_pid()
        start = event.get_start_address()
        if start:
            start = HexOutput.address(start)
            print("Started process %d at %s" % (pid, start))
        else:
            print("Attached to process %d" % pid)

    # Tell the user a thread was started.
    def print_thread_start(self, event):
        tid = event.get_tid()
        start = event.get_start_address()
        if start:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                start = event.get_process().get_label_at_address(start)
            print("Started thread %d at %s" % (tid, start))
        else:
            print("Attached to thread %d" % tid)

    # Tell the user a process has finished.
    def print_process_end(self, event):
        pid = event.get_pid()
        code = event.get_exit_code()
```
