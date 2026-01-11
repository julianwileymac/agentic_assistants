# Chunk: ac01e9f9eb6f_4

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/pydev_console_utils.py`
- lines: 269-361
- chunk: 5/9

```
True
                                sys.stderr.write("\nError when trying to update pydoc.help.input\n")
                                sys.stderr.write("(help() may not work -- please report this as a bug in the pydev bugtracker).\n\n")
                                traceback.print_exc()

                    try:
                        self.start_exec()
                        if hasattr(self, "debugger"):
                            self.debugger.enable_tracing()

                        more = self.do_add_exec(code_fragment)

                        if hasattr(self, "debugger"):
                            self.debugger.disable_tracing()

                        self.finish_exec(more)
                    finally:
                        if help is not None:
                            try:
                                try:
                                    help.input = original_in
                                except AttributeError:
                                    help._input = original_in
                            except:
                                pass

                finally:
                    sys.stdin = original_in
            except SystemExit:
                raise
            except:
                traceback.print_exc()
        finally:
            sys.__excepthook__ = sys.excepthook

        return more

    def do_add_exec(self, codeFragment):
        """
        Subclasses should override.

        @return: more (True if more input is needed to complete the statement and False if the statement is complete).
        """
        raise NotImplementedError()

    def get_namespace(self):
        """
        Subclasses should override.

        @return: dict with namespace.
        """
        raise NotImplementedError()

    def __resolve_reference__(self, text):
        """

        :type text: str
        """
        obj = None
        if "." not in text:
            try:
                obj = self.get_namespace()[text]
            except KeyError:
                pass

            if obj is None:
                try:
                    obj = self.get_namespace()["__builtins__"][text]
                except:
                    pass

            if obj is None:
                try:
                    obj = getattr(self.get_namespace()["__builtins__"], text, None)
                except:
                    pass

        else:
            try:
                last_dot = text.rindex(".")
                parent_context = text[0:last_dot]
                res = pydevd_vars.eval_in_context(parent_context, self.get_namespace(), self.get_namespace())
                obj = getattr(res, text[last_dot + 1 :])
            except:
                pass
        return obj

    def getDescription(self, text):
        try:
            obj = self.__resolve_reference__(text)
            if obj is None:
                return ""
```
