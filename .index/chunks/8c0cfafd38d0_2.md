# Chunk: 8c0cfafd38d0_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_stackless.py`
- lines: 144-214
- chunk: 3/7

```
klet_registered_to_info = {}


# =======================================================================================================================
# get_tasklet_info
# =======================================================================================================================
def get_tasklet_info(tasklet):
    return register_tasklet_info(tasklet)


# =======================================================================================================================
# register_tasklet_info
# =======================================================================================================================
def register_tasklet_info(tasklet):
    r = weakref.ref(tasklet)
    info = _weak_tasklet_registered_to_info.get(r)
    if info is None:
        info = _weak_tasklet_registered_to_info[r] = _TaskletInfo(r, tasklet)

    return info


_application_set_schedule_callback = None


# =======================================================================================================================
# _schedule_callback
# =======================================================================================================================
def _schedule_callback(prev, next):
    """
    Called when a context is stopped or a new context is made runnable.
    """
    try:
        if not prev and not next:
            return

        current_frame = sys._getframe()

        if next:
            register_tasklet_info(next)

            # Ok, making next runnable: set the tracing facility in it.
            debugger = get_global_debugger()
            if debugger is not None:
                next.trace_function = debugger.get_thread_local_trace_func()
                frame = next.frame
                if frame is current_frame:
                    frame = frame.f_back
                if hasattr(frame, "f_trace"):  # Note: can be None (but hasattr should cover for that too).
                    frame.f_trace = debugger.get_thread_local_trace_func()

            debugger = None

        if prev:
            register_tasklet_info(prev)

        try:
            for tasklet_ref, tasklet_info in list(_weak_tasklet_registered_to_info.items()):  # Make sure it's a copy!
                tasklet = tasklet_ref()
                if tasklet is None or not tasklet.alive:
                    # Garbage-collected already!
                    try:
                        del _weak_tasklet_registered_to_info[tasklet_ref]
                    except KeyError:
                        pass
                    if tasklet_info.frame_id is not None:
                        remove_custom_frame(tasklet_info.frame_id)
                else:
                    is_running = stackless.get_thread_info(tasklet.thread_id)[1] is tasklet
                    if tasklet is prev or (tasklet is not next and not is_running):
```
