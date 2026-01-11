# Chunk: a8ff7ab556df_2

- source: `.venv-lab/Lib/site-packages/IPython/core/debugger_backport.py`
- lines: 131-207
- chunk: 3/3

```
       except Exception:
            return False
        code = ns["__pdb_outer"]()

        cells = tuple(types.CellType(locals_copy.get(var)) for var in code.co_freevars)

        try:
            exec(code, globals, locals_copy, closure=cells)
        except Exception:
            return False

        # get the data we need from the statement
        pdb_eval = locals_copy["__pdb_eval__"]

        # __pdb_eval__ should not be updated back to locals
        pdb_eval["write_back"].pop("__pdb_eval__")

        # Write all local variables back to locals
        locals.update(pdb_eval["write_back"])
        eval_result = pdb_eval["result"]
        if eval_result is not None:
            print(repr(eval_result))

        return True

    def default(self, line):  # type: ignore[no-untyped-def]
        if line[:1] == "!":
            line = line[1:].strip()
        locals = self.curframe_locals
        globals = self.curframe.f_globals
        try:
            buffer = line
            if (
                code := codeop.compile_command(line + "\n", "<stdin>", "single")
            ) is None:
                # Multi-line mode
                with self._disable_command_completion():
                    buffer = line
                    continue_prompt = "...   "
                    while (
                        code := codeop.compile_command(buffer, "<stdin>", "single")
                    ) is None:
                        if self.use_rawinput:
                            try:
                                line = input(continue_prompt)
                            except (EOFError, KeyboardInterrupt):
                                self.lastcmd = ""
                                print("\n")
                                return
                        else:
                            self.stdout.write(continue_prompt)
                            self.stdout.flush()
                            line = self.stdin.readline()
                            if not len(line):
                                self.lastcmd = ""
                                self.stdout.write("\n")
                                self.stdout.flush()
                                return
                            else:
                                line = line.rstrip("\r\n")
                        buffer += "\n" + line
            save_stdout = sys.stdout
            save_stdin = sys.stdin
            save_displayhook = sys.displayhook
            try:
                sys.stdin = self.stdin
                sys.stdout = self.stdout
                sys.displayhook = self.displayhook
                if not self._exec_in_closure(buffer, globals, locals):
                    exec(code, globals, locals)
            finally:
                sys.stdout = save_stdout
                sys.stdin = save_stdin
                sys.displayhook = save_displayhook
        except:
            self._error_exc()
```
