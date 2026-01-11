# Chunk: 74bddb2df6fd_13

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 932-1017
- chunk: 14/33

```
-----------------------
    # Command prompt input

    # Prompt the user for commands.
    def prompt_user(self):
        while not self.debuggerExit:
            try:
                self.cmdloop()
                break
            except CmdError:
                e = sys.exc_info()[1]
                print("*** Error: %s" % str(e))
            except Exception:
                traceback.print_exc()

    # #                self.debuggerExit = True

    # Prompt the user for a YES/NO kind of question.
    def ask_user(self, msg, prompt="Are you sure? (y/N): "):
        print(msg)
        answer = raw_input(prompt)
        answer = answer.strip()[:1].lower()
        return answer == "y"

    # Autocomplete the given command when not ambiguous.
    # Convert it to lowercase (so commands are seen as case insensitive).
    def autocomplete(self, cmd):
        cmd = cmd.lower()
        completed = self.completenames(cmd)
        if len(completed) == 1:
            cmd = completed[0]
        return cmd

    # Get the help text for the given list of command methods.
    # Note it's NOT a list of commands, but a list of actual method names.
    # Each line of text is stripped and all lines are sorted.
    # Repeated text lines are removed.
    # Returns a single, possibly multiline, string.
    def get_help(self, commands):
        msg = set()
        for name in commands:
            if name != "do_help":
                try:
                    doc = getattr(self, name).__doc__.split("\n")
                except Exception:
                    return "No help available when Python" " is run with the -OO switch."
                for x in doc:
                    x = x.strip()
                    if x:
                        msg.add("  %s" % x)
        msg = list(msg)
        msg.sort()
        msg = "\n".join(msg)
        return msg

    # Parse the prefix and remove it from the command line.
    def split_prefix(self, line):
        prefix = None
        if line.startswith("~"):
            pos = line.find(" ")
            if pos == 1:
                pos = line.find(" ", pos + 1)
            if not pos < 0:
                prefix = line[1:pos].strip()
                line = line[pos:].strip()
        return prefix, line

    # ------------------------------------------------------------------------------
    # Cmd() hacks

    # Header for help page.
    doc_header = "Available commands (type help * or help <command>)"

    # #    # Read and write directly to stdin and stdout.
    # #    # This prevents the use of raw_input and print.
    # #    use_rawinput = False

    @property
    def prompt(self):
        if self.lastEvent:
            pid = self.lastEvent.get_pid()
            tid = self.lastEvent.get_tid()
            if self.debug.is_debugee(pid):
                # #                return '~%d(%d)> ' % (tid, pid)
                return "%d:%d> " % (pid, tid)
```
