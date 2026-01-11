# Chunk: b500f2f4beeb_7

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_concurrency_analyser/pydevd_concurrency_logger.py`
- lines: 427-483
- chunk: 8/8

```
                          frame.f_lineno,
                            frame,
                            lock_id=str(id(self_obj)),
                        )
                        send_concurrency_message(
                            "asyncio_event",
                            event_time,
                            task_name,
                            task_name,
                            "lock",
                            "release",
                            frame.f_code.co_filename,
                            frame.f_lineno,
                            frame,
                            lock_id=str(id(self_obj)),
                        )
                    elif method_name == "get":
                        back = frame.f_back
                        if back.f_code.co_name != "send":
                            send_concurrency_message(
                                "asyncio_event",
                                event_time,
                                task_name,
                                task_name,
                                "lock",
                                "acquire_begin",
                                frame.f_code.co_filename,
                                frame.f_lineno,
                                frame,
                                lock_id=str(id(self_obj)),
                            )
                        else:
                            send_concurrency_message(
                                "asyncio_event",
                                event_time,
                                task_name,
                                task_name,
                                "lock",
                                "acquire_end",
                                frame.f_code.co_filename,
                                frame.f_lineno,
                                frame,
                                lock_id=str(id(self_obj)),
                            )
                            send_concurrency_message(
                                "asyncio_event",
                                event_time,
                                task_name,
                                task_name,
                                "lock",
                                "release",
                                frame.f_code.co_filename,
                                frame.f_lineno,
                                frame,
                                lock_id=str(id(self_obj)),
                            )
```
