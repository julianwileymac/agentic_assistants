# Chunk: 7e6f1b19fdab_4

- source: `.venv-lab/Lib/site-packages/IPython/core/shellapp.py`
- lines: 289-368
- chunk: 5/8

```

            key = self.gui

        if not enable:
            return

        try:
            r = enable(key)
        except ImportError:
            self.log.warning("Eventloop or matplotlib integration failed. Is matplotlib installed?")
            self.shell.showtraceback()
            return
        except Exception:
            self.log.warning("GUI event loop or pylab initialization failed")
            self.shell.showtraceback()
            return

        if isinstance(r, tuple):
            gui, backend = r[:2]
            self.log.info("Enabling GUI event loop integration, "
                      "eventloop=%s, matplotlib=%s", gui, backend)
            if key == "auto":
                print("Using matplotlib backend: %s" % backend)
        else:
            gui = r
            self.log.info("Enabling GUI event loop integration, "
                      "eventloop=%s", gui)

    def init_extensions(self):
        """Load all IPython extensions in IPythonApp.extensions.

        This uses the :meth:`ExtensionManager.load_extensions` to load all
        the extensions listed in ``self.extensions``.
        """
        try:
            self.log.debug("Loading IPython extensions...")
            extensions = (
                self.default_extensions + self.extensions + self.extra_extensions
            )
            for ext in extensions:
                try:
                    self.log.info("Loading IPython extension: %s", ext)
                    self.shell.extension_manager.load_extension(ext)
                except:
                    if self.reraise_ipython_extension_failures:
                        raise
                    msg = ("Error in loading extension: {ext}\n"
                           "Check your config files in {location}".format(
                               ext=ext,
                               location=self.profile_dir.location
                           ))
                    self.log.warning(msg, exc_info=True)
        except:
            if self.reraise_ipython_extension_failures:
                raise
            self.log.warning("Unknown error in loading extensions:", exc_info=True)

    def init_code(self):
        """run the pre-flight code, specified via exec_lines"""
        self._run_startup_files()
        self._run_exec_lines()
        self._run_exec_files()

        # Hide variables defined here from %who etc.
        if self.hide_initial_ns:
            self.shell.user_ns_hidden.update(self.shell.user_ns)

        # command-line execution (ipython -i script.py, ipython -m module)
        # should *not* be excluded from %whos
        self._run_cmd_line_code()
        self._run_module()

        # flush output, so itwon't be attached to the first cell
        sys.stdout.flush()
        sys.stderr.flush()
        self.shell._sys_modules_keys = set(sys.modules.keys())

    def _run_exec_lines(self):
        """Run lines of code in IPythonApp.exec_lines in the user's namespace."""
```
