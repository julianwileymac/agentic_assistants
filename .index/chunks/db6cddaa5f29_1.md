# Chunk: db6cddaa5f29_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevconsole.py`
- lines: 87-173
- chunk: 2/8

```
face.__init__(self, mainThread, connect_status_queue)
        self.client_port = client_port
        self.host = host
        self.namespace = {}
        self.interpreter = InteractiveConsole(self.namespace)
        self._input_error_printed = False

    def do_add_exec(self, codeFragment):
        command = Command(self.interpreter, codeFragment)
        command.run()
        return command.more

    def get_namespace(self):
        return self.namespace

    def getCompletions(self, text, act_tok):
        try:
            from _pydev_bundle._pydev_completer import Completer

            completer = Completer(self.namespace, None)
            return completer.complete(act_tok)
        except:
            pydev_log.exception()
            return []

    def close(self):
        sys.exit(0)

    def get_greeting_msg(self):
        return "PyDev console: starting.\n"


class _ProcessExecQueueHelper:
    _debug_hook = None
    _return_control_osc = False


def set_debug_hook(debug_hook):
    _ProcessExecQueueHelper._debug_hook = debug_hook


def activate_mpl_if_already_imported(interpreter):
    if interpreter.mpl_modules_for_patching:
        for module in list(interpreter.mpl_modules_for_patching):
            if module in sys.modules:
                activate_function = interpreter.mpl_modules_for_patching.pop(module)
                activate_function()


def init_set_return_control_back(interpreter):
    from pydev_ipython.inputhook import set_return_control_callback

    def return_control():
        """A function that the inputhooks can call (via inputhook.stdin_ready()) to find
        out if they should cede control and return"""
        if _ProcessExecQueueHelper._debug_hook:
            # Some of the input hooks check return control without doing
            # a single operation, so we don't return True on every
            # call when the debug hook is in place to allow the GUI to run
            # XXX: Eventually the inputhook code will have diverged enough
            # from the IPython source that it will be worthwhile rewriting
            # it rather than pretending to maintain the old API
            _ProcessExecQueueHelper._return_control_osc = not _ProcessExecQueueHelper._return_control_osc
            if _ProcessExecQueueHelper._return_control_osc:
                return True

        if not interpreter.exec_queue.empty():
            return True
        return False

    set_return_control_callback(return_control)


def init_mpl_in_console(interpreter):
    init_set_return_control_back(interpreter)

    if not INTERACTIVE_MODE_AVAILABLE:
        return

    activate_mpl_if_already_imported(interpreter)
    from _pydev_bundle.pydev_import_hook import import_hook_manager

    for mod in list(interpreter.mpl_modules_for_patching):
        import_hook_manager.add_module_name(mod, interpreter.mpl_modules_for_patching.pop(mod))


```
