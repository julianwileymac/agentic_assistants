# Chunk: b500f2f4beeb_5

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_concurrency_analyser/pydevd_concurrency_logger.py`
- lines: 299-371
- chunk: 6/8

```
io was not imported, there's nothing to be done
            # (also fixes issue where multiprocessing is imported due
            # to asyncio).
            return None
        while frame is not None:
            if "self" in frame.f_locals:
                self_obj = frame.f_locals["self"]
                if isinstance(self_obj, asyncio.Task):
                    method_name = frame.f_code.co_name
                    if method_name == "_step":
                        return id(self_obj)
            frame = frame.f_back
        return None

    def log_event(self, frame):
        event_time = cur_time() - self.start_time

        # Debug loop iterations
        # if isinstance(self_obj, asyncio.base_events.BaseEventLoop):
        #     if method_name == "_run_once":
        #         print("Loop iteration")

        if not hasattr(frame, "f_back") or frame.f_back is None:
            return

        asyncio = sys.modules.get("asyncio")
        if asyncio is None:
            # If asyncio was not imported, there's nothing to be done
            # (also fixes issue where multiprocessing is imported due
            # to asyncio).
            return

        back = frame.f_back

        if "self" in frame.f_locals:
            self_obj = frame.f_locals["self"]
            if isinstance(self_obj, asyncio.Task):
                method_name = frame.f_code.co_name
                if method_name == "set_result":
                    task_id = id(self_obj)
                    task_name = self.task_mgr.get(str(task_id))
                    send_concurrency_message(
                        "asyncio_event", event_time, task_name, task_name, "thread", "stop", frame.f_code.co_filename, frame.f_lineno, frame
                    )

                method_name = back.f_code.co_name
                if method_name == "__init__":
                    task_id = id(self_obj)
                    task_name = self.task_mgr.get(str(task_id))
                    send_concurrency_message(
                        "asyncio_event",
                        event_time,
                        task_name,
                        task_name,
                        "thread",
                        "start",
                        frame.f_code.co_filename,
                        frame.f_lineno,
                        frame,
                    )

            method_name = frame.f_code.co_name
            if isinstance(self_obj, asyncio.Lock):
                if method_name in ("acquire", "release"):
                    task_id = self.get_task_id(frame)
                    task_name = self.task_mgr.get(str(task_id))

                    if method_name == "acquire":
                        if not self_obj._waiters and not self_obj.locked():
                            send_concurrency_message(
                                "asyncio_event",
                                event_time,
```
