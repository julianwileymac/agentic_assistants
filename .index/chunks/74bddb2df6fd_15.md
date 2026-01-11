# Chunk: 74bddb2df6fd_15

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1084-1160
- chunk: 16/33

```
ommand> [command...] - show help for the given command(s)
        help - show the list of available commands
        help * - show help for all commands
        help <command> [command...] - show help for the given command(s)
        """
        if not arg:
            Cmd.do_help(self, arg)
        elif arg in ("?", "help"):
            # An easter egg :)
            print("  Help! I need somebody...")
            print("  Help! Not just anybody...")
            print("  Help! You know, I need someone...")
            print("  Heeelp!")
        else:
            if arg == "*":
                commands = self.get_names()
                commands = [x for x in commands if x.startswith("do_")]
            else:
                commands = set()
                for x in arg.split(" "):
                    x = x.strip()
                    if x:
                        for n in self.completenames(x):
                            commands.add("do_%s" % n)
                commands = list(commands)
                commands.sort()
            print(self.get_help(commands))

    def do_shell(self, arg):
        """
        ! - spawn a system shell
        shell - spawn a system shell
        ! <command> [arguments...] - execute a single shell command
        shell <command> [arguments...] - execute a single shell command
        """
        if self.cmdprefix:
            raise CmdError("prefix not allowed")

        # Try to use the environment to locate cmd.exe.
        # If not found, it's usually OK to just use the filename,
        # since cmd.exe is one of those "magic" programs that
        # can be automatically found by CreateProcess.
        shell = os.getenv("ComSpec", "cmd.exe")

        # When given a command, run it and return.
        # When no command is given, spawn a shell.
        if arg:
            arg = "%s /c %s" % (shell, arg)
        else:
            arg = shell
        process = self.debug.system.start_process(arg, bConsole=True)
        process.wait()

    # This hack fixes a bug in Python, the interpreter console is closing the
    # stdin pipe when calling the exit() function (Ctrl+Z seems to work fine).
    class _PythonExit(object):
        def __repr__(self):
            return "Use exit() or Ctrl-Z plus Return to exit"

        def __call__(self):
            raise SystemExit()

    _python_exit = _PythonExit()

    # Spawns a Python shell with some handy local variables and the winappdbg
    # module already imported. Also the console banner is improved.
    def _spawn_python_shell(self, arg):
        import winappdbg

        banner = 'Python %s on %s\nType "help", "copyright", ' '"credits" or "license" for more information.\n'
        platform = winappdbg.version.lower()
        platform = "WinAppDbg %s" % platform
        banner = banner % (sys.version, platform)
        local = {}
        local.update(__builtins__)
        local.update(
```
