# Chunk: 74bddb2df6fd_5

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 384-455
- chunk: 6/33

```
10)

    # Token is an integer.
    # It can be in any supported format.
    def input_integer(self, token):
        return HexInput.integer(token)

    # #    input_integer = input_hexadecimal_integer

    # Token is an address.
    # The address can be a integer, a label or a register.
    def input_address(self, token, pid=None, tid=None):
        address = None
        if self.is_register(token):
            if tid is None:
                if self.lastEvent is None or pid != self.lastEvent.get_pid():
                    msg = "can't resolve register (%s) for unknown thread"
                    raise CmdError(msg % token)
                tid = self.lastEvent.get_tid()
            address = self.input_register(token, tid)
        if address is None:
            try:
                address = self.input_hexadecimal_integer(token)
            except ValueError:
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
                try:
                    address = process.resolve_label(token)
                except Exception:
                    raise CmdError("unknown address (%s)" % token)
        return address

    # Token is an address range, or a single address.
    # The addresses can be integers, labels or registers.
    def input_address_range(self, token_list, pid=None, tid=None):
        if len(token_list) == 2:
            token_1, token_2 = token_list
            address = self.input_address(token_1, pid, tid)
            try:
                size = self.input_integer(token_2)
            except ValueError:
                raise CmdError("bad address range: %s %s" % (token_1, token_2))
        elif len(token_list) == 1:
            token = token_list[0]
            if "-" in token:
                try:
                    token_1, token_2 = token.split("-")
                except Exception:
                    raise CmdError("bad address range: %s" % token)
                address = self.input_address(token_1, pid, tid)
                size = self.input_address(token_2, pid, tid) - address
            else:
                address = self.input_address(token, pid, tid)
                size = None
        return address, size

    # XXX TODO
    # Support non-integer registers here.
    def is_register(self, token):
        if win32.arch == "i386":
            if token in self.register_aliases_full_32:
                return True
```
