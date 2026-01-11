# Chunk: 74bddb2df6fd_24

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1708-1777
- chunk: 25/33

```
int one-shot
        [~process] bo <address> <size> - make a memory breakpoint one-shot
        """
        token_list = self.split_tokens(arg, 1, 2)
        pid, tid, address, size = self.input_breakpoint(token_list)
        debug = self.debug
        found = False
        if size is None:
            if tid is not None:
                if debug.has_hardware_breakpoint(tid, address):
                    debug.enable_one_shot_hardware_breakpoint(tid, address)
                    found = True
            if pid is not None:
                if debug.has_code_breakpoint(pid, address):
                    debug.enable_one_shot_code_breakpoint(pid, address)
                    found = True
        else:
            if debug.has_page_breakpoint(pid, address):
                debug.enable_one_shot_page_breakpoint(pid, address)
                found = True
        if not found:
            print("Error: breakpoint not found.")

    def do_be(self, arg):
        """
        [~process] be <address> - enable a code breakpoint
        [~thread] be <address> - enable a hardware breakpoint
        [~process] be <address-address> - enable a memory breakpoint
        [~process] be <address> <size> - enable a memory breakpoint
        """
        token_list = self.split_tokens(arg, 1, 2)
        pid, tid, address, size = self.input_breakpoint(token_list)
        debug = self.debug
        found = False
        if size is None:
            if tid is not None:
                if debug.has_hardware_breakpoint(tid, address):
                    debug.enable_hardware_breakpoint(tid, address)
                    found = True
            if pid is not None:
                if debug.has_code_breakpoint(pid, address):
                    debug.enable_code_breakpoint(pid, address)
                    found = True
        else:
            if debug.has_page_breakpoint(pid, address):
                debug.enable_page_breakpoint(pid, address)
                found = True
        if not found:
            print("Error: breakpoint not found.")

    def do_bd(self, arg):
        """
        [~process] bd <address> - disable a code breakpoint
        [~thread] bd <address> - disable a hardware breakpoint
        [~process] bd <address-address> - disable a memory breakpoint
        [~process] bd <address> <size> - disable a memory breakpoint
        """
        token_list = self.split_tokens(arg, 1, 2)
        pid, tid, address, size = self.input_breakpoint(token_list)
        debug = self.debug
        found = False
        if size is None:
            if tid is not None:
                if debug.has_hardware_breakpoint(tid, address):
                    debug.disable_hardware_breakpoint(tid, address)
                    found = True
            if pid is not None:
                if debug.has_code_breakpoint(pid, address):
                    debug.disable_code_breakpoint(pid, address)
```
