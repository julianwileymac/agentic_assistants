# Chunk: 4e9bd49cabbf_16

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 1227-1324
- chunk: 17/64

```
not bHookedReturn:
                self.__pop_params(dwThreadId)

    def __postCallAction_hwbp(self, event):
        """
        Handles hardware breakpoint events on return from the function.

        @type  event: L{ExceptionEvent}
        @param event: Single step event.
        """

        # Remove the one shot hardware breakpoint
        # at the return address location in the stack.
        tid = event.get_tid()
        address = event.breakpoint.get_address()
        event.debug.erase_hardware_breakpoint(tid, address)

        # Call the "post" callback.
        try:
            self.__postCallAction(event)

        # Forget the parameters.
        finally:
            self.__pop_params(tid)

    def __postCallAction_codebp(self, event):
        """
        Handles code breakpoint events on return from the function.

        @type  event: L{ExceptionEvent}
        @param event: Breakpoint hit event.
        """

        # If the breakpoint was accidentally hit by another thread,
        # pass it to the debugger instead of calling the "post" callback.
        #
        # XXX FIXME:
        # I suppose this check will fail under some weird conditions...
        #
        tid = event.get_tid()
        if tid not in self.__paramStack:
            return True

        # Remove the code breakpoint at the return address.
        pid = event.get_pid()
        address = event.breakpoint.get_address()
        event.debug.dont_break_at(pid, address)

        # Call the "post" callback.
        try:
            self.__postCallAction(event)

        # Forget the parameters.
        finally:
            self.__pop_params(tid)

    def __postCallAction(self, event):
        """
        Calls the "post" callback.

        @type  event: L{ExceptionEvent}
        @param event: Breakpoint hit event.
        """
        aThread = event.get_thread()
        retval = self._get_return_value(aThread)
        self.__callHandler(self.__postCB, event, retval)

    def __callHandler(self, callback, event, *params):
        """
        Calls a "pre" or "post" handler, if set.

        @type  callback: function
        @param callback: Callback function to call.

        @type  event: L{ExceptionEvent}
        @param event: Breakpoint hit event.

        @type  params: tuple
        @param params: Parameters for the callback function.
        """
        if callback is not None:
            event.hook = self
            callback(event, *params)

    def __push_params(self, tid, params):
        """
        Remembers the arguments tuple for the last call to the hooked function
        from this thread.

        @type  tid: int
        @param tid: Thread global ID.

        @type  params: tuple( arg, arg, arg... )
        @param params: Tuple of arguments.
        """
        stack = self.__paramStack.get(tid, [])
        stack.append(params)
```
