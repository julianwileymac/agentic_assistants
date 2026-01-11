# Chunk: 4e9bd49cabbf_47

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 3561-3640
- chunk: 48/64

```
= ctx["Dr6"]
                ctx["Dr6"] = Dr6 & DebugRegister.clearHitMask
                aThread.set_context(ctx)
                bFoundBreakpoint = False
                bCondition = False
                hwbpList = [bp for bp in self.__hardwareBP[tid]]
                for bp in hwbpList:
                    if not bp in self.__hardwareBP[tid]:
                        continue  # it was removed by a user-defined callback
                    slot = bp.get_slot()
                    if (slot is not None) and (Dr6 & DebugRegister.hitMask[slot]):
                        if not bFoundBreakpoint:  # set before actions are called
                            if not bFakeSingleStep:
                                event.continueStatus = win32.DBG_CONTINUE
                        bFoundBreakpoint = True
                        bIsOurs = True
                        bp.hit(event)
                        if bp.is_running():
                            self.__add_running_bp(tid, bp)
                        bThisCondition = bp.eval_condition(event)
                        if bThisCondition and bp.is_automatic():
                            bp.run_action(event)
                            bThisCondition = False
                        bCondition = bCondition or bThisCondition
                if bFoundBreakpoint:
                    bCallHandler = bCondition

            # Always call the user-defined handler
            # when the thread is in tracing mode.
            if self.is_tracing(tid):
                bCallHandler = True

            # If we're not in hostile mode, by default we assume all single
            # step exceptions are caused by the debugger.
            if not bIsOurs and not self.in_hostile_mode():
                aThread.clear_tf()

        # If the user hit Control-C while we were inside the try block,
        # set the default continueStatus back.
        except:
            event.continueStatus = old_continueStatus
            raise

        return bCallHandler

    def _notify_load_dll(self, event):
        """
        Notify the loading of a DLL.

        @type  event: L{LoadDLLEvent}
        @param event: Load DLL event.

        @rtype:  bool
        @return: C{True} to call the user-defined handler, C{False} otherwise.
        """
        self.__set_deferred_breakpoints(event)
        return True

    def _notify_unload_dll(self, event):
        """
        Notify the unloading of a DLL.

        @type  event: L{UnloadDLLEvent}
        @param event: Unload DLL event.

        @rtype:  bool
        @return: C{True} to call the user-defined handler, C{False} otherwise.
        """
        self.__cleanup_module(event)
        return True

    def _notify_exit_thread(self, event):
        """
        Notify the termination of a thread.

        @type  event: L{ExitThreadEvent}
        @param event: Exit thread event.

        @rtype:  bool
```
