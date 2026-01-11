# Chunk: 8c0cfafd38d0_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_stackless.py`
- lines: 209-269
- chunk: 4/7

```
et_info.frame_id is not None:
                        remove_custom_frame(tasklet_info.frame_id)
                else:
                    is_running = stackless.get_thread_info(tasklet.thread_id)[1] is tasklet
                    if tasklet is prev or (tasklet is not next and not is_running):
                        # the tasklet won't run after this scheduler action:
                        # - the tasklet is the previous tasklet
                        # - it is not the next tasklet and it is not an already running tasklet
                        frame = tasklet.frame
                        if frame is current_frame:
                            frame = frame.f_back
                        if frame is not None:
                            # print >>sys.stderr, "SchedCB: %r, %d, '%s', '%s'" % (tasklet, frame.f_lineno, _filename, base)
                            debugger = get_global_debugger()
                            if debugger is not None and debugger.get_file_type(frame) is None:
                                tasklet_info.update_name()
                                if tasklet_info.frame_id is None:
                                    tasklet_info.frame_id = add_custom_frame(frame, tasklet_info.tasklet_name, tasklet.thread_id)
                                else:
                                    update_custom_frame(tasklet_info.frame_id, frame, tasklet.thread_id, name=tasklet_info.tasklet_name)
                            debugger = None

                    elif tasklet is next or is_running:
                        if tasklet_info.frame_id is not None:
                            # Remove info about stackless suspended when it starts to run.
                            remove_custom_frame(tasklet_info.frame_id)
                            tasklet_info.frame_id = None

        finally:
            tasklet = None
            tasklet_info = None
            frame = None

    except:
        pydev_log.exception()

    if _application_set_schedule_callback is not None:
        return _application_set_schedule_callback(prev, next)


if not hasattr(stackless.tasklet, "trace_function"):
    # Older versions of Stackless, released before 2014
    # This code does not work reliable! It is affected by several
    # stackless bugs: Stackless issues #44, #42, #40
    def _schedule_callback(prev, next):
        """
        Called when a context is stopped or a new context is made runnable.
        """
        try:
            if not prev and not next:
                return

            if next:
                register_tasklet_info(next)

                # Ok, making next runnable: set the tracing facility in it.
                debugger = get_global_debugger()
                if debugger is not None and next.frame:
                    if hasattr(next.frame, "f_trace"):
                        next.frame.f_trace = debugger.get_thread_local_trace_func()
```
