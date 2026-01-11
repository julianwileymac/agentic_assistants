# Chunk: f4d7bc2edecc_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_breakpoints.py`
- lines: 1-87
- chunk: 1/3

```
from _pydev_bundle import pydev_log
from _pydevd_bundle import pydevd_import_class
from _pydevd_bundle.pydevd_frame_utils import add_exception_to_frame
from _pydev_bundle._pydev_saved_modules import threading


class ExceptionBreakpoint(object):
    def __init__(
        self,
        qname,
        condition,
        expression,
        notify_on_handled_exceptions,
        notify_on_unhandled_exceptions,
        notify_on_user_unhandled_exceptions,
        notify_on_first_raise_only,
        ignore_libraries,
    ):
        exctype = get_exception_class(qname)
        self.qname = qname
        if exctype is not None:
            self.name = exctype.__name__
        else:
            self.name = None

        self.condition = condition
        self.expression = expression
        self.notify_on_unhandled_exceptions = notify_on_unhandled_exceptions
        self.notify_on_handled_exceptions = notify_on_handled_exceptions
        self.notify_on_first_raise_only = notify_on_first_raise_only
        self.notify_on_user_unhandled_exceptions = notify_on_user_unhandled_exceptions
        self.ignore_libraries = ignore_libraries

        self.type = exctype

    def __str__(self):
        return self.qname

    @property
    def has_condition(self):
        return self.condition is not None

    def handle_hit_condition(self, frame):
        return False


class LineBreakpoint(object):
    def __init__(self, breakpoint_id, line, condition, func_name, expression, suspend_policy="NONE", hit_condition=None, is_logpoint=False):
        self.breakpoint_id = breakpoint_id
        self.line = line
        self.condition = condition
        self.func_name = func_name
        self.expression = expression
        self.suspend_policy = suspend_policy
        self.hit_condition = hit_condition
        self._hit_count = 0
        self._hit_condition_lock = threading.Lock()
        self.is_logpoint = is_logpoint

    @property
    def has_condition(self):
        return bool(self.condition) or bool(self.hit_condition)

    def handle_hit_condition(self, frame):
        if not self.hit_condition:
            return False
        ret = False
        with self._hit_condition_lock:
            self._hit_count += 1
            expr = self.hit_condition.replace("@HIT@", str(self._hit_count))
            try:
                ret = bool(eval(expr, frame.f_globals, frame.f_locals))
            except Exception:
                ret = False
        return ret


class FunctionBreakpoint(object):
    def __init__(self, func_name, condition, expression, suspend_policy="NONE", hit_condition=None, is_logpoint=False):
        self.condition = condition
        self.func_name = func_name
        self.expression = expression
        self.suspend_policy = suspend_policy
        self.hit_condition = hit_condition
        self._hit_count = 0
        self._hit_condition_lock = threading.Lock()
```
