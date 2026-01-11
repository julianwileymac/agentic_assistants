# Chunk: 4e9bd49cabbf_44

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 3366-3444
- chunk: 45/64

```
 # Do we have an active page breakpoint there?
        key = (pid, address)
        if key in self.__pageBP:
            bp = self.__pageBP[key]
            if bp.is_enabled() or bp.is_one_shot():
                # Breakpoint is ours.
                event.continueStatus = win32.DBG_CONTINUE
                ##                event.continueStatus = win32.DBG_EXCEPTION_HANDLED

                # Hit the breakpoint.
                bp.hit(event)

                # Remember breakpoints in RUNNING state.
                if bp.is_running():
                    tid = event.get_tid()
                    self.__add_running_bp(tid, bp)

                # Evaluate the breakpoint condition.
                bCondition = bp.eval_condition(event)

                # If the breakpoint is automatic, run the action.
                # If not, notify the user.
                if bCondition and bp.is_automatic():
                    bp.run_action(event)
                    bCallHandler = False
                else:
                    bCallHandler = bCondition

        # If we don't have a breakpoint here pass the exception to the debugee.
        # This is a normally occurring exception so we shouldn't swallow it.
        else:
            event.continueStatus = win32.DBG_EXCEPTION_NOT_HANDLED

        return bCallHandler

    def _notify_breakpoint(self, event):
        """
        Notify breakpoints of a breakpoint exception event.

        @type  event: L{ExceptionEvent}
        @param event: Breakpoint exception event.

        @rtype:  bool
        @return: C{True} to call the user-defined handle, C{False} otherwise.
        """
        address = event.get_exception_address()
        pid = event.get_pid()
        bCallHandler = True

        # Do we have an active code breakpoint there?
        key = (pid, address)
        if key in self.__codeBP:
            bp = self.__codeBP[key]
            if not bp.is_disabled():
                # Change the program counter (PC) to the exception address.
                # This accounts for the change in PC caused by
                # executing the breakpoint instruction, no matter
                # the size of it.
                aThread = event.get_thread()
                aThread.set_pc(address)

                # Swallow the exception.
                event.continueStatus = win32.DBG_CONTINUE

                # Hit the breakpoint.
                bp.hit(event)

                # Remember breakpoints in RUNNING state.
                if bp.is_running():
                    tid = event.get_tid()
                    self.__add_running_bp(tid, bp)

                # Evaluate the breakpoint condition.
                bCondition = bp.eval_condition(event)

                # If the breakpoint is automatic, run the action.
                # If not, notify the user.
                if bCondition and bp.is_automatic():
```
