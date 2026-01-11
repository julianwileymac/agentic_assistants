# Chunk: 8c0cfafd38d0_6

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_stackless.py`
- lines: 378-413
- chunk: 7/7

```
w tasklets are properly tracked in the
    debugger.
    """
    global _application_set_schedule_callback
    _application_set_schedule_callback = stackless.set_schedule_callback(_schedule_callback)

    def set_schedule_callback(callable):
        global _application_set_schedule_callback
        old = _application_set_schedule_callback
        _application_set_schedule_callback = callable
        return old

    def get_schedule_callback():
        global _application_set_schedule_callback
        return _application_set_schedule_callback

    set_schedule_callback.__doc__ = stackless.set_schedule_callback.__doc__
    if hasattr(stackless, "get_schedule_callback"):
        get_schedule_callback.__doc__ = stackless.get_schedule_callback.__doc__
    stackless.set_schedule_callback = set_schedule_callback
    stackless.get_schedule_callback = get_schedule_callback

    if not hasattr(stackless.tasklet, "trace_function"):
        # Older versions of Stackless, released before 2014
        __call__.__doc__ = stackless.tasklet.__call__.__doc__
        stackless.tasklet.__call__ = __call__

        setup.__doc__ = stackless.tasklet.setup.__doc__
        stackless.tasklet.setup = setup

        run.__doc__ = stackless.run.__doc__
        stackless.run = run


patch_stackless = call_only_once(patch_stackless)
```
