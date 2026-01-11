# Chunk: b500f2f4beeb_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_concurrency_analyser/pydevd_concurrency_logger.py`
- lines: 136-190
- chunk: 3/8

```
              return
                name, _, back_base = pydevd_file_utils.get_abs_path_real_path_and_base_from_frame(back)
                event_time = cur_time() - self.start_time
                method_name = frame.f_code.co_name

                if isinstance(self_obj, threading.Thread):
                    if not hasattr(self_obj, "_pydev_run_patched"):
                        wrap_attr(self_obj, "run")
                    if (method_name in THREAD_METHODS) and (
                        back_base not in DONT_TRACE_THREADING or (method_name in INNER_METHODS and back_base in INNER_FILES)
                    ):
                        thread_id = get_thread_id(self_obj)
                        name = self_obj.getName()
                        real_method = frame.f_code.co_name
                        parent = None
                        if real_method == "_stop":
                            if back_base in INNER_FILES and back.f_code.co_name == "_wait_for_tstate_lock":
                                back = back.f_back.f_back
                            real_method = "stop"
                            if hasattr(self_obj, "_pydev_join_called"):
                                parent = get_thread_id(t)
                        elif real_method == "join":
                            # join called in the current thread, not in self object
                            if not self_obj.is_alive():
                                return
                            thread_id = get_thread_id(t)
                            name = t.name
                            self_obj._pydev_join_called = True

                        if real_method == "start":
                            parent = get_thread_id(t)
                        send_concurrency_message(
                            "threading_event",
                            event_time,
                            name,
                            thread_id,
                            "thread",
                            real_method,
                            back.f_code.co_filename,
                            back.f_lineno,
                            back,
                            parent=parent,
                        )
                        # print(event_time, self_obj.getName(), thread_id, "thread",
                        #       real_method, back.f_code.co_filename, back.f_lineno)

                if method_name == "pydev_after_run_call":
                    if hasattr(frame, "f_back") and frame.f_back is not None:
                        back = frame.f_back
                        if hasattr(back, "f_back") and back.f_back is not None:
                            back = back.f_back
                        if "self" in back.f_locals:
                            if isinstance(back.f_locals["self"], threading.Thread):
                                my_self_obj = frame.f_back.f_back.f_locals["self"]
```
