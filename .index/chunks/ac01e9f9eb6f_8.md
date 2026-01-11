# Chunk: ac01e9f9eb6f_8

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/pydev_console_utils.py`
- lines: 569-642
- chunk: 9/9

```

                self.debugger.disable_tracing()
            except:
                traceback.print_exc()
                sys.stderr.write("Failed to connect to target debugger.\n")

            # Register to process commands when idle
            self.debugrunning = False
            try:
                import pydevconsole

                pydevconsole.set_debug_hook(self.debugger.process_internal_commands)
            except:
                traceback.print_exc()
                sys.stderr.write("Version of Python does not support debuggable Interactive Console.\n")

        # Important: it has to be really enabled in the main thread, so, schedule
        # it to run in the main thread.
        self.exec_queue.put(do_connect_to_debugger)

        return ("connect complete",)

    def handshake(self):
        if self.connect_status_queue is not None:
            self.connect_status_queue.put(True)
        return "PyCharm"

    def get_connect_status_queue(self):
        return self.connect_status_queue

    def hello(self, input_str):
        # Don't care what the input string is
        return ("Hello eclipse",)

    def enableGui(self, guiname):
        """Enable the GUI specified in guiname (see inputhook for list).
        As with IPython, enabling multiple GUIs isn't an error, but
        only the last one's main loop runs and it may not work
        """

        def do_enable_gui():
            from _pydev_bundle.pydev_versioncheck import versionok_for_gui

            if versionok_for_gui():
                try:
                    from pydev_ipython.inputhook import enable_gui

                    enable_gui(guiname)
                except:
                    sys.stderr.write("Failed to enable GUI event loop integration for '%s'\n" % guiname)
                    traceback.print_exc()
            elif guiname not in ["none", "", None]:
                # Only print a warning if the guiname was going to do something
                sys.stderr.write("PyDev console: Python version does not support GUI event loop integration for '%s'\n" % guiname)
            # Return value does not matter, so return back what was sent
            return guiname

        # Important: it has to be really enabled in the main thread, so, schedule
        # it to run in the main thread.
        self.exec_queue.put(do_enable_gui)

    def get_ipython_hidden_vars_dict(self):
        return None


# =======================================================================================================================
# FakeFrame
# =======================================================================================================================
class FakeFrame:
    """
    Used to show console with variables connection.
    A class to be used as a mock of a frame.
    """
```
