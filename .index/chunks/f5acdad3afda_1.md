# Chunk: f5acdad3afda_1

- source: `.venv-lab/Lib/site-packages/ipywidgets/widgets/widget_output.py`
- lines: 80-160
- chunk: 2/3

```
s, **clear_kwargs):
        """
        Decorator to capture the stdout and stderr of a function.

        Parameters
        ----------

        clear_output: bool
            If True, clear the content of the output widget at every
            new function call. Default: False

        wait: bool
            If True, wait to clear the output until new output is
            available to replace it. This is only used if clear_output
            is also True.
            Default: False
        """
        def capture_decorator(func):
            @wraps(func)
            def inner(*args, **kwargs):
                if clear_output:
                    self.clear_output(*clear_args, **clear_kwargs)
                with self:
                    return func(*args, **kwargs)
            return inner
        return capture_decorator

    def __enter__(self):
        """Called upon entering output widget context manager."""
        self._flush()
        ip = get_ipython()
        kernel = None
        if ip and getattr(ip, "kernel", None) is not None:
            kernel = ip.kernel
        elif self.comm is not None and getattr(self.comm, 'kernel', None) is not None:
            kernel = self.comm.kernel

        if kernel:
            parent = None
            if hasattr(kernel, "get_parent"):
                parent = kernel.get_parent()
            elif hasattr(kernel, "_parent_header"):
                # ipykernel < 6: kernel._parent_header is the parent *request*
                parent = kernel._parent_header

            if parent and parent.get("header"):
                self.msg_id = parent["header"]["msg_id"]
                self.__counter += 1

    def __exit__(self, etype, evalue, tb):
        """Called upon exiting output widget context manager."""
        kernel = None
        if etype is not None:
            ip = get_ipython()
            if ip:
                kernel = ip
                ip.showtraceback((etype, evalue, tb), tb_offset=0)
            elif (self.comm is not None and
                    getattr(self.comm, "kernel", None) is not None and
                    # Check if it's ipykernel
                    getattr(self.comm.kernel, "send_response", None) is not None):
                kernel = self.comm.kernel
                kernel.send_response(kernel.iopub_socket,
                                     u'error',
                                     {
                    u'traceback': ["".join(traceback.format_exception(etype, evalue, tb))],
                    u'evalue': repr(evalue.args),
                    u'ename': etype.__name__
                    })
        self._flush()
        self.__counter -= 1
        if self.__counter == 0:
            self.msg_id = ''
        # suppress exceptions when in IPython, since they are shown above,
        # otherwise let someone else handle it
        return True if kernel else None

    def _flush(self):
        """Flush stdout and stderr buffers."""
        sys.stdout.flush()
```
