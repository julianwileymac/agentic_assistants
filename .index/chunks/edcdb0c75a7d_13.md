# Chunk: edcdb0c75a7d_13

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 779-856
- chunk: 14/20

```
xec(seq, thread_id, frame_id, expression)
        py_db.post_internal_command(int_cmd, thread_id)

    def request_load_source(self, py_db, seq, filename):
        """
        :param str filename:
            Note: must be sent as it was received in the protocol. It may be translated in this
            function.
        """
        try:
            filename = self.filename_to_server(filename)
            assert filename.__class__ == str  # i.e.: bytes on py2 and str on py3

            with tokenize.open(filename) as stream:
                source = stream.read()
            cmd = py_db.cmd_factory.make_load_source_message(seq, source)
        except:
            cmd = py_db.cmd_factory.make_error_message(seq, get_exception_traceback_str())

        py_db.writer.add_command(cmd)

    def get_decompiled_source_from_frame_id(self, py_db, frame_id):
        """
        :param py_db:
        :param frame_id:
        :throws Exception:
            If unable to get the frame in the currently paused frames or if some error happened
            when decompiling.
        """
        variable = py_db.suspended_frames_manager.get_variable(int(frame_id))
        frame = variable.value

        # Check if it's in the linecache first.
        lines = (linecache.getline(frame.f_code.co_filename, i) for i in itertools.count(1))
        lines = itertools.takewhile(bool, lines)  # empty lines are '\n', EOF is ''

        source = "".join(lines)
        if not source:
            source = code_to_bytecode_representation(frame.f_code)

        return source

    def request_load_source_from_frame_id(self, py_db, seq, frame_id):
        try:
            source = self.get_decompiled_source_from_frame_id(py_db, frame_id)
            cmd = py_db.cmd_factory.make_load_source_from_frame_id_message(seq, source)
        except:
            cmd = py_db.cmd_factory.make_error_message(seq, get_exception_traceback_str())

        py_db.writer.add_command(cmd)

    def add_python_exception_breakpoint(
        self,
        py_db,
        exception,
        condition,
        expression,
        notify_on_handled_exceptions,
        notify_on_unhandled_exceptions,
        notify_on_user_unhandled_exceptions,
        notify_on_first_raise_only,
        ignore_libraries,
    ):
        exception_breakpoint = py_db.add_break_on_exception(
            exception,
            condition=condition,
            expression=expression,
            notify_on_handled_exceptions=notify_on_handled_exceptions,
            notify_on_unhandled_exceptions=notify_on_unhandled_exceptions,
            notify_on_user_unhandled_exceptions=notify_on_user_unhandled_exceptions,
            notify_on_first_raise_only=notify_on_first_raise_only,
            ignore_libraries=ignore_libraries,
        )

        if exception_breakpoint is not None:
            py_db.on_breakpoints_changed()

```
