# Chunk: 7e6f1b19fdab_7

- source: `.venv-lab/Lib/site-packages/IPython/core/shellapp.py`
- lines: 482-501
- chunk: 8/8

```
       try:
                self._exec_file(fname, shell_futures=True)
            except:
                self.shell.showtraceback(tb_offset=4)
                if not self.interact:
                    self.exit(1)

    def _run_module(self):
        """Run module specified at the command-line."""
        if self.module_to_run:
            # Make sure that the module gets a proper sys.argv as if it were
            # run using `python -m`.
            save_argv = sys.argv
            sys.argv = [sys.executable] + self.extra_args
            try:
                self.shell.safe_run_module(self.module_to_run,
                                           self.shell.user_ns)
            finally:
                sys.argv = save_argv
```
