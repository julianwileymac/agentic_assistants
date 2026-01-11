# Chunk: ac01e9f9eb6f_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/pydev_console_utils.py`
- lines: 132-210
- chunk: 3/9

```
= 1:
            self.__send_input_requested_message(True)
        try:
            yield
        finally:
            self._in_notification -= 1
            if self._in_notification == 0:
                self.__send_input_requested_message(False)

    def readline(self, *args, **kwargs):
        with self.notify_input_requested():
            return self.original_stdin.readline(*args, **kwargs)

    def read(self, *args, **kwargs):
        with self.notify_input_requested():
            return self.original_stdin.read(*args, **kwargs)


class CodeFragment:
    def __init__(self, text, is_single_line=True):
        self.text = text
        self.is_single_line = is_single_line

    def append(self, code_fragment):
        self.text = self.text + "\n" + code_fragment.text
        if not code_fragment.is_single_line:
            self.is_single_line = False


# =======================================================================================================================
# BaseInterpreterInterface
# =======================================================================================================================
class BaseInterpreterInterface:
    def __init__(self, mainThread, connect_status_queue=None):
        self.mainThread = mainThread
        self.interruptable = False
        self.exec_queue = _queue.Queue(0)
        self.buffer = None
        self.banner_shown = False
        self.connect_status_queue = connect_status_queue
        self.mpl_modules_for_patching = {}
        self.init_mpl_modules_for_patching()

    def build_banner(self):
        return "print({0})\n".format(repr(self.get_greeting_msg()))

    def get_greeting_msg(self):
        return "PyDev console: starting.\n"

    def init_mpl_modules_for_patching(self):
        from pydev_ipython.matplotlibtools import activate_matplotlib, activate_pylab, activate_pyplot

        self.mpl_modules_for_patching = {
            "matplotlib": lambda: activate_matplotlib(self.enableGui),
            "matplotlib.pyplot": activate_pyplot,
            "pylab": activate_pylab,
        }

    def need_more_for_code(self, source):
        # PyDev-502: PyDev 3.9 F2 doesn't support backslash continuations

        # Strangely even the IPython console is_complete said it was complete
        # even with a continuation char at the end.
        if source.endswith("\\"):
            return True

        if hasattr(self.interpreter, "is_complete"):
            return not self.interpreter.is_complete(source)
        try:
            # At this point, it should always be single.
            # If we don't do this, things as:
            #
            #     for i in range(10): print(i)
            #
            # (in a single line) don't work.
            # Note that it won't give an error and code will be None (so, it'll
            # use execMultipleLines in the next call in this case).
            symbol = "single"
```
