# Chunk: 74bddb2df6fd_28

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1964-2038
- chunk: 29/33

```
s qwords
        [~process] dq <address-address> - show memory contents as qwords
        [~process] dq <address> <size> - show memory contents as qwords
        """
        self.print_memory_display(arg, HexDump.hexblock_qword)
        self.last_display_command = self.do_dq

    # XXX TODO
    # Change the way the default is used with ds and du

    def do_ds(self, arg):
        """
        [~thread] ds <register> - show memory contents as ANSI string
        [~process] ds <address> - show memory contents as ANSI string
        """
        if not arg:
            arg = self.default_display_target
        token_list = self.split_tokens(arg, 1, 1)
        pid, tid, address, size = self.input_display(token_list, 256)
        process = self.get_process(pid)
        data = process.peek_string(address, False, size)
        if data:
            print(repr(data))
        self.last_display_command = self.do_ds

    def do_du(self, arg):
        """
        [~thread] du <register> - show memory contents as Unicode string
        [~process] du <address> - show memory contents as Unicode string
        """
        if not arg:
            arg = self.default_display_target
        token_list = self.split_tokens(arg, 1, 2)
        pid, tid, address, size = self.input_display(token_list, 256)
        process = self.get_process(pid)
        data = process.peek_string(address, True, size)
        if data:
            print(repr(data))
        self.last_display_command = self.do_du

    def do_register(self, arg):
        """
        [~thread] r - print(the value of all registers
        [~thread] r <register> - print(the value of a register
        [~thread] r <register>=<value> - change the value of a register
        [~thread] register - print(the value of all registers
        [~thread] register <register> - print(the value of a register
        [~thread] register <register>=<value> - change the value of a register
        """
        arg = arg.strip()
        if not arg:
            self.print_current_location()
        else:
            equ = arg.find("=")
            if equ >= 0:
                register = arg[:equ].strip()
                value = arg[equ + 1 :].strip()
                if not value:
                    value = "0"
                self.change_register(register, value)
            else:
                value = self.input_register(arg)
                if value is None:
                    raise CmdError("unknown register: %s" % arg)
                try:
                    label = None
                    thread = self.get_thread_from_prefix()
                    process = thread.get_process()
                    module = process.get_module_at_address(value)
                    if module:
                        label = module.get_label_at_address(value)
                except RuntimeError:
                    label = None
                reg = arg.upper()
```
