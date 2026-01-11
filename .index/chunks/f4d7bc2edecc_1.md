# Chunk: f4d7bc2edecc_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_breakpoints.py`
- lines: 79-167
- chunk: 2/3

```
logpoint=False):
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


def get_exception_breakpoint(exctype, exceptions):
    if not exctype:
        exception_full_qname = None
    else:
        exception_full_qname = str(exctype.__module__) + "." + exctype.__name__

    exc = None
    if exceptions is not None:
        try:
            return exceptions[exception_full_qname]
        except KeyError:
            for exception_breakpoint in exceptions.values():
                if exception_breakpoint.type is not None and issubclass(exctype, exception_breakpoint.type):
                    if exc is None or issubclass(exception_breakpoint.type, exc.type):
                        exc = exception_breakpoint
    return exc


def stop_on_unhandled_exception(py_db, thread, additional_info, arg):
    exctype, value, tb = arg
    break_on_uncaught_exceptions = py_db.break_on_uncaught_exceptions
    if break_on_uncaught_exceptions:
        exception_breakpoint = py_db.get_exception_breakpoint(exctype, break_on_uncaught_exceptions)
    else:
        exception_breakpoint = None

    if not exception_breakpoint:
        return

    if tb is None:  # sometimes it can be None, e.g. with GTK
        return

    if exctype is KeyboardInterrupt:
        return

    if exctype is SystemExit and py_db.ignore_system_exit_code(value):
        return

    frames = []
    user_frame = None

    while tb is not None:
        if not py_db.exclude_exception_by_filter(exception_breakpoint, tb):
            user_frame = tb.tb_frame
        frames.append(tb.tb_frame)
        tb = tb.tb_next

    if user_frame is None:
        return

    frames_byid = dict([(id(frame), frame) for frame in frames])
    add_exception_to_frame(user_frame, arg)
    if exception_breakpoint.condition is not None:
        eval_result = py_db.handle_breakpoint_condition(additional_info, exception_breakpoint, user_frame)
        if not eval_result:
            return

    if exception_breakpoint.expression is not None:
        py_db.handle_breakpoint_expression(exception_breakpoint, additional_info, user_frame)

```
