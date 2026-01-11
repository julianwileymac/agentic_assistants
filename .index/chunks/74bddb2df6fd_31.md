# Chunk: 74bddb2df6fd_31

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 2187-2266
- chunk: 32/33

```
ys.exc_info()[1]
            warnings.warn("Cannot load history file, reason: %s" % str(e))

    def save_history(self):
        if self.history_file_full_path is not None:
            global readline
            if readline is None:
                try:
                    import readline
                except ImportError:
                    return
            try:
                readline.write_history_file(self.history_file_full_path)
            except IOError:
                e = sys.exc_info()[1]
                warnings.warn("Cannot save history file, reason: %s" % str(e))

    # ------------------------------------------------------------------------------
    # Main loop

    # Debugging loop.
    def loop(self):
        self.debuggerExit = False
        debug = self.debug

        # Stop on the initial event, if any.
        if self.lastEvent is not None:
            self.cmdqueue.append("r")
            self.prompt_user()

        # Loop until the debugger is told to quit.
        while not self.debuggerExit:
            try:
                # If for some reason the last event wasn't continued,
                # continue it here. This won't be done more than once
                # for a given Event instance, though.
                try:
                    debug.cont()
                # On error, show the command prompt.
                except Exception:
                    traceback.print_exc()
                    self.prompt_user()

                # While debugees are attached, handle debug events.
                # Some debug events may cause the command prompt to be shown.
                if self.debug.get_debugee_count() > 0:
                    try:
                        # Get the next debug event.
                        debug.wait()

                        # Dispatch the debug event.
                        try:
                            debug.dispatch()

                        # Continue the debug event.
                        finally:
                            debug.cont()

                    # On error, show the command prompt.
                    except Exception:
                        traceback.print_exc()
                        self.prompt_user()

                # While no debugees are attached, show the command prompt.
                else:
                    self.prompt_user()

            # When the user presses Ctrl-C send a debug break to all debugees.
            except KeyboardInterrupt:
                success = False
                try:
                    print("*** User requested debug break")
                    system = debug.system
                    for pid in debug.get_debugee_pids():
                        try:
                            system.get_process(pid).debug_break()
                            success = True
                        except:
                            traceback.print_exc()
```
