# Chunk: b500f2f4beeb_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_concurrency_analyser/pydevd_concurrency_logger.py`
- lines: 185-238
- chunk: 4/8

```
and back.f_back is not None:
                            back = back.f_back
                        if "self" in back.f_locals:
                            if isinstance(back.f_locals["self"], threading.Thread):
                                my_self_obj = frame.f_back.f_back.f_locals["self"]
                                my_back = frame.f_back.f_back
                                my_thread_id = get_thread_id(my_self_obj)
                                send_massage = True
                                if hasattr(my_self_obj, "_pydev_join_called"):
                                    send_massage = False
                                    # we can't detect stop after join in Python 2 yet
                                if send_massage:
                                    send_concurrency_message(
                                        "threading_event",
                                        event_time,
                                        "Thread",
                                        my_thread_id,
                                        "thread",
                                        "stop",
                                        my_back.f_code.co_filename,
                                        my_back.f_lineno,
                                        my_back,
                                        parent=None,
                                    )

                if self_obj.__class__ == ObjectWrapper:
                    if back_base in DONT_TRACE_THREADING:
                        # do not trace methods called from threading
                        return
                    back_back_base = pydevd_file_utils.get_abs_path_real_path_and_base_from_frame(back.f_back)[2]
                    back = back.f_back
                    if back_back_base in DONT_TRACE_THREADING:
                        # back_back_base is the file, where the method was called froms
                        return
                    if method_name == "__init__":
                        send_concurrency_message(
                            "threading_event",
                            event_time,
                            t.name,
                            get_thread_id(t),
                            "lock",
                            method_name,
                            back.f_code.co_filename,
                            back.f_lineno,
                            back,
                            lock_id=str(id(frame.f_locals["self"])),
                        )
                    if "attr" in frame.f_locals and (frame.f_locals["attr"] in LOCK_METHODS or frame.f_locals["attr"] in QUEUE_METHODS):
                        real_method = frame.f_locals["attr"]
                        if method_name == "call_begin":
                            real_method += "_begin"
                        elif method_name == "call_end":
                            real_method += "_end"
```
