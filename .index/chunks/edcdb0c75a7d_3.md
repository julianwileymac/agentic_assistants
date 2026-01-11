# Chunk: edcdb0c75a7d_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 226-289
- chunk: 4/20

```
_tok, line=-1, column=-1):
        py_db.post_method_as_internal_command(
            thread_id, internal_get_completions, seq, thread_id, frame_id, act_tok, line=line, column=column
        )

    def request_stack(self, py_db, seq, thread_id, fmt=None, timeout=0.5, start_frame=0, levels=0):
        # If it's already suspended, get it right away.
        internal_get_thread_stack = InternalGetThreadStack(
            seq, thread_id, py_db, set_additional_thread_info, fmt=fmt, timeout=timeout, start_frame=start_frame, levels=levels
        )
        if internal_get_thread_stack.can_be_executed_by(get_current_thread_id(threading.current_thread())):
            internal_get_thread_stack.do_it(py_db)
        else:
            py_db.post_internal_command(internal_get_thread_stack, "*")

    def request_exception_info_json(self, py_db, request, thread_id, thread, max_frames):
        py_db.post_method_as_internal_command(
            thread_id,
            internal_get_exception_details_json,
            request,
            thread_id,
            thread,
            max_frames,
            set_additional_thread_info=set_additional_thread_info,
            iter_visible_frames_info=py_db.cmd_factory._iter_visible_frames_info,
        )

    def request_step(self, py_db, thread_id, step_cmd_id):
        t = pydevd_find_thread_by_id(thread_id)
        if t:
            py_db.post_method_as_internal_command(
                thread_id,
                internal_step_in_thread,
                thread_id,
                step_cmd_id,
                set_additional_thread_info=set_additional_thread_info,
            )
        elif thread_id.startswith("__frame__:"):
            sys.stderr.write("Can't make tasklet step command: %s\n" % (thread_id,))

    def request_smart_step_into(self, py_db, seq, thread_id, offset, child_offset):
        t = pydevd_find_thread_by_id(thread_id)
        if t:
            py_db.post_method_as_internal_command(
                thread_id, internal_smart_step_into, thread_id, offset, child_offset, set_additional_thread_info=set_additional_thread_info
            )
        elif thread_id.startswith("__frame__:"):
            sys.stderr.write("Can't set next statement in tasklet: %s\n" % (thread_id,))

    def request_smart_step_into_by_func_name(self, py_db, seq, thread_id, line, func_name):
        # Same thing as set next, just with a different cmd id.
        self.request_set_next(py_db, seq, thread_id, CMD_SMART_STEP_INTO, None, line, func_name)

    def request_set_next(self, py_db, seq, thread_id, set_next_cmd_id, original_filename, line, func_name):
        """
        set_next_cmd_id may actually be one of:

        CMD_RUN_TO_LINE
        CMD_SET_NEXT_STATEMENT

        CMD_SMART_STEP_INTO -- note: request_smart_step_into is preferred if it's possible
                               to work with bytecode offset.

```
