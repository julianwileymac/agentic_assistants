# Chunk: 4e9bd49cabbf_55

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 4124-4207
- chunk: 56/64

```
variable} and L{stalk_variable}.

        @type  tid: int
        @param tid: Thread global ID.

        @type  address: int
        @param address: Memory address of variable to watch.

        @type  size: int
        @param size: Size of variable to watch. The only supported sizes are:
            byte (1), word (2), dword (4) and qword (8).

        @type  action: function
        @param action: (Optional) Action callback function.

            See L{define_hardware_breakpoint} for more details.

        @rtype:  L{HardwareBreakpoint}
        @return: Hardware breakpoint at the requested address.
        """

        # TODO
        # We should merge the breakpoints instead of overwriting them.
        # We'll have the same problem as watch_buffer and we'll need to change
        # the API again.

        if size == 1:
            sizeFlag = self.BP_WATCH_BYTE
        elif size == 2:
            sizeFlag = self.BP_WATCH_WORD
        elif size == 4:
            sizeFlag = self.BP_WATCH_DWORD
        elif size == 8:
            sizeFlag = self.BP_WATCH_QWORD
        else:
            raise ValueError("Bad size for variable watch: %r" % size)

        if self.has_hardware_breakpoint(tid, address):
            warnings.warn(
                "Hardware breakpoint in thread %d at address %s was overwritten!"
                % (tid, HexDump.address(address, self.system.get_thread(tid).get_bits())),
                BreakpointWarning,
            )

            bp = self.get_hardware_breakpoint(tid, address)
            if bp.get_trigger() != self.BP_BREAK_ON_ACCESS or bp.get_watch() != sizeFlag:
                self.erase_hardware_breakpoint(tid, address)
                self.define_hardware_breakpoint(tid, address, self.BP_BREAK_ON_ACCESS, sizeFlag, True, action)
                bp = self.get_hardware_breakpoint(tid, address)

        else:
            self.define_hardware_breakpoint(tid, address, self.BP_BREAK_ON_ACCESS, sizeFlag, True, action)
            bp = self.get_hardware_breakpoint(tid, address)

        return bp

    def __clear_variable_watch(self, tid, address):
        """
        Used by L{dont_watch_variable} and L{dont_stalk_variable}.

        @type  tid: int
        @param tid: Thread global ID.

        @type  address: int
        @param address: Memory address of variable to stop watching.
        """
        if self.has_hardware_breakpoint(tid, address):
            self.erase_hardware_breakpoint(tid, address)

    def watch_variable(self, tid, address, size, action=None):
        """
        Sets a hardware breakpoint at the given thread, address and size.

        @see: L{dont_watch_variable}

        @type  tid: int
        @param tid: Thread global ID.

        @type  address: int
        @param address: Memory address of variable to watch.

        @type  size: int
        @param size: Size of variable to watch. The only supported sizes are:
```
