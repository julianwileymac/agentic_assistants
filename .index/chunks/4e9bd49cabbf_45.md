# Chunk: 4e9bd49cabbf_45

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 3436-3508
- chunk: 46/64

```
_running_bp(tid, bp)

                # Evaluate the breakpoint condition.
                bCondition = bp.eval_condition(event)

                # If the breakpoint is automatic, run the action.
                # If not, notify the user.
                if bCondition and bp.is_automatic():
                    bCallHandler = bp.run_action(event)
                else:
                    bCallHandler = bCondition

        # Handle the system breakpoint.
        # TODO: examine the stack trace to figure out if it's really a
        # system breakpoint or an antidebug trick. The caller should be
        # inside ntdll if it's legit.
        elif event.get_process().is_system_defined_breakpoint(address):
            event.continueStatus = win32.DBG_CONTINUE

        # In hostile mode, if we don't have a breakpoint here pass the
        # exception to the debugee. In normal mode assume all breakpoint
        # exceptions are to be handled by the debugger.
        else:
            if self.in_hostile_mode():
                event.continueStatus = win32.DBG_EXCEPTION_NOT_HANDLED
            else:
                event.continueStatus = win32.DBG_CONTINUE

        return bCallHandler

    def _notify_single_step(self, event):
        """
        Notify breakpoints of a single step exception event.

        @type  event: L{ExceptionEvent}
        @param event: Single step exception event.

        @rtype:  bool
        @return: C{True} to call the user-defined handle, C{False} otherwise.
        """
        pid = event.get_pid()
        tid = event.get_tid()
        aThread = event.get_thread()
        aProcess = event.get_process()
        bCallHandler = True
        bIsOurs = False

        # In hostile mode set the default to pass the exception to the debugee.
        # If we later determine the exception is ours, hide it instead.
        old_continueStatus = event.continueStatus
        try:
            if self.in_hostile_mode():
                event.continueStatus = win32.DBG_EXCEPTION_NOT_HANDLED

            # Single step support is implemented on x86/x64 architectures only.
            if self.system.arch not in (win32.ARCH_I386, win32.ARCH_AMD64):
                return bCallHandler

            # In hostile mode, read the last executed bytes to try to detect
            # some antidebug tricks. Skip this check in normal mode because
            # it'd slow things down.
            #
            # FIXME: weird opcode encodings may bypass this check!
            #
            # bFakeSingleStep: Ice Breakpoint undocumented instruction.
            # bHideTrapFlag: Don't let pushf instructions get the real value of
            #                the trap flag.
            # bNextIsPopFlags: Don't let popf instructions clear the trap flag.
            #
            bFakeSingleStep = False
            bLastIsPushFlags = False
            bNextIsPopFlags = False
```
