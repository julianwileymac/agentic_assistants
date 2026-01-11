# Chunk: 74bddb2df6fd_27

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1908-1972
- chunk: 28/33

```
process(pid)
    # #        for addr, size, data in process.strings():
    # #            print("%s: %r" % (HexDump.address(addr), data)

    def do_d(self, arg):
        """
        [~thread] d <register> - show memory contents
        [~thread] d <register-register> - show memory contents
        [~thread] d <register> <size> - show memory contents
        [~process] d <address> - show memory contents
        [~process] d <address-address> - show memory contents
        [~process] d <address> <size> - show memory contents
        """
        return self.last_display_command(arg)

    def do_db(self, arg):
        """
        [~thread] db <register> - show memory contents as bytes
        [~thread] db <register-register> - show memory contents as bytes
        [~thread] db <register> <size> - show memory contents as bytes
        [~process] db <address> - show memory contents as bytes
        [~process] db <address-address> - show memory contents as bytes
        [~process] db <address> <size> - show memory contents as bytes
        """
        self.print_memory_display(arg, HexDump.hexblock)
        self.last_display_command = self.do_db

    def do_dw(self, arg):
        """
        [~thread] dw <register> - show memory contents as words
        [~thread] dw <register-register> - show memory contents as words
        [~thread] dw <register> <size> - show memory contents as words
        [~process] dw <address> - show memory contents as words
        [~process] dw <address-address> - show memory contents as words
        [~process] dw <address> <size> - show memory contents as words
        """
        self.print_memory_display(arg, HexDump.hexblock_word)
        self.last_display_command = self.do_dw

    def do_dd(self, arg):
        """
        [~thread] dd <register> - show memory contents as dwords
        [~thread] dd <register-register> - show memory contents as dwords
        [~thread] dd <register> <size> - show memory contents as dwords
        [~process] dd <address> - show memory contents as dwords
        [~process] dd <address-address> - show memory contents as dwords
        [~process] dd <address> <size> - show memory contents as dwords
        """
        self.print_memory_display(arg, HexDump.hexblock_dword)
        self.last_display_command = self.do_dd

    def do_dq(self, arg):
        """
        [~thread] dq <register> - show memory contents as qwords
        [~thread] dq <register-register> - show memory contents as qwords
        [~thread] dq <register> <size> - show memory contents as qwords
        [~process] dq <address> - show memory contents as qwords
        [~process] dq <address-address> - show memory contents as qwords
        [~process] dq <address> <size> - show memory contents as qwords
        """
        self.print_memory_display(arg, HexDump.hexblock_qword)
        self.last_display_command = self.do_dq

    # XXX TODO
```
