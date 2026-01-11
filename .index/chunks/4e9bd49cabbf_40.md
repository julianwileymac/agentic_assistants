# Chunk: 4e9bd49cabbf_40

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 3080-3162
- chunk: 41/64

```
, bp))
        return result

    ##    def get_all_hooks(self):
    ##        """
    ##        @see: L{get_process_hooks}
    ##
    ##        @rtype:  list of tuple( int, int, L{Hook} )
    ##        @return: All defined hooks as a list of tuples (pid, address, hook).
    ##        """
    ##        return [ (pid, address, hook) \
    ##            for ((pid, address), hook) in self.__hook_objects ]
    ##
    ##    def get_process_hooks(self, dwProcessId):
    ##        """
    ##        @see: L{get_all_hooks}
    ##
    ##        @type  dwProcessId: int
    ##        @param dwProcessId: Process global ID.
    ##
    ##        @rtype:  list of tuple( int, int, L{Hook} )
    ##        @return: All hooks for the given process as a list of tuples
    ##            (pid, address, hook).
    ##        """
    ##        return [ (pid, address, hook) \
    ##            for ((pid, address), hook) in self.__hook_objects \
    ##            if pid == dwProcessId ]

    # ------------------------------------------------------------------------------

    # Batch operations on all breakpoints.

    def enable_all_breakpoints(self):
        """
        Enables all disabled breakpoints in all processes.

        @see:
            enable_code_breakpoint,
            enable_page_breakpoint,
            enable_hardware_breakpoint
        """

        # disable code breakpoints
        for pid, bp in self.get_all_code_breakpoints():
            if bp.is_disabled():
                self.enable_code_breakpoint(pid, bp.get_address())

        # disable page breakpoints
        for pid, bp in self.get_all_page_breakpoints():
            if bp.is_disabled():
                self.enable_page_breakpoint(pid, bp.get_address())

        # disable hardware breakpoints
        for tid, bp in self.get_all_hardware_breakpoints():
            if bp.is_disabled():
                self.enable_hardware_breakpoint(tid, bp.get_address())

    def enable_one_shot_all_breakpoints(self):
        """
        Enables for one shot all disabled breakpoints in all processes.

        @see:
            enable_one_shot_code_breakpoint,
            enable_one_shot_page_breakpoint,
            enable_one_shot_hardware_breakpoint
        """

        # disable code breakpoints for one shot
        for pid, bp in self.get_all_code_breakpoints():
            if bp.is_disabled():
                self.enable_one_shot_code_breakpoint(pid, bp.get_address())

        # disable page breakpoints for one shot
        for pid, bp in self.get_all_page_breakpoints():
            if bp.is_disabled():
                self.enable_one_shot_page_breakpoint(pid, bp.get_address())

        # disable hardware breakpoints for one shot
        for tid, bp in self.get_all_hardware_breakpoints():
            if bp.is_disabled():
                self.enable_one_shot_hardware_breakpoint(tid, bp.get_address())

```
