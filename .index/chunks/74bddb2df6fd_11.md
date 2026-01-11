# Chunk: 74bddb2df6fd_11

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 795-871
- chunk: 12/33

```
.get_process(pid)
        try:
            data = process.peek(address, size)
        except WindowsError:
            orig_address = HexOutput.integer(address)
            next_address = HexOutput.integer(address + size)
            msg = "error reading process %d, from %s to %s (%d bytes)"
            msg = msg % (pid, orig_address, next_address, size)
            raise CmdError(msg)
        return data

    # Write the process memory.
    def write_memory(self, address, data, pid=None):
        process = self.get_process(pid)
        try:
            process.write(address, data)
        except WindowsError:
            size = len(data)
            orig_address = HexOutput.integer(address)
            next_address = HexOutput.integer(address + size)
            msg = "error reading process %d, from %s to %s (%d bytes)"
            msg = msg % (pid, orig_address, next_address, size)
            raise CmdError(msg)

    # Change a register value.
    def change_register(self, register, value, tid=None):
        # Get the thread.
        if tid is None:
            if self.lastEvent is None:
                raise CmdError("no current process set")
            thread = self.lastEvent.get_thread()
        else:
            try:
                thread = self.debug.system.get_thread(tid)
            except KeyError:
                raise CmdError("thread not found (%d)" % tid)

        # Convert the value to integer type.
        try:
            value = self.input_integer(value)
        except ValueError:
            pid = thread.get_pid()
            value = self.input_address(value, pid, tid)

        # Suspend the thread.
        # The finally clause ensures the thread is resumed before returning.
        thread.suspend()
        try:
            # Get the current context.
            ctx = thread.get_context()

            # Register name matching is case insensitive.
            register = register.lower()

            # Integer 32 bits registers.
            if register in self.register_names:
                register = register.title()  # eax -> Eax

            # Segment (16 bit) registers.
            if register in self.segment_names:
                register = "Seg%s" % register.title()  # cs -> SegCs
                value = value & 0x0000FFFF

            # Integer 16 bits registers.
            if register in self.register_alias_16:
                register = self.register_alias_16[register]
                previous = ctx.get(register) & 0xFFFF0000
                value = (value & 0x0000FFFF) | previous

            # Integer 8 bits registers (low part).
            if register in self.register_alias_8_low:
                register = self.register_alias_8_low[register]
                previous = ctx.get(register) % 0xFFFFFF00
                value = (value & 0x000000FF) | previous

            # Integer 8 bits registers (high part).
```
