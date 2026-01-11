# Chunk: 4e9bd49cabbf_38

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 2940-3016
- chunk: 39/64

```

        # Get the page breakpoints.
        for pid, bp in self.get_all_page_breakpoints():
            bplist.append((pid, None, bp))

        # Get the hardware breakpoints.
        for tid, bp in self.get_all_hardware_breakpoints():
            pid = self.system.get_thread(tid).get_pid()
            bplist.append((pid, tid, bp))

        # Return the list of breakpoints.
        return bplist

    def get_all_code_breakpoints(self):
        """
        @rtype:  list of tuple( int, L{CodeBreakpoint} )
        @return: All code breakpoints as a list of tuples (pid, bp).
        """
        return [(pid, bp) for ((pid, address), bp) in compat.iteritems(self.__codeBP)]

    def get_all_page_breakpoints(self):
        """
        @rtype:  list of tuple( int, L{PageBreakpoint} )
        @return: All page breakpoints as a list of tuples (pid, bp).
        """
        ##        return list( set( [ (pid, bp) for ((pid, address), bp) in compat.iteritems(self.__pageBP) ] ) )
        result = set()
        for (pid, address), bp in compat.iteritems(self.__pageBP):
            result.add((pid, bp))
        return list(result)

    def get_all_hardware_breakpoints(self):
        """
        @rtype:  list of tuple( int, L{HardwareBreakpoint} )
        @return: All hardware breakpoints as a list of tuples (tid, bp).
        """
        result = list()
        for tid, bplist in compat.iteritems(self.__hardwareBP):
            for bp in bplist:
                result.append((tid, bp))
        return result

    def get_process_breakpoints(self, dwProcessId):
        """
        Returns all breakpoint objects for the given process as a list of tuples.

        Each tuple contains:
         - Process global ID to which the breakpoint applies.
         - Thread global ID to which the breakpoint applies, or C{None}.
         - The L{Breakpoint} object itself.

        @note: If you're only interested in a specific breakpoint type, or in
            breakpoints for a specific process or thread, it's probably faster
            to call one of the following methods:
             - L{get_all_code_breakpoints}
             - L{get_all_page_breakpoints}
             - L{get_all_hardware_breakpoints}
             - L{get_process_code_breakpoints}
             - L{get_process_page_breakpoints}
             - L{get_process_hardware_breakpoints}
             - L{get_thread_hardware_breakpoints}

        @type  dwProcessId: int
        @param dwProcessId: Process global ID.

        @rtype:  list of tuple( pid, tid, bp )
        @return: List of all breakpoints for the given process.
        """
        bplist = list()

        # Get the code breakpoints.
        for bp in self.get_process_code_breakpoints(dwProcessId):
            bplist.append((dwProcessId, None, bp))

        # Get the page breakpoints.
        for bp in self.get_process_page_breakpoints(dwProcessId):
```
