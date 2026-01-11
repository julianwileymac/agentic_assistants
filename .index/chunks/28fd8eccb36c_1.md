# Chunk: 28fd8eccb36c_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_trace_dispatch_regular.py`
- lines: 74-159
- chunk: 2/9

```
ne else None
#     def  get_method_object(self):
#         return self.method_object
# ELSE
# ENDIF
# fmt: on


def fix_top_level_trace_and_get_trace_func(py_db, frame):
    # fmt: off
    # IFDEF CYTHON
    # cdef str filename;
    # cdef str name;
    # cdef tuple args;
    # ENDIF
    # fmt: on

    # Note: this is always the first entry-point in the tracing for any thread.
    # After entering here we'll set a new tracing function for this thread
    # where more information is cached (and will also setup the tracing for
    # frames where we should deal with unhandled exceptions).
    thread = None
    # Cache the frame which should be traced to deal with unhandled exceptions.
    # (i.e.: thread entry-points).

    f_unhandled = frame
    # print('called at', f_unhandled.f_code.co_name, f_unhandled.f_code.co_filename, f_unhandled.f_code.co_firstlineno)
    force_only_unhandled_tracer = False
    while f_unhandled is not None:
        # name = splitext(basename(f_unhandled.f_code.co_filename))[0]

        name = f_unhandled.f_code.co_filename
        # basename
        i = name.rfind("/")
        j = name.rfind("\\")
        if j > i:
            i = j
        if i >= 0:
            name = name[i + 1 :]
        # remove ext
        i = name.rfind(".")
        if i >= 0:
            name = name[:i]

        if name == "threading":
            if f_unhandled.f_code.co_name in ("__bootstrap", "_bootstrap"):
                # We need __bootstrap_inner, not __bootstrap.
                return None, False

            elif f_unhandled.f_code.co_name in ("__bootstrap_inner", "_bootstrap_inner"):
                # Note: be careful not to use threading.currentThread to avoid creating a dummy thread.
                t = f_unhandled.f_locals.get("self")
                force_only_unhandled_tracer = True
                if t is not None and isinstance(t, threading.Thread):
                    thread = t
                    break

        elif name == "pydev_monkey":
            if f_unhandled.f_code.co_name == "__call__":
                force_only_unhandled_tracer = True
                break

        elif name == "pydevd":
            if f_unhandled.f_code.co_name in ("run", "main"):
                # We need to get to _exec
                return None, False

            if f_unhandled.f_code.co_name == "_exec":
                force_only_unhandled_tracer = True
                break

        elif name == "pydevd_tracing":
            return None, False

        elif f_unhandled.f_back is None:
            break

        f_unhandled = f_unhandled.f_back

    if thread is None:
        # Important: don't call threadingCurrentThread if we're in the threading module
        # to avoid creating dummy threads.
        if py_db.threading_get_ident is not None:
            thread = py_db.threading_active.get(py_db.threading_get_ident())
            if thread is None:
```
