# Chunk: 4e9bd49cabbf_46

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 3501-3568
- chunk: 47/64

```
 let pushf instructions get the real value of
            #                the trap flag.
            # bNextIsPopFlags: Don't let popf instructions clear the trap flag.
            #
            bFakeSingleStep = False
            bLastIsPushFlags = False
            bNextIsPopFlags = False
            if self.in_hostile_mode():
                pc = aThread.get_pc()
                c = aProcess.read_char(pc - 1)
                if c == 0xF1:  # int1
                    bFakeSingleStep = True
                elif c == 0x9C:  # pushf
                    bLastIsPushFlags = True
                c = aProcess.peek_char(pc)
                if c == 0x66:  # the only valid prefix for popf
                    c = aProcess.peek_char(pc + 1)
                if c == 0x9D:  # popf
                    if bLastIsPushFlags:
                        bLastIsPushFlags = False  # they cancel each other out
                    else:
                        bNextIsPopFlags = True

            # When the thread is in tracing mode,
            # don't pass the exception to the debugee
            # and set the trap flag again.
            if self.is_tracing(tid):
                bIsOurs = True
                if not bFakeSingleStep:
                    event.continueStatus = win32.DBG_CONTINUE
                aThread.set_tf()

                # Don't let the debugee read or write the trap flag.
                # This code works in 32 and 64 bits thanks to the endianness.
                if bLastIsPushFlags or bNextIsPopFlags:
                    sp = aThread.get_sp()
                    flags = aProcess.read_dword(sp)
                    if bLastIsPushFlags:
                        flags &= ~Thread.Flags.Trap
                    else:  # if bNextIsPopFlags:
                        flags |= Thread.Flags.Trap
                    aProcess.write_dword(sp, flags)

            # Handle breakpoints in RUNNING state.
            running = self.__get_running_bp_set(tid)
            if running:
                bIsOurs = True
                if not bFakeSingleStep:
                    event.continueStatus = win32.DBG_CONTINUE
                bCallHandler = False
                while running:
                    try:
                        running.pop().hit(event)
                    except Exception:
                        e = sys.exc_info()[1]
                        warnings.warn(str(e), BreakpointWarning)

            # Handle hardware breakpoints.
            if tid in self.__hardwareBP:
                ctx = aThread.get_context(win32.CONTEXT_DEBUG_REGISTERS)
                Dr6 = ctx["Dr6"]
                ctx["Dr6"] = Dr6 & DebugRegister.clearHitMask
                aThread.set_context(ctx)
                bFoundBreakpoint = False
                bCondition = False
                hwbpList = [bp for bp in self.__hardwareBP[tid]]
                for bp in hwbpList:
```
