# Chunk: b500f2f4beeb_4

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_concurrency_analyser/pydevd_concurrency_logger.py`
- lines: 232-306
- chunk: 5/8

```
in QUEUE_METHODS):
                        real_method = frame.f_locals["attr"]
                        if method_name == "call_begin":
                            real_method += "_begin"
                        elif method_name == "call_end":
                            real_method += "_end"
                        else:
                            return
                        if real_method == "release_end":
                            # do not log release end. Maybe use it later
                            return
                        send_concurrency_message(
                            "threading_event",
                            event_time,
                            t.name,
                            get_thread_id(t),
                            "lock",
                            real_method,
                            back.f_code.co_filename,
                            back.f_lineno,
                            back,
                            lock_id=str(id(self_obj)),
                        )

                        if real_method in ("put_end", "get_end"):
                            # fake release for queue, cause we don't call it directly
                            send_concurrency_message(
                                "threading_event",
                                event_time,
                                t.name,
                                get_thread_id(t),
                                "lock",
                                "release",
                                back.f_code.co_filename,
                                back.f_lineno,
                                back,
                                lock_id=str(id(self_obj)),
                            )
                        # print(event_time, t.name, get_thread_id(t), "lock",
                        #       real_method, back.f_code.co_filename, back.f_lineno)

        except Exception:
            pydev_log.exception()


class NameManager:
    def __init__(self, name_prefix):
        self.tasks = {}
        self.last = 0
        self.prefix = name_prefix

    def get(self, id):
        if id not in self.tasks:
            self.last += 1
            self.tasks[id] = self.prefix + "-" + str(self.last)
        return self.tasks[id]


class AsyncioLogger:
    def __init__(self):
        self.task_mgr = NameManager("Task")
        self.coro_mgr = NameManager("Coro")
        self.start_time = cur_time()

    def get_task_id(self, frame):
        asyncio = sys.modules.get("asyncio")
        if asyncio is None:
            # If asyncio was not imported, there's nothing to be done
            # (also fixes issue where multiprocessing is imported due
            # to asyncio).
            return None
        while frame is not None:
            if "self" in frame.f_locals:
                self_obj = frame.f_locals["self"]
```
