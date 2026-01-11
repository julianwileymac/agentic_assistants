# Chunk: ac01e9f9eb6f_7

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/pydev_console_utils.py`
- lines: 510-578
- chunk: 8/9

```
erver(), seq, var_objects)
        t.start()

    def changeVariable(self, attr, value):
        def do_change_variable():
            Exec("%s=%s" % (attr, value), self.get_namespace(), self.get_namespace())

        # Important: it has to be really enabled in the main thread, so, schedule
        # it to run in the main thread.
        self.exec_queue.put(do_change_variable)

    def connectToDebugger(self, debuggerPort, debugger_options=None):
        """
        Used to show console with variables connection.
        Mainly, monkey-patches things in the debugger structure so that the debugger protocol works.
        """

        if debugger_options is None:
            debugger_options = {}
        env_key = "PYDEVD_EXTRA_ENVS"
        if env_key in debugger_options:
            for env_name, value in debugger_options[env_key].items():
                existing_value = os.environ.get(env_name, None)
                if existing_value:
                    os.environ[env_name] = "%s%c%s" % (existing_value, os.path.pathsep, value)
                else:
                    os.environ[env_name] = value
                if env_name == "PYTHONPATH":
                    sys.path.append(value)

            del debugger_options[env_key]

        def do_connect_to_debugger():
            try:
                # Try to import the packages needed to attach the debugger
                import pydevd
                from _pydev_bundle._pydev_saved_modules import threading
            except:
                # This happens on Jython embedded in host eclipse
                traceback.print_exc()
                sys.stderr.write("pydevd is not available, cannot connect\n")

            from _pydevd_bundle.pydevd_constants import set_thread_id
            from _pydev_bundle import pydev_localhost

            set_thread_id(threading.current_thread(), "console_main")

            VIRTUAL_FRAME_ID = "1"  # matches PyStackFrameConsole.java
            VIRTUAL_CONSOLE_ID = "console_main"  # matches PyThreadConsole.java
            f = FakeFrame()
            f.f_back = None
            f.f_globals = {}  # As globals=locals here, let's simply let it empty (and save a bit of network traffic).
            f.f_locals = self.get_namespace()

            self.debugger = pydevd.PyDB()
            self.debugger.add_fake_frame(thread_id=VIRTUAL_CONSOLE_ID, frame_id=VIRTUAL_FRAME_ID, frame=f)
            try:
                pydevd.apply_debugger_options(debugger_options)
                self.debugger.connect(pydev_localhost.get_localhost(), debuggerPort)
                self.debugger.prepare_to_run()
                self.debugger.disable_tracing()
            except:
                traceback.print_exc()
                sys.stderr.write("Failed to connect to target debugger.\n")

            # Register to process commands when idle
            self.debugrunning = False
            try:
```
