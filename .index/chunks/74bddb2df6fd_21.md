# Chunk: 74bddb2df6fd_21

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1511-1596
- chunk: 22/33

```
ent:
            current = self.lastEvent.get_pid()
        else:
            current = None
        for pid in targets:
            if pid != current and debug.is_debugee(pid):
                process = system.get_process(pid)
                try:
                    process.debug_break()
                except WindowsError:
                    print("Can't force a debug break on process (%d)")

    def do_step(self, arg):
        """
        p - step on the current assembly instruction
        next - step on the current assembly instruction
        step - step on the current assembly instruction
        """
        if self.cmdprefix:
            raise CmdError("prefix not allowed")
        if self.lastEvent is None:
            raise CmdError("no current process set")
        if arg:  # XXX this check is to be removed
            raise CmdError("too many arguments")
        pid = self.lastEvent.get_pid()
        thread = self.lastEvent.get_thread()
        pc = thread.get_pc()
        code = thread.disassemble(pc, 16)[0]
        size = code[1]
        opcode = code[2].lower()
        if " " in opcode:
            opcode = opcode[: opcode.find(" ")]
        if opcode in self.jump_instructions or opcode in ("int", "ret", "retn"):
            return self.do_trace(arg)
        address = pc + size
        # #        print(hex(pc), hex(address), size   # XXX DEBUG
        self.debug.stalk_at(pid, address)
        return True

    do_p = do_step
    do_next = do_step

    def do_trace(self, arg):
        """
        t - trace at the current assembly instruction
        trace - trace at the current assembly instruction
        """
        if arg:  # XXX this check is to be removed
            raise CmdError("too many arguments")
        if self.lastEvent is None:
            raise CmdError("no current thread set")
        self.lastEvent.get_thread().set_tf()
        return True

    do_t = do_trace

    def do_bp(self, arg):
        """
        [~process] bp <address> - set a code breakpoint
        """
        pid = self.get_process_id_from_prefix()
        if not self.debug.is_debugee(pid):
            raise CmdError("target process is not being debugged")
        process = self.get_process(pid)
        token_list = self.split_tokens(arg, 1, 1)
        try:
            address = self.input_address(token_list[0], pid)
            deferred = False
        except Exception:
            address = token_list[0]
            deferred = True
        if not address:
            address = token_list[0]
            deferred = True
        self.debug.break_at(pid, address)
        if deferred:
            print("Deferred breakpoint set at %s" % address)
        else:
            print("Breakpoint set at %s" % address)

    def do_ba(self, arg):
        """
        [~thread] ba <a|w|e> <1|2|4|8> <address> - set hardware breakpoint
        """
        debug = self.debug
```
