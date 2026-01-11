# Chunk: 4e9bd49cabbf_6

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 494-584
- chunk: 7/64

```
t):
        """
        Notify a breakpoint that it's been hit.

        This triggers the corresponding state transition and sets the
        C{breakpoint} property of the given L{Event} object.

        @see: L{disable}, L{enable}, L{one_shot}, L{running}

        @type  event: L{Event}
        @param event: Debug event to handle (depends on the breakpoint type).

        @raise AssertionError: Disabled breakpoints can't be hit.
        """
        aProcess = event.get_process()
        aThread = event.get_thread()
        state = self.get_state()

        event.breakpoint = self

        if state == self.ENABLED:
            self.running(aProcess, aThread)

        elif state == self.RUNNING:
            self.enable(aProcess, aThread)

        elif state == self.ONESHOT:
            self.disable(aProcess, aThread)

        elif state == self.DISABLED:
            # this should not happen
            msg = "Hit a disabled breakpoint at address %s"
            msg = msg % HexDump.address(self.get_address())
            warnings.warn(msg, BreakpointWarning)


# ==============================================================================

# XXX TODO
# Check if the user is trying to set a code breakpoint on a memory mapped file,
# so we don't end up writing the int3 instruction in the file by accident.


class CodeBreakpoint(Breakpoint):
    """
    Code execution breakpoints (using an int3 opcode).

    @see: L{Debug.break_at}

    @type bpInstruction: str
    @cvar bpInstruction: Breakpoint instruction for the current processor.
    """

    typeName = "code breakpoint"

    if win32.arch in (win32.ARCH_I386, win32.ARCH_AMD64):
        bpInstruction = "\xCC"  # int 3

    def __init__(self, address, condition=True, action=None):
        """
        Code breakpoint object.

        @see: L{Breakpoint.__init__}

        @type  address: int
        @param address: Memory address for breakpoint.

        @type  condition: function
        @param condition: (Optional) Condition callback function.

        @type  action: function
        @param action: (Optional) Action callback function.
        """
        if win32.arch not in (win32.ARCH_I386, win32.ARCH_AMD64):
            msg = "Code breakpoints not supported for %s" % win32.arch
            raise NotImplementedError(msg)
        Breakpoint.__init__(self, address, len(self.bpInstruction), condition, action)
        self.__previousValue = self.bpInstruction

    def __set_bp(self, aProcess):
        """
        Writes a breakpoint instruction at the target address.

        @type  aProcess: L{Process}
        @param aProcess: Process object.
        """
        address = self.get_address()
        self.__previousValue = aProcess.read(address, len(self.bpInstruction))
        if self.__previousValue == self.bpInstruction:
            msg = "Possible overlapping code breakpoints at %s"
```
