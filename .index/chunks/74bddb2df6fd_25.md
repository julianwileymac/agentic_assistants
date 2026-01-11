# Chunk: 74bddb2df6fd_25

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1771-1840
- chunk: 26/33

```
s_hardware_breakpoint(tid, address):
                    debug.disable_hardware_breakpoint(tid, address)
                    found = True
            if pid is not None:
                if debug.has_code_breakpoint(pid, address):
                    debug.disable_code_breakpoint(pid, address)
                    found = True
        else:
            if debug.has_page_breakpoint(pid, address):
                debug.disable_page_breakpoint(pid, address)
                found = True
        if not found:
            print("Error: breakpoint not found.")

    def do_bc(self, arg):
        """
        [~process] bc <address> - clear a code breakpoint
        [~thread] bc <address> - clear a hardware breakpoint
        [~process] bc <address-address> - clear a memory breakpoint
        [~process] bc <address> <size> - clear a memory breakpoint
        """
        token_list = self.split_tokens(arg, 1, 2)
        pid, tid, address, size = self.input_breakpoint(token_list)
        debug = self.debug
        found = False
        if size is None:
            if tid is not None:
                if debug.has_hardware_breakpoint(tid, address):
                    debug.dont_watch_variable(tid, address)
                    found = True
            if pid is not None:
                if debug.has_code_breakpoint(pid, address):
                    debug.dont_break_at(pid, address)
                    found = True
        else:
            if debug.has_page_breakpoint(pid, address):
                debug.dont_watch_buffer(pid, address, size)
                found = True
        if not found:
            print("Error: breakpoint not found.")

    def do_disassemble(self, arg):
        """
        [~thread] u [register] - show code disassembly
        [~process] u [address] - show code disassembly
        [~thread] disassemble [register] - show code disassembly
        [~process] disassemble [address] - show code disassembly
        """
        if not arg:
            arg = self.default_disasm_target
        token_list = self.split_tokens(arg, 1, 1)
        pid, tid = self.get_process_and_thread_ids_from_prefix()
        process = self.get_process(pid)
        address = self.input_address(token_list[0], pid, tid)
        try:
            code = process.disassemble(address, 15 * 8)[:8]
        except Exception:
            msg = "can't disassemble address %s"
            msg = msg % HexDump.address(address)
            raise CmdError(msg)
        if code:
            label = process.get_label_at_address(address)
            last_code = code[-1]
            next_address = last_code[0] + last_code[1]
            next_address = HexOutput.integer(next_address)
            self.default_disasm_target = next_address
            print("%s:" % label)
            # #            print(CrashDump.dump_code(code))
            for line in code:
```
