# Chunk: 28fd8eccb36c_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_trace_dispatch_regular.py`
- lines: 153-219
- chunk: 3/9

```
one:
        # Important: don't call threadingCurrentThread if we're in the threading module
        # to avoid creating dummy threads.
        if py_db.threading_get_ident is not None:
            thread = py_db.threading_active.get(py_db.threading_get_ident())
            if thread is None:
                return None, False
        else:
            # Jython does not have threading.get_ident().
            thread = py_db.threading_current_thread()

    if getattr(thread, "pydev_do_not_trace", None):
        py_db.disable_tracing()
        return None, False

    try:
        additional_info = thread.additional_info
        if additional_info is None:
            raise AttributeError()
    except:
        additional_info = py_db.set_additional_thread_info(thread)

    # print('enter thread tracer', thread, get_current_thread_id(thread))
    args = (py_db, thread, additional_info, global_cache_skips, global_cache_frame_skips)

    if f_unhandled is not None:
        if f_unhandled.f_back is None and not force_only_unhandled_tracer:
            # Happens when we attach to a running program (cannot reuse instance because it's mutable).
            top_level_thread_tracer = TopLevelThreadTracerNoBackFrame(ThreadTracer(args), args)
            additional_info.top_level_thread_tracer_no_back_frames.append(
                top_level_thread_tracer
            )  # Hack for cython to keep it alive while the thread is alive (just the method in the SetTrace is not enough).
        else:
            top_level_thread_tracer = additional_info.top_level_thread_tracer_unhandled
            if top_level_thread_tracer is None:
                # Stop in some internal place to report about unhandled exceptions
                top_level_thread_tracer = TopLevelThreadTracerOnlyUnhandledExceptions(args)
                additional_info.top_level_thread_tracer_unhandled = top_level_thread_tracer  # Hack for cython to keep it alive while the thread is alive (just the method in the SetTrace is not enough).

        # print(' --> found to trace unhandled', f_unhandled.f_code.co_name, f_unhandled.f_code.co_filename, f_unhandled.f_code.co_firstlineno)
        f_trace = top_level_thread_tracer.get_trace_dispatch_func()
        # fmt: off
        # IFDEF CYTHON
        # f_trace = SafeCallWrapper(f_trace)
        # ENDIF
        # fmt: on
        f_unhandled.f_trace = f_trace

        if frame is f_unhandled:
            return f_trace, False

    thread_tracer = additional_info.thread_tracer
    if thread_tracer is None or thread_tracer._args[0] is not py_db:
        thread_tracer = ThreadTracer(args)
        additional_info.thread_tracer = thread_tracer

    # fmt: off
    # IFDEF CYTHON
    # return SafeCallWrapper(thread_tracer), True
    # ELSE
    return thread_tracer, True
    # ENDIF
    # fmt: on


def trace_dispatch(py_db, frame, event, arg):
```
