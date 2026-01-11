# Chunk: 28fd8eccb36c_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_trace_dispatch_regular.py`
- lines: 206-285
- chunk: 4/9

```
ead_tracer = ThreadTracer(args)
        additional_info.thread_tracer = thread_tracer

    # fmt: off
    # IFDEF CYTHON
    # return SafeCallWrapper(thread_tracer), True
    # ELSE
    return thread_tracer, True
    # ENDIF
    # fmt: on


def trace_dispatch(py_db, frame, event, arg):
    thread_trace_func, apply_to_settrace = py_db.fix_top_level_trace_and_get_trace_func(py_db, frame)
    if thread_trace_func is None:
        return None if event == "call" else NO_FTRACE
    if apply_to_settrace:
        py_db.enable_tracing(thread_trace_func)
    return thread_trace_func(frame, event, arg)


# fmt: off
# IFDEF CYTHON
# cdef class TopLevelThreadTracerOnlyUnhandledExceptions:
#     cdef public tuple _args;
#     def __init__(self, tuple args):
#         self._args = args
# ELSE
class TopLevelThreadTracerOnlyUnhandledExceptions(object):
    def __init__(self, args):
        self._args = args

# ENDIF
# fmt: on

    def trace_unhandled_exceptions(self, frame, event, arg):
        # Note that we ignore the frame as this tracing method should only be put in topmost frames already.
        # print('trace_unhandled_exceptions', event, frame.f_code.co_name, frame.f_code.co_filename, frame.f_code.co_firstlineno)
        if event == "exception" and arg is not None:
            py_db, t, additional_info = self._args[0:3]
            if arg is not None:
                if not additional_info.suspended_at_unhandled:
                    additional_info.suspended_at_unhandled = True

                    py_db.stop_on_unhandled_exception(py_db, t, additional_info, arg)

        # No need to reset frame.f_trace to keep the same trace function.
        return self.trace_unhandled_exceptions

    def get_trace_dispatch_func(self):
        return self.trace_unhandled_exceptions

# fmt: off
# IFDEF CYTHON
# cdef class TopLevelThreadTracerNoBackFrame:
#
#     cdef public object _frame_trace_dispatch;
#     cdef public tuple _args;
#     cdef public object try_except_infos;
#     cdef public object _last_exc_arg;
#     cdef public set _raise_lines;
#     cdef public int _last_raise_line;
#
#     def __init__(self, frame_trace_dispatch, tuple args):
#         self._frame_trace_dispatch = frame_trace_dispatch
#         self._args = args
#         self.try_except_infos = None
#         self._last_exc_arg = None
#         self._raise_lines = set()
#         self._last_raise_line = -1
# ELSE
class TopLevelThreadTracerNoBackFrame(object):
    """
    This tracer is pretty special in that it's dealing with a frame without f_back (i.e.: top frame
    on remote attach or QThread).

    This means that we have to carefully inspect exceptions to discover whether the exception will
    be unhandled or not (if we're dealing with an unhandled exception we need to stop as unhandled,
    otherwise we need to use the regular tracer -- unfortunately the debugger has little info to
```
