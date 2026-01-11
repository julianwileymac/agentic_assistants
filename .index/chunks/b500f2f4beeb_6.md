# Chunk: b500f2f4beeb_6

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_concurrency_analyser/pydevd_concurrency_logger.py`
- lines: 364-434
- chunk: 7/8

```
r.get(str(task_id))

                    if method_name == "acquire":
                        if not self_obj._waiters and not self_obj.locked():
                            send_concurrency_message(
                                "asyncio_event",
                                event_time,
                                task_name,
                                task_name,
                                "lock",
                                method_name + "_begin",
                                frame.f_code.co_filename,
                                frame.f_lineno,
                                frame,
                                lock_id=str(id(self_obj)),
                            )
                        if self_obj.locked():
                            method_name += "_begin"
                        else:
                            method_name += "_end"
                    elif method_name == "release":
                        method_name += "_end"

                    send_concurrency_message(
                        "asyncio_event",
                        event_time,
                        task_name,
                        task_name,
                        "lock",
                        method_name,
                        frame.f_code.co_filename,
                        frame.f_lineno,
                        frame,
                        lock_id=str(id(self_obj)),
                    )

            if isinstance(self_obj, asyncio.Queue):
                if method_name in ("put", "get", "_put", "_get"):
                    task_id = self.get_task_id(frame)
                    task_name = self.task_mgr.get(str(task_id))

                    if method_name == "put":
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
                    elif method_name == "_put":
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
```
