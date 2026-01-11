# Chunk: 4e9bd49cabbf_49

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 3703-3775
- chunk: 50/64

```
      raise Exception()
            except Exception:
                try:
                    deferred = self.__deferredBP[pid]
                except KeyError:
                    deferred = dict()
                    self.__deferredBP[pid] = deferred
                if label in deferred:
                    msg = "Redefined deferred code breakpoint at %s in process ID %d"
                    msg = msg % (label, pid)
                    warnings.warn(msg, BreakpointWarning)
                deferred[label] = (action, oneshot)
                return None
        if self.has_code_breakpoint(pid, address):
            bp = self.get_code_breakpoint(pid, address)
            if bp.get_action() != action:  # can't use "is not", fails for bound methods
                bp.set_action(action)
                msg = "Redefined code breakpoint at %s in process ID %d"
                msg = msg % (label, pid)
                warnings.warn(msg, BreakpointWarning)
        else:
            self.define_code_breakpoint(pid, address, True, action)
            bp = self.get_code_breakpoint(pid, address)
        if oneshot:
            if not bp.is_one_shot():
                self.enable_one_shot_code_breakpoint(pid, address)
        else:
            if not bp.is_enabled():
                self.enable_code_breakpoint(pid, address)
        return bp

    def __clear_break(self, pid, address):
        """
        Used by L{dont_break_at} and L{dont_stalk_at}.

        @type  pid: int
        @param pid: Process global ID.

        @type  address: int or str
        @param address:
            Memory address of code instruction to break at. It can be an
            integer value for the actual address or a string with a label
            to be resolved.
        """
        if type(address) not in (int, long):
            unknown = True
            label = address
            try:
                deferred = self.__deferredBP[pid]
                del deferred[label]
                unknown = False
            except KeyError:
                ##                traceback.print_last()      # XXX DEBUG
                pass
            aProcess = self.system.get_process(pid)
            try:
                address = aProcess.resolve_label(label)
                if not address:
                    raise Exception()
            except Exception:
                ##                traceback.print_last()      # XXX DEBUG
                if unknown:
                    msg = "Can't clear unknown code breakpoint" " at %s in process ID %d"
                    msg = msg % (label, pid)
                    warnings.warn(msg, BreakpointWarning)
                return
        if self.has_code_breakpoint(pid, address):
            self.erase_code_breakpoint(pid, address)

    def __set_deferred_breakpoints(self, event):
        """
        Used internally. Sets all deferred breakpoints for a DLL when it's
```
