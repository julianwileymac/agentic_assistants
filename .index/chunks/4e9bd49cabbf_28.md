# Chunk: 4e9bd49cabbf_28

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 2173-2256
- chunk: 29/64

```
.__pageBP):
            if bp_pid == pid:
                if process.get_module_at_address(bp_address) == module:
                    bp = self.__pageBP[(bp_pid, bp_address)]
                    self.__cleanup_breakpoint(event, bp)
                    del self.__pageBP[(bp_pid, bp_address)]

    # ------------------------------------------------------------------------------

    # Defining breakpoints.

    # Code breakpoints.
    def define_code_breakpoint(self, dwProcessId, address, condition=True, action=None):
        """
        Creates a disabled code breakpoint at the given address.

        @see:
            L{has_code_breakpoint},
            L{get_code_breakpoint},
            L{enable_code_breakpoint},
            L{enable_one_shot_code_breakpoint},
            L{disable_code_breakpoint},
            L{erase_code_breakpoint}

        @type  dwProcessId: int
        @param dwProcessId: Process global ID.

        @type  address: int
        @param address: Memory address of the code instruction to break at.

        @type  condition: function
        @param condition: (Optional) Condition callback function.

            The callback signature is::

                def condition_callback(event):
                    return True     # returns True or False

            Where B{event} is an L{Event} object,
            and the return value is a boolean
            (C{True} to dispatch the event, C{False} otherwise).

        @type  action: function
        @param action: (Optional) Action callback function.
            If specified, the event is handled by this callback instead of
            being dispatched normally.

            The callback signature is::

                def action_callback(event):
                    pass        # no return value

            Where B{event} is an L{Event} object,
            and the return value is a boolean
            (C{True} to dispatch the event, C{False} otherwise).

        @rtype:  L{CodeBreakpoint}
        @return: The code breakpoint object.
        """
        process = self.system.get_process(dwProcessId)
        bp = CodeBreakpoint(address, condition, action)

        key = (dwProcessId, bp.get_address())
        if key in self.__codeBP:
            msg = "Already exists (PID %d) : %r"
            raise KeyError(msg % (dwProcessId, self.__codeBP[key]))
        self.__codeBP[key] = bp
        return bp

    # Page breakpoints.
    def define_page_breakpoint(self, dwProcessId, address, pages=1, condition=True, action=None):
        """
        Creates a disabled page breakpoint at the given address.

        @see:
            L{has_page_breakpoint},
            L{get_page_breakpoint},
            L{enable_page_breakpoint},
            L{enable_one_shot_page_breakpoint},
            L{disable_page_breakpoint},
            L{erase_page_breakpoint}

        @type  dwProcessId: int
```
