# Chunk: 4e9bd49cabbf_41

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 3155-3238
- chunk: 42/64

```
      self.enable_one_shot_page_breakpoint(pid, bp.get_address())

        # disable hardware breakpoints for one shot
        for tid, bp in self.get_all_hardware_breakpoints():
            if bp.is_disabled():
                self.enable_one_shot_hardware_breakpoint(tid, bp.get_address())

    def disable_all_breakpoints(self):
        """
        Disables all breakpoints in all processes.

        @see:
            disable_code_breakpoint,
            disable_page_breakpoint,
            disable_hardware_breakpoint
        """

        # disable code breakpoints
        for pid, bp in self.get_all_code_breakpoints():
            self.disable_code_breakpoint(pid, bp.get_address())

        # disable page breakpoints
        for pid, bp in self.get_all_page_breakpoints():
            self.disable_page_breakpoint(pid, bp.get_address())

        # disable hardware breakpoints
        for tid, bp in self.get_all_hardware_breakpoints():
            self.disable_hardware_breakpoint(tid, bp.get_address())

    def erase_all_breakpoints(self):
        """
        Erases all breakpoints in all processes.

        @see:
            erase_code_breakpoint,
            erase_page_breakpoint,
            erase_hardware_breakpoint
        """

        # This should be faster but let's not trust the GC so much :P
        # self.disable_all_breakpoints()
        # self.__codeBP       = dict()
        # self.__pageBP       = dict()
        # self.__hardwareBP   = dict()
        # self.__runningBP    = dict()
        # self.__hook_objects = dict()

        ##        # erase hooks
        ##        for (pid, address, hook) in self.get_all_hooks():
        ##            self.dont_hook_function(pid, address)

        # erase code breakpoints
        for pid, bp in self.get_all_code_breakpoints():
            self.erase_code_breakpoint(pid, bp.get_address())

        # erase page breakpoints
        for pid, bp in self.get_all_page_breakpoints():
            self.erase_page_breakpoint(pid, bp.get_address())

        # erase hardware breakpoints
        for tid, bp in self.get_all_hardware_breakpoints():
            self.erase_hardware_breakpoint(tid, bp.get_address())

    # ------------------------------------------------------------------------------

    # Batch operations on breakpoints per process.

    def enable_process_breakpoints(self, dwProcessId):
        """
        Enables all disabled breakpoints for the given process.

        @type  dwProcessId: int
        @param dwProcessId: Process global ID.
        """

        # enable code breakpoints
        for bp in self.get_process_code_breakpoints(dwProcessId):
            if bp.is_disabled():
                self.enable_code_breakpoint(dwProcessId, bp.get_address())

        # enable page breakpoints
        for bp in self.get_process_page_breakpoints(dwProcessId):
            if bp.is_disabled():
```
