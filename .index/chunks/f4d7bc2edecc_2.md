# Chunk: f4d7bc2edecc_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_breakpoints.py`
- lines: 160-182
- chunk: 3/3

```
val_result = py_db.handle_breakpoint_condition(additional_info, exception_breakpoint, user_frame)
        if not eval_result:
            return

    if exception_breakpoint.expression is not None:
        py_db.handle_breakpoint_expression(exception_breakpoint, additional_info, user_frame)

    try:
        additional_info.pydev_message = exception_breakpoint.qname
    except:
        additional_info.pydev_message = exception_breakpoint.qname.encode("utf-8")

    pydev_log.debug("Handling post-mortem stop on exception breakpoint %s" % (exception_breakpoint.qname,))

    py_db.do_stop_on_unhandled_exception(thread, user_frame, frames_byid, arg)


def get_exception_class(kls):
    try:
        return eval(kls)
    except:
        return pydevd_import_class.import_name(kls)
```
