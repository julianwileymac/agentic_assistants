# Chunk: edcdb0c75a7d_5

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 329-400
- chunk: 6/20

```

        """
        py_db.post_method_as_internal_command(thread_id, internal_change_variable, seq, thread_id, frame_id, scope, attr, value)

    def request_get_variable(self, py_db, seq, thread_id, frame_id, scope, attrs):
        """
        :param scope: 'FRAME' or 'GLOBAL'
        """
        int_cmd = InternalGetVariable(seq, thread_id, frame_id, scope, attrs)
        py_db.post_internal_command(int_cmd, thread_id)

    def request_get_array(self, py_db, seq, roffset, coffset, rows, cols, fmt, thread_id, frame_id, scope, attrs):
        int_cmd = InternalGetArray(seq, roffset, coffset, rows, cols, fmt, thread_id, frame_id, scope, attrs)
        py_db.post_internal_command(int_cmd, thread_id)

    def request_load_full_value(self, py_db, seq, thread_id, frame_id, vars):
        int_cmd = InternalLoadFullValue(seq, thread_id, frame_id, vars)
        py_db.post_internal_command(int_cmd, thread_id)

    def request_get_description(self, py_db, seq, thread_id, frame_id, expression):
        py_db.post_method_as_internal_command(thread_id, internal_get_description, seq, thread_id, frame_id, expression)

    def request_get_frame(self, py_db, seq, thread_id, frame_id):
        py_db.post_method_as_internal_command(thread_id, internal_get_frame, seq, thread_id, frame_id)

    def to_str(self, s):
        """
        -- in py3 raises an error if it's not str already.
        """
        if s.__class__ != str:
            raise AssertionError("Expected to have str on Python 3. Found: %s (%s)" % (s, s.__class__))
        return s

    def filename_to_str(self, filename):
        """
        -- in py3 raises an error if it's not str already.
        """
        if filename.__class__ != str:
            raise AssertionError("Expected to have str on Python 3. Found: %s (%s)" % (filename, filename.__class__))
        return filename

    def filename_to_server(self, filename):
        filename = self.filename_to_str(filename)
        filename = pydevd_file_utils.map_file_to_server(filename)
        return filename

    class _DummyFrame(object):
        """
        Dummy frame to be used with PyDB.apply_files_filter (as we don't really have the
        related frame as breakpoints are added before execution).
        """

        class _DummyCode(object):
            def __init__(self, filename):
                self.co_firstlineno = 1
                self.co_filename = filename
                self.co_name = "invalid func name "

        def __init__(self, filename):
            self.f_code = self._DummyCode(filename)
            self.f_globals = {}

    ADD_BREAKPOINT_NO_ERROR = 0
    ADD_BREAKPOINT_FILE_NOT_FOUND = 1
    ADD_BREAKPOINT_FILE_EXCLUDED_BY_FILTERS = 2

    # This means that the breakpoint couldn't be fully validated (more runtime
    # information may be needed).
    ADD_BREAKPOINT_LAZY_VALIDATION = 3
    ADD_BREAKPOINT_INVALID_LINE = 4

```
