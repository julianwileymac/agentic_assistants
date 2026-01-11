# Chunk: ce92ab9adeed_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_console.py`
- lines: 137-212
- chunk: 3/4

```
elf, line)

    @overrides(InteractiveConsole.runcode)
    def runcode(self, code):
        """Execute a code object.

        When an exception occurs, self.showtraceback() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which is reraised.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.

        """
        try:
            updated_globals = self.get_namespace()
            initial_globals = updated_globals.copy()

            updated_locals = None

            is_async = False
            if hasattr(inspect, "CO_COROUTINE"):
                is_async = inspect.CO_COROUTINE & code.co_flags == inspect.CO_COROUTINE

            if is_async:
                t = _EvalAwaitInNewEventLoop(code, updated_globals, updated_locals)
                t.start()
                t.join()

                update_globals_and_locals(updated_globals, initial_globals, self.frame)
                if t.exc:
                    raise t.exc[1].with_traceback(t.exc[2])

            else:
                try:
                    exec(code, updated_globals, updated_locals)
                finally:
                    update_globals_and_locals(updated_globals, initial_globals, self.frame)
        except SystemExit:
            raise
        except:
            # In case sys.excepthook called, use original excepthook #PyDev-877: Debug console freezes with Python 3.5+
            # (showtraceback does it on python 3.5 onwards)
            sys.excepthook = sys.__excepthook__
            try:
                self.showtraceback()
            finally:
                sys.__excepthook__ = sys.excepthook

    def get_namespace(self):
        dbg_namespace = {}
        dbg_namespace.update(self.frame.f_globals)
        dbg_namespace.update(self.frame.f_locals)  # locals later because it has precedence over the actual globals
        return dbg_namespace


# =======================================================================================================================
# InteractiveConsoleCache
# =======================================================================================================================
class InteractiveConsoleCache:
    thread_id = None
    frame_id = None
    interactive_console_instance = None


# Note: On Jython 2.1 we can't use classmethod or staticmethod, so, just make the functions below free-functions.
def get_interactive_console(thread_id, frame_id, frame, console_message):
    """returns the global interactive console.
    interactive console should have been initialized by this time
    :rtype: DebugConsole
    """
    if InteractiveConsoleCache.thread_id == thread_id and InteractiveConsoleCache.frame_id == frame_id:
        return InteractiveConsoleCache.interactive_console_instance

```
