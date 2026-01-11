# Chunk: 4e9bd49cabbf_37

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 2868-2948
- chunk: 38/64

```

        @param address: Memory address of breakpoint.
        """
        bp = self.get_page_breakpoint(dwProcessId, address)
        begin = bp.get_address()
        end = begin + bp.get_size()
        if not bp.is_disabled():
            self.disable_page_breakpoint(dwProcessId, address)
        address = begin
        pageSize = MemoryAddresses.pageSize
        while address < end:
            del self.__pageBP[(dwProcessId, address)]
            address = address + pageSize

    def erase_hardware_breakpoint(self, dwThreadId, address):
        """
        Erases the hardware breakpoint at the given address.

        @see:
            L{define_hardware_breakpoint},
            L{has_hardware_breakpoint},
            L{get_hardware_breakpoint},
            L{enable_hardware_breakpoint},
            L{enable_one_shot_hardware_breakpoint},
            L{disable_hardware_breakpoint}

        @type  dwThreadId: int
        @param dwThreadId: Thread global ID.

        @type  address: int
        @param address: Memory address of breakpoint.
        """
        bp = self.get_hardware_breakpoint(dwThreadId, address)
        if not bp.is_disabled():
            self.disable_hardware_breakpoint(dwThreadId, address)
        bpSet = self.__hardwareBP[dwThreadId]
        bpSet.remove(bp)
        if not bpSet:
            del self.__hardwareBP[dwThreadId]

    # ------------------------------------------------------------------------------

    # Listing breakpoints.

    def get_all_breakpoints(self):
        """
        Returns all breakpoint objects as a list of tuples.

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

        @rtype:  list of tuple( pid, tid, bp )
        @return: List of all breakpoints.
        """
        bplist = list()

        # Get the code breakpoints.
        for pid, bp in self.get_all_code_breakpoints():
            bplist.append((pid, None, bp))

        # Get the page breakpoints.
        for pid, bp in self.get_all_page_breakpoints():
            bplist.append((pid, None, bp))

        # Get the hardware breakpoints.
        for tid, bp in self.get_all_hardware_breakpoints():
            pid = self.system.get_thread(tid).get_pid()
```
