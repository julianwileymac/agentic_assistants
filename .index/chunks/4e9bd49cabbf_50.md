# Chunk: 4e9bd49cabbf_50

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 3767-3845
- chunk: 51/64

```
arn(msg, BreakpointWarning)
                return
        if self.has_code_breakpoint(pid, address):
            self.erase_code_breakpoint(pid, address)

    def __set_deferred_breakpoints(self, event):
        """
        Used internally. Sets all deferred breakpoints for a DLL when it's
        loaded.

        @type  event: L{LoadDLLEvent}
        @param event: Load DLL event.
        """
        pid = event.get_pid()
        try:
            deferred = self.__deferredBP[pid]
        except KeyError:
            return
        aProcess = event.get_process()
        for label, (action, oneshot) in deferred.items():
            try:
                address = aProcess.resolve_label(label)
            except Exception:
                continue
            del deferred[label]
            try:
                self.__set_break(pid, address, action, oneshot)
            except Exception:
                msg = "Can't set deferred breakpoint %s at process ID %d"
                msg = msg % (label, pid)
                warnings.warn(msg, BreakpointWarning)

    def get_all_deferred_code_breakpoints(self):
        """
        Returns a list of deferred code breakpoints.

        @rtype:  tuple of (int, str, callable, bool)
        @return: Tuple containing the following elements:
             - Process ID where to set the breakpoint.
             - Label pointing to the address where to set the breakpoint.
             - Action callback for the breakpoint.
             - C{True} of the breakpoint is one-shot, C{False} otherwise.
        """
        result = []
        for pid, deferred in compat.iteritems(self.__deferredBP):
            for label, (action, oneshot) in compat.iteritems(deferred):
                result.add((pid, label, action, oneshot))
        return result

    def get_process_deferred_code_breakpoints(self, dwProcessId):
        """
        Returns a list of deferred code breakpoints.

        @type  dwProcessId: int
        @param dwProcessId: Process ID.

        @rtype:  tuple of (int, str, callable, bool)
        @return: Tuple containing the following elements:
             - Label pointing to the address where to set the breakpoint.
             - Action callback for the breakpoint.
             - C{True} of the breakpoint is one-shot, C{False} otherwise.
        """
        return [(label, action, oneshot) for (label, (action, oneshot)) in compat.iteritems(self.__deferredBP.get(dwProcessId, {}))]

    def stalk_at(self, pid, address, action=None):
        """
        Sets a one shot code breakpoint at the given process and address.

        If instead of an address you pass a label, the breakpoint may be
        deferred until the DLL it points to is loaded.

        @see: L{break_at}, L{dont_stalk_at}

        @type  pid: int
        @param pid: Process global ID.

        @type  address: int or str
        @param address:
```
