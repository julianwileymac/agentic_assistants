# Chunk: edcdb0c75a7d_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 159-232
- chunk: 3/20

```
e(self, py_db, msg):
        cmd = py_db.cmd_factory.make_warning_message("pydevd: %s\n" % (msg,))
        py_db.writer.add_command(cmd)

    def set_show_return_values(self, py_db, show_return_values):
        if show_return_values:
            py_db.show_return_values = True
        else:
            if py_db.show_return_values:
                # We should remove saved return values
                py_db.remove_return_values_flag = True
            py_db.show_return_values = False
        pydev_log.debug("Show return values: %s", py_db.show_return_values)

    def list_threads(self, py_db, seq):
        # Response is the command with the list of threads to be added to the writer thread.
        return py_db.cmd_factory.make_list_threads_message(py_db, seq)

    def request_suspend_thread(self, py_db, thread_id="*"):
        # Yes, thread suspend is done at this point, not through an internal command.
        threads = []
        suspend_all = thread_id.strip() == "*"
        if suspend_all:
            threads = pydevd_utils.get_non_pydevd_threads()

        elif thread_id.startswith("__frame__:"):
            sys.stderr.write("Can't suspend tasklet: %s\n" % (thread_id,))

        else:
            threads = [pydevd_find_thread_by_id(thread_id)]

        for t in threads:
            if t is None:
                continue
            py_db.set_suspend(
                t,
                CMD_THREAD_SUSPEND,
                suspend_other_threads=suspend_all,
                is_pause=True,
            )
            # Break here (even if it's suspend all) as py_db.set_suspend will
            # take care of suspending other threads.
            break

    def set_enable_thread_notifications(self, py_db, enable):
        """
        When disabled, no thread notifications (for creation/removal) will be
        issued until it's re-enabled.

        Note that when it's re-enabled, a creation notification will be sent for
        all existing threads even if it was previously sent (this is meant to
        be used on disconnect/reconnect).
        """
        py_db.set_enable_thread_notifications(enable)

    def request_disconnect(self, py_db, resume_threads):
        self.set_enable_thread_notifications(py_db, False)
        self.remove_all_breakpoints(py_db, "*")
        self.remove_all_exception_breakpoints(py_db)
        self.notify_disconnect(py_db)

        if resume_threads:
            self.request_resume_thread(thread_id="*")

    def request_resume_thread(self, thread_id):
        resume_threads(thread_id)

    def request_completions(self, py_db, seq, thread_id, frame_id, act_tok, line=-1, column=-1):
        py_db.post_method_as_internal_command(
            thread_id, internal_get_completions, seq, thread_id, frame_id, act_tok, line=line, column=column
        )

    def request_stack(self, py_db, seq, thread_id, fmt=None, timeout=0.5, start_frame=0, levels=0):
```
