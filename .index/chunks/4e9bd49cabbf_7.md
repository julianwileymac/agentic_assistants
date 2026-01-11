# Chunk: 4e9bd49cabbf_7

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 577-644
- chunk: 8/64

```
ess}
        @param aProcess: Process object.
        """
        address = self.get_address()
        self.__previousValue = aProcess.read(address, len(self.bpInstruction))
        if self.__previousValue == self.bpInstruction:
            msg = "Possible overlapping code breakpoints at %s"
            msg = msg % HexDump.address(address)
            warnings.warn(msg, BreakpointWarning)
        aProcess.write(address, self.bpInstruction)

    def __clear_bp(self, aProcess):
        """
        Restores the original byte at the target address.

        @type  aProcess: L{Process}
        @param aProcess: Process object.
        """
        address = self.get_address()
        currentValue = aProcess.read(address, len(self.bpInstruction))
        if currentValue == self.bpInstruction:
            # Only restore the previous value if the int3 is still there.
            aProcess.write(self.get_address(), self.__previousValue)
        else:
            self.__previousValue = currentValue
            msg = "Overwritten code breakpoint at %s"
            msg = msg % HexDump.address(address)
            warnings.warn(msg, BreakpointWarning)

    def disable(self, aProcess, aThread):
        if not self.is_disabled() and not self.is_running():
            self.__clear_bp(aProcess)
        super(CodeBreakpoint, self).disable(aProcess, aThread)

    def enable(self, aProcess, aThread):
        if not self.is_enabled() and not self.is_one_shot():
            self.__set_bp(aProcess)
        super(CodeBreakpoint, self).enable(aProcess, aThread)

    def one_shot(self, aProcess, aThread):
        if not self.is_enabled() and not self.is_one_shot():
            self.__set_bp(aProcess)
        super(CodeBreakpoint, self).one_shot(aProcess, aThread)

    # FIXME race condition here (however unlikely)
    # If another thread runs on over the target address while
    # the breakpoint is in RUNNING state, we'll miss it. There
    # is a solution to this but it's somewhat complicated, so
    # I'm leaving it for another version of the debugger. :(
    def running(self, aProcess, aThread):
        if self.is_enabled():
            self.__clear_bp(aProcess)
            aThread.set_tf()
        super(CodeBreakpoint, self).running(aProcess, aThread)


# ==============================================================================

# TODO:
# * If the original page was already a guard page, the exception should be
#   passed to the debugee instead of being handled by the debugger.
# * If the original page was already a guard page, it should NOT be converted
#   to a no-access page when disabling the breakpoint.
# * If the page permissions were modified after the breakpoint was enabled,
#   no change should be done on them when disabling the breakpoint. For this
#   we need to remember the original page permissions instead of blindly
#   setting and clearing the guard page bit on them.
```
