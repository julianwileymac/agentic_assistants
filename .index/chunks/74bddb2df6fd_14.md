# Chunk: 74bddb2df6fd_14

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1009-1091
- chunk: 15/33

```

    def prompt(self):
        if self.lastEvent:
            pid = self.lastEvent.get_pid()
            tid = self.lastEvent.get_tid()
            if self.debug.is_debugee(pid):
                # #                return '~%d(%d)> ' % (tid, pid)
                return "%d:%d> " % (pid, tid)
        return "> "

    # Return a sorted list of method names.
    # Only returns the methods that implement commands.
    def get_names(self):
        names = Cmd.get_names(self)
        names = [x for x in set(names) if x.startswith("do_")]
        names.sort()
        return names

    # Automatically autocomplete commands, even if Tab wasn't pressed.
    # The prefix is removed from the line and stored in self.cmdprefix.
    # Also implement the commands that consist of a symbol character.
    def parseline(self, line):
        self.cmdprefix, line = self.split_prefix(line)
        line = line.strip()
        if line:
            if line[0] == ".":
                line = "plugin " + line[1:]
            elif line[0] == "#":
                line = "python " + line[1:]
        cmd, arg, line = Cmd.parseline(self, line)
        if cmd:
            cmd = self.autocomplete(cmd)
        return cmd, arg, line

    # #    # Don't repeat the last executed command.
    # #    def emptyline(self):
    # #        pass

    # Reset the defaults for some commands.
    def preloop(self):
        self.default_disasm_target = "eip"
        self.default_display_target = "eip"
        self.last_display_command = self.do_db

    # Put the prefix back in the command line.
    def get_lastcmd(self):
        return self.__lastcmd

    def set_lastcmd(self, lastcmd):
        if self.cmdprefix:
            lastcmd = "~%s %s" % (self.cmdprefix, lastcmd)
        self.__lastcmd = lastcmd

    lastcmd = property(get_lastcmd, set_lastcmd)

    # Quit the command prompt if the debuggerExit flag is on.
    def postcmd(self, stop, line):
        return stop or self.debuggerExit

    # ------------------------------------------------------------------------------
    # Commands

    # Each command contains a docstring with it's help text.
    # The help text consist of independent text lines,
    # where each line shows a command and it's parameters.
    # Each command method has the help message for itself and all it's aliases.
    # Only the docstring for the "help" command is shown as-is.

    # NOTE: Command methods MUST be all lowercase!

    # Extended help command.
    def do_help(self, arg):
        """
        ? - show the list of available commands
        ? * - show help for all commands
        ? <command> [command...] - show help for the given command(s)
        help - show the list of available commands
        help * - show help for all commands
        help <command> [command...] - show help for the given command(s)
        """
        if not arg:
            Cmd.do_help(self, arg)
```
