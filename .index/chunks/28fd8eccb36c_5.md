# Chunk: 28fd8eccb36c_5

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_trace_dispatch_regular.py`
- lines: 336-409
- chunk: 6/9

```
nc(self):
        return self.trace_dispatch_and_unhandled_exceptions


# fmt: off
# IFDEF CYTHON
# cdef class ThreadTracer:
#     cdef public tuple _args;
#     def __init__(self, tuple args):
#         self._args = args
# ELSE
class ThreadTracer(object):
    def __init__(self, args):
        self._args = args

# ENDIF
# fmt: on

    def __call__(self, frame, event, arg):
        """This is the callback used when we enter some context in the debugger.

        We also decorate the thread we are in with info about the debugging.
        The attributes added are:
            pydev_state
            pydev_step_stop
            pydev_step_cmd
            pydev_notify_kill

        :param PyDB py_db:
            This is the global debugger (this method should actually be added as a method to it).
        """
        # fmt: off
        # IFDEF CYTHON
        # cdef str filename;
        # cdef str base;
        # cdef int pydev_step_cmd;
        # cdef object frame_cache_key;
        # cdef dict cache_skips;
        # cdef bint is_stepping;
        # cdef tuple abs_path_canonical_path_and_base;
        # cdef PyDBAdditionalThreadInfo additional_info;
        # ENDIF
        # fmt: on

        # DEBUG = 'code_to_debug' in frame.f_code.co_filename
        # if DEBUG: print('ENTER: trace_dispatch: %s %s %s %s' % (frame.f_code.co_filename, frame.f_lineno, event, frame.f_code.co_name))
        py_db, t, additional_info, cache_skips, frame_skips_cache = self._args
        if additional_info.is_tracing:
            return None if event == "call" else NO_FTRACE  # we don't wan't to trace code invoked from pydevd_frame.trace_dispatch

        additional_info.is_tracing += 1
        try:
            pydev_step_cmd = additional_info.pydev_step_cmd
            is_stepping = pydev_step_cmd != -1
            if py_db.pydb_disposed:
                return None if event == "call" else NO_FTRACE

            # if thread is not alive, cancel trace_dispatch processing
            if not is_thread_alive(t):
                py_db.notify_thread_not_alive(get_current_thread_id(t))
                return None if event == "call" else NO_FTRACE

            # Note: it's important that the context name is also given because we may hit something once
            # in the global context and another in the local context.
            frame_cache_key = frame.f_code
            if frame_cache_key in cache_skips:
                if not is_stepping:
                    # if DEBUG: print('skipped: trace_dispatch (cache hit)', frame_cache_key, frame.f_lineno, event, frame.f_code.co_name)
                    return None if event == "call" else NO_FTRACE
                else:
                    # When stepping we can't take into account caching based on the breakpoints (only global filtering).
                    if cache_skips.get(frame_cache_key) == 1:
                        if (
```
