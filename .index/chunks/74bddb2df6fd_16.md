# Chunk: 74bddb2df6fd_16

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1153-1239
- chunk: 17/33

```
Type "help", "copyright", ' '"credits" or "license" for more information.\n'
        platform = winappdbg.version.lower()
        platform = "WinAppDbg %s" % platform
        banner = banner % (sys.version, platform)
        local = {}
        local.update(__builtins__)
        local.update(
            {
                "__name__": "__console__",
                "__doc__": None,
                "exit": self._python_exit,
                "self": self,
                "arg": arg,
                "winappdbg": winappdbg,
            }
        )
        try:
            code.interact(banner=banner, local=local)
        except SystemExit:
            # We need to catch it so it doesn't kill our program.
            pass

    def do_python(self, arg):
        """
        # - spawn a python interpreter
        python - spawn a python interpreter
        # <statement> - execute a single python statement
        python <statement> - execute a single python statement
        """
        if self.cmdprefix:
            raise CmdError("prefix not allowed")

        # When given a Python statement, execute it directly.
        if arg:
            try:
                compat.exec_(arg, globals(), locals())
            except Exception:
                traceback.print_exc()

        # When no statement is given, spawn a Python interpreter.
        else:
            try:
                self._spawn_python_shell(arg)
            except Exception:
                e = sys.exc_info()[1]
                raise CmdError("unhandled exception when running Python console: %s" % e)

    def do_quit(self, arg):
        """
        quit - close the debugging session
        q - close the debugging session
        """
        if self.cmdprefix:
            raise CmdError("prefix not allowed")
        if arg:
            raise CmdError("too many arguments")
        if self.confirm_quit:
            count = self.debug.get_debugee_count()
            if count > 0:
                if count == 1:
                    msg = "There's a program still running."
                else:
                    msg = "There are %s programs still running." % count
                if not self.ask_user(msg):
                    return False
        self.debuggerExit = True
        return True

    do_q = do_quit

    def do_attach(self, arg):
        """
        attach <target> [target...] - attach to the given process(es)
        """
        if self.cmdprefix:
            raise CmdError("prefix not allowed")
        targets = self.input_process_list(self.split_tokens(arg, 1))
        if not targets:
            print("Error: missing parameters")
        else:
            debug = self.debug
            for pid in targets:
                try:
                    debug.attach(pid)
                    print("Attached to process (%d)" % pid)
                except Exception:
```
