# Chunk: 74bddb2df6fd_6

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 445-520
- chunk: 7/33

```
address(token, pid, tid)
                size = None
        return address, size

    # XXX TODO
    # Support non-integer registers here.
    def is_register(self, token):
        if win32.arch == "i386":
            if token in self.register_aliases_full_32:
                return True
            token = token.title()
            for name, typ in win32.CONTEXT._fields_:
                if name == token:
                    return win32.sizeof(typ) == win32.sizeof(win32.DWORD)
        elif win32.arch == "amd64":
            if token in self.register_aliases_full_64:
                return True
            token = token.title()
            for name, typ in win32.CONTEXT._fields_:
                if name == token:
                    return win32.sizeof(typ) == win32.sizeof(win32.DWORD64)
        return False

    # The token is a register name.
    # Returns None if no register name is matched.
    def input_register(self, token, tid=None):
        if tid is None:
            if self.lastEvent is None:
                raise CmdError("no current process set")
            thread = self.lastEvent.get_thread()
        else:
            thread = self.debug.system.get_thread(tid)
        ctx = thread.get_context()

        token = token.lower()
        title = token.title()

        if title in ctx:
            return ctx.get(title)  # eax -> Eax

        if ctx.arch == "i386":
            if token in self.segment_names:
                return ctx.get("Seg%s" % title)  # cs -> SegCs

            if token in self.register_alias_32_to_16:
                return ctx.get(self.register_alias_32_to_16[token]) & 0xFFFF

            if token in self.register_alias_32_to_8_low:
                return ctx.get(self.register_alias_32_to_8_low[token]) & 0xFF

            if token in self.register_alias_32_to_8_high:
                return (ctx.get(self.register_alias_32_to_8_high[token]) & 0xFF00) >> 8

        elif ctx.arch == "amd64":
            if token in self.segment_names:
                return ctx.get("Seg%s" % title)  # cs -> SegCs

            if token in self.register_alias_64_to_32:
                return ctx.get(self.register_alias_64_to_32[token]) & 0xFFFFFFFF

            if token in self.register_alias_64_to_16:
                return ctx.get(self.register_alias_64_to_16[token]) & 0xFFFF

            if token in self.register_alias_64_to_8_low:
                return ctx.get(self.register_alias_64_to_8_low[token]) & 0xFF

            if token in self.register_alias_64_to_8_high:
                return (ctx.get(self.register_alias_64_to_8_high[token]) & 0xFF00) >> 8

        return None

    # Token list contains an address or address range.
    # The prefix is also parsed looking for process and thread IDs.
    def input_full_address_range(self, token_list):
        pid, tid = self.get_process_and_thread_ids_from_prefix()
```
