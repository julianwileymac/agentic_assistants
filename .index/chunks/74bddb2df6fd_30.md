# Chunk: 74bddb2df6fd_30

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 2106-2196
- chunk: 31/33

```
     self.prompt_user()

    # Stop for breakpoint exceptions.
    def breakpoint(self, event):
        if hasattr(event, "breakpoint") and event.breakpoint:
            self.print_breakpoint_location(event)
        else:
            self.print_exception(event)
        self.prompt_user()

    # Stop for WOW64 breakpoint exceptions.
    def wow64_breakpoint(self, event):
        self.print_exception(event)
        self.prompt_user()

    # Stop for single step exceptions.
    def single_step(self, event):
        if event.debug.is_tracing(event.get_tid()):
            self.print_breakpoint_location(event)
        else:
            self.print_exception(event)
        self.prompt_user()

    # Don't stop for C++ exceptions.
    def ms_vc_exception(self, event):
        self.print_exception(event)
        event.continueStatus = win32.DBG_CONTINUE

    # Don't stop for process start.
    def create_process(self, event):
        self.print_process_start(event)
        self.print_thread_start(event)
        self.print_module_load(event)

    # Don't stop for process exit.
    def exit_process(self, event):
        self.print_process_end(event)

    # Don't stop for thread creation.
    def create_thread(self, event):
        self.print_thread_start(event)

    # Don't stop for thread exit.
    def exit_thread(self, event):
        self.print_thread_end(event)

    # Don't stop for DLL load.
    def load_dll(self, event):
        self.print_module_load(event)

    # Don't stop for DLL unload.
    def unload_dll(self, event):
        self.print_module_unload(event)

    # Don't stop for debug strings.
    def output_string(self, event):
        self.print_debug_string(event)

    # ------------------------------------------------------------------------------
    # History file

    def load_history(self):
        global readline
        if readline is None:
            try:
                import readline
            except ImportError:
                return
        if self.history_file_full_path is None:
            folder = os.environ.get("USERPROFILE", "")
            if not folder:
                folder = os.environ.get("HOME", "")
            if not folder:
                folder = os.path.split(sys.argv[0])[1]
            if not folder:
                folder = os.path.curdir
            self.history_file_full_path = os.path.join(folder, self.history_file)
        try:
            if os.path.exists(self.history_file_full_path):
                readline.read_history_file(self.history_file_full_path)
        except IOError:
            e = sys.exc_info()[1]
            warnings.warn("Cannot load history file, reason: %s" % str(e))

    def save_history(self):
        if self.history_file_full_path is not None:
            global readline
            if readline is None:
                try:
                    import readline
```
