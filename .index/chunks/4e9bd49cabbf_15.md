# Chunk: 4e9bd49cabbf_15

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 1165-1238
- chunk: 16/64

```
 But since a thread can run
    # out of those, we need to fall back to this method when needed.

    def __call__(self, event):
        """
        Handles the breakpoint event on entry of the function.

        @type  event: L{ExceptionEvent}
        @param event: Breakpoint hit event.

        @raise WindowsError: An error occured.
        """
        debug = event.debug

        dwProcessId = event.get_pid()
        dwThreadId = event.get_tid()
        aProcess = event.get_process()
        aThread = event.get_thread()

        # Get the return address and function arguments.
        ra = self._get_return_address(aProcess, aThread)
        params = self._get_function_arguments(aProcess, aThread)

        # Keep the function arguments for later use.
        self.__push_params(dwThreadId, params)

        # If we need to hook the return from the function...
        bHookedReturn = False
        if ra is not None and self.__postCB is not None:
            # Try to set a one shot hardware breakpoint at the return address.
            useHardwareBreakpoints = self.useHardwareBreakpoints
            if useHardwareBreakpoints:
                try:
                    debug.define_hardware_breakpoint(
                        dwThreadId, ra, event.debug.BP_BREAK_ON_EXECUTION, event.debug.BP_WATCH_BYTE, True, self.__postCallAction_hwbp
                    )
                    debug.enable_one_shot_hardware_breakpoint(dwThreadId, ra)
                    bHookedReturn = True
                except Exception:
                    e = sys.exc_info()[1]
                    useHardwareBreakpoints = False
                    msg = "Failed to set hardware breakpoint" " at address %s for thread ID %d"
                    msg = msg % (HexDump.address(ra), dwThreadId)
                    warnings.warn(msg, BreakpointWarning)

            # If not possible, set a code breakpoint instead.
            if not useHardwareBreakpoints:
                try:
                    debug.break_at(dwProcessId, ra, self.__postCallAction_codebp)
                    bHookedReturn = True
                except Exception:
                    e = sys.exc_info()[1]
                    msg = "Failed to set code breakpoint" " at address %s for process ID %d"
                    msg = msg % (HexDump.address(ra), dwProcessId)
                    warnings.warn(msg, BreakpointWarning)

        # Call the "pre" callback.
        try:
            self.__callHandler(self.__preCB, event, ra, *params)

        # If no "post" callback is defined, forget the function arguments.
        finally:
            if not bHookedReturn:
                self.__pop_params(dwThreadId)

    def __postCallAction_hwbp(self, event):
        """
        Handles hardware breakpoint events on return from the function.

        @type  event: L{ExceptionEvent}
        @param event: Single step event.
        """

```
