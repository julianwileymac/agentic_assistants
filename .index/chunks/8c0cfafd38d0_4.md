# Chunk: 8c0cfafd38d0_4

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_stackless.py`
- lines: 264-324
- chunk: 5/7

```
ing next runnable: set the tracing facility in it.
                debugger = get_global_debugger()
                if debugger is not None and next.frame:
                    if hasattr(next.frame, "f_trace"):
                        next.frame.f_trace = debugger.get_thread_local_trace_func()
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
                        if tasklet.paused or tasklet.blocked or tasklet.scheduled:
                            if tasklet.frame and tasklet.frame.f_back:
                                f_back = tasklet.frame.f_back
                                debugger = get_global_debugger()
                                if debugger is not None and debugger.get_file_type(f_back) is None:
                                    if tasklet_info.frame_id is None:
                                        tasklet_info.frame_id = add_custom_frame(f_back, tasklet_info.tasklet_name, tasklet.thread_id)
                                    else:
                                        update_custom_frame(tasklet_info.frame_id, f_back, tasklet.thread_id)
                                debugger = None

                        elif tasklet.is_current:
                            if tasklet_info.frame_id is not None:
                                # Remove info about stackless suspended when it starts to run.
                                remove_custom_frame(tasklet_info.frame_id)
                                tasklet_info.frame_id = None

            finally:
                tasklet = None
                tasklet_info = None
                f_back = None

        except:
            pydev_log.exception()

        if _application_set_schedule_callback is not None:
            return _application_set_schedule_callback(prev, next)

    _original_setup = stackless.tasklet.setup

    # =======================================================================================================================
    # setup
    # =======================================================================================================================
    def setup(self, *args, **kwargs):
        """
        Called to run a new tasklet: rebind the creation so that we can trace it.
        """

```
