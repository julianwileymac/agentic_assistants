# Chunk: 74bddb2df6fd_8

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 582-661
- chunk: 9/33

```
_address(start)
            print("Started thread %d at %s" % (tid, start))
        else:
            print("Attached to thread %d" % tid)

    # Tell the user a process has finished.
    def print_process_end(self, event):
        pid = event.get_pid()
        code = event.get_exit_code()
        print("Process %d terminated, exit code %d" % (pid, code))

    # Tell the user a thread has finished.
    def print_thread_end(self, event):
        tid = event.get_tid()
        code = event.get_exit_code()
        print("Thread %d terminated, exit code %d" % (tid, code))

    # Print(debug strings.
    def print_debug_string(self, event):
        tid = event.get_tid()
        string = event.get_debug_string()
        print("Thread %d says: %r" % (tid, string))

    # Inform the user of any other debugging event.
    def print_event(self, event):
        code = HexDump.integer(event.get_event_code())
        name = event.get_event_name()
        desc = event.get_event_description()
        if code in desc:
            print("")
            print("%s: %s" % (name, desc))
        else:
            print("")
            print("%s (%s): %s" % (name, code, desc))
        self.print_event_location(event)

    # Stop on exceptions and prompt for commands.
    def print_exception(self, event):
        address = HexDump.address(event.get_exception_address())
        code = HexDump.integer(event.get_exception_code())
        desc = event.get_exception_description()
        if event.is_first_chance():
            chance = "first"
        else:
            chance = "second"
        if code in desc:
            msg = "%s at address %s (%s chance)" % (desc, address, chance)
        else:
            msg = "%s (%s) at address %s (%s chance)" % (desc, code, address, chance)
        print("")
        print(msg)
        self.print_event_location(event)

    # Show the current location in the code.
    def print_event_location(self, event):
        process = event.get_process()
        thread = event.get_thread()
        self.print_current_location(process, thread)

    # Show the current location in the code.
    def print_breakpoint_location(self, event):
        process = event.get_process()
        thread = event.get_thread()
        pc = event.get_exception_address()
        self.print_current_location(process, thread, pc)

    # Show the current location in any process and thread.
    def print_current_location(self, process=None, thread=None, pc=None):
        if not process:
            if self.lastEvent is None:
                raise CmdError("no current process set")
            process = self.lastEvent.get_process()
        if not thread:
            if self.lastEvent is None:
                raise CmdError("no current process set")
            thread = self.lastEvent.get_thread()
        thread.suspend()
        try:
            if pc is None:
```
