# Chunk: 4e9bd49cabbf_27

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 2105-2180
- chunk: 28/64

```
id)

    def __cleanup_process(self, event):
        """
        Auxiliary method for L{_notify_exit_process}.
        """
        pid = event.get_pid()
        process = event.get_process()

        # Cleanup code breakpoints
        for bp_pid, bp_address in compat.keys(self.__codeBP):
            if bp_pid == pid:
                bp = self.__codeBP[(bp_pid, bp_address)]
                self.__cleanup_breakpoint(event, bp)
                del self.__codeBP[(bp_pid, bp_address)]

        # Cleanup page breakpoints
        for bp_pid, bp_address in compat.keys(self.__pageBP):
            if bp_pid == pid:
                bp = self.__pageBP[(bp_pid, bp_address)]
                self.__cleanup_breakpoint(event, bp)
                del self.__pageBP[(bp_pid, bp_address)]

        # Cleanup deferred code breakpoints
        try:
            del self.__deferredBP[pid]
        except KeyError:
            pass

    def __cleanup_module(self, event):
        """
        Auxiliary method for L{_notify_unload_dll}.
        """
        pid = event.get_pid()
        process = event.get_process()
        module = event.get_module()

        # Cleanup thread breakpoints on this module
        for tid in process.iter_thread_ids():
            thread = process.get_thread(tid)

            # Running breakpoints
            if tid in self.__runningBP:
                bplist = list(self.__runningBP[tid])
                for bp in bplist:
                    bp_address = bp.get_address()
                    if process.get_module_at_address(bp_address) == module:
                        self.__cleanup_breakpoint(event, bp)
                        self.__runningBP[tid].remove(bp)

            # Hardware breakpoints
            if tid in self.__hardwareBP:
                bplist = list(self.__hardwareBP[tid])
                for bp in bplist:
                    bp_address = bp.get_address()
                    if process.get_module_at_address(bp_address) == module:
                        self.__cleanup_breakpoint(event, bp)
                        self.__hardwareBP[tid].remove(bp)

        # Cleanup code breakpoints on this module
        for bp_pid, bp_address in compat.keys(self.__codeBP):
            if bp_pid == pid:
                if process.get_module_at_address(bp_address) == module:
                    bp = self.__codeBP[(bp_pid, bp_address)]
                    self.__cleanup_breakpoint(event, bp)
                    del self.__codeBP[(bp_pid, bp_address)]

        # Cleanup page breakpoints on this module
        for bp_pid, bp_address in compat.keys(self.__pageBP):
            if bp_pid == pid:
                if process.get_module_at_address(bp_address) == module:
                    bp = self.__pageBP[(bp_pid, bp_address)]
                    self.__cleanup_breakpoint(event, bp)
                    del self.__pageBP[(bp_pid, bp_address)]

```
