# Chunk: 4e9bd49cabbf_26

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 2031-2116
- chunk: 27/64

```
# tid -> set( Breakpoint )
        self.__tracing = set()  # set( tid )
        self.__deferredBP = dict()  # pid -> label -> (action, oneshot)

    # ------------------------------------------------------------------------------

    # This operates on the dictionary of running breakpoints.
    # Since the bps are meant to stay alive no cleanup is done here.

    def __get_running_bp_set(self, tid):
        "Auxiliary method."
        return self.__runningBP.get(tid, ())

    def __add_running_bp(self, tid, bp):
        "Auxiliary method."
        if tid not in self.__runningBP:
            self.__runningBP[tid] = set()
        self.__runningBP[tid].add(bp)

    def __del_running_bp(self, tid, bp):
        "Auxiliary method."
        self.__runningBP[tid].remove(bp)
        if not self.__runningBP[tid]:
            del self.__runningBP[tid]

    def __del_running_bp_from_all_threads(self, bp):
        "Auxiliary method."
        for tid, bpset in compat.iteritems(self.__runningBP):
            if bp in bpset:
                bpset.remove(bp)
                self.system.get_thread(tid).clear_tf()

    # ------------------------------------------------------------------------------

    # This is the cleanup code. Mostly called on response to exit/unload debug
    # events. If possible it shouldn't raise exceptions on runtime errors.
    # The main goal here is to avoid memory or handle leaks.

    def __cleanup_breakpoint(self, event, bp):
        "Auxiliary method."
        try:
            process = event.get_process()
            thread = event.get_thread()
            bp.disable(process, thread)  # clear the debug regs / trap flag
        except Exception:
            pass
        bp.set_condition(True)  # break possible circular reference
        bp.set_action(None)  # break possible circular reference

    def __cleanup_thread(self, event):
        """
        Auxiliary method for L{_notify_exit_thread}
        and L{_notify_exit_process}.
        """
        tid = event.get_tid()

        # Cleanup running breakpoints
        try:
            for bp in self.__runningBP[tid]:
                self.__cleanup_breakpoint(event, bp)
            del self.__runningBP[tid]
        except KeyError:
            pass

        # Cleanup hardware breakpoints
        try:
            for bp in self.__hardwareBP[tid]:
                self.__cleanup_breakpoint(event, bp)
            del self.__hardwareBP[tid]
        except KeyError:
            pass

        # Cleanup set of threads being traced
        if tid in self.__tracing:
            self.__tracing.remove(tid)

    def __cleanup_process(self, event):
        """
        Auxiliary method for L{_notify_exit_process}.
        """
        pid = event.get_pid()
        process = event.get_process()

        # Cleanup code breakpoints
        for bp_pid, bp_address in compat.keys(self.__codeBP):
```
