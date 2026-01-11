# Chunk: 74bddb2df6fd_9

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 652-736
- chunk: 10/33

```
 set")
            process = self.lastEvent.get_process()
        if not thread:
            if self.lastEvent is None:
                raise CmdError("no current process set")
            thread = self.lastEvent.get_thread()
        thread.suspend()
        try:
            if pc is None:
                pc = thread.get_pc()
            ctx = thread.get_context()
        finally:
            thread.resume()
        label = process.get_label_at_address(pc)
        try:
            disasm = process.disassemble(pc, 15)
        except WindowsError:
            disasm = None
        except NotImplementedError:
            disasm = None
        print("")
        print(
            CrashDump.dump_registers(ctx),
        )
        print("%s:" % label)
        if disasm:
            print(CrashDump.dump_code_line(disasm[0], pc, bShowDump=True))
        else:
            try:
                data = process.peek(pc, 15)
            except Exception:
                data = None
            if data:
                print("%s: %s" % (HexDump.address(pc), HexDump.hexblock_byte(data)))
            else:
                print("%s: ???" % HexDump.address(pc))

    # Display memory contents using a given method.
    def print_memory_display(self, arg, method):
        if not arg:
            arg = self.default_display_target
        token_list = self.split_tokens(arg, 1, 2)
        pid, tid, address, size = self.input_display(token_list)
        label = self.get_process(pid).get_label_at_address(address)
        data = self.read_memory(address, size, pid)
        if data:
            print("%s:" % label)
            print(
                method(data, address),
            )

    # ------------------------------------------------------------------------------
    # Debugging

    # Get the process ID from the prefix or the last event.
    def get_process_id_from_prefix(self):
        if self.cmdprefix:
            pid = self.input_process(self.cmdprefix)
        else:
            if self.lastEvent is None:
                raise CmdError("no current process set")
            pid = self.lastEvent.get_pid()
        return pid

    # Get the thread ID from the prefix or the last event.
    def get_thread_id_from_prefix(self):
        if self.cmdprefix:
            tid = self.input_thread(self.cmdprefix)
        else:
            if self.lastEvent is None:
                raise CmdError("no current process set")
            tid = self.lastEvent.get_tid()
        return tid

    # Get the process from the prefix or the last event.
    def get_process_from_prefix(self):
        pid = self.get_process_id_from_prefix()
        return self.get_process(pid)

    # Get the thread from the prefix or the last event.
    def get_thread_from_prefix(self):
        tid = self.get_thread_id_from_prefix()
        return self.get_thread(tid)

```
