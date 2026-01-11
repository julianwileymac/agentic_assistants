# Chunk: edcdb0c75a7d_6

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 391-469
- chunk: 7/20

```
T_NO_ERROR = 0
    ADD_BREAKPOINT_FILE_NOT_FOUND = 1
    ADD_BREAKPOINT_FILE_EXCLUDED_BY_FILTERS = 2

    # This means that the breakpoint couldn't be fully validated (more runtime
    # information may be needed).
    ADD_BREAKPOINT_LAZY_VALIDATION = 3
    ADD_BREAKPOINT_INVALID_LINE = 4

    class _AddBreakpointResult(object):
        # :see: ADD_BREAKPOINT_NO_ERROR = 0
        # :see: ADD_BREAKPOINT_FILE_NOT_FOUND = 1
        # :see: ADD_BREAKPOINT_FILE_EXCLUDED_BY_FILTERS = 2
        # :see: ADD_BREAKPOINT_LAZY_VALIDATION = 3
        # :see: ADD_BREAKPOINT_INVALID_LINE = 4

        __slots__ = ["error_code", "breakpoint_id", "translated_filename", "translated_line", "original_line"]

        def __init__(self, breakpoint_id, translated_filename, translated_line, original_line):
            self.error_code = PyDevdAPI.ADD_BREAKPOINT_NO_ERROR
            self.breakpoint_id = breakpoint_id
            self.translated_filename = translated_filename
            self.translated_line = translated_line
            self.original_line = original_line

    def add_breakpoint(
        self,
        py_db,
        original_filename,
        breakpoint_type,
        breakpoint_id,
        line,
        condition,
        func_name,
        expression,
        suspend_policy,
        hit_condition,
        is_logpoint,
        adjust_line=False,
        on_changed_breakpoint_state=None,
    ):
        """
        :param str original_filename:
            Note: must be sent as it was received in the protocol. It may be translated in this
            function and its final value will be available in the returned _AddBreakpointResult.

        :param str breakpoint_type:
            One of: 'python-line', 'django-line', 'jinja2-line'.

        :param int breakpoint_id:

        :param int line:
            Note: it's possible that a new line was actually used. If that's the case its
            final value will be available in the returned _AddBreakpointResult.

        :param condition:
            Either None or the condition to activate the breakpoint.

        :param str func_name:
            If "None" (str), may hit in any context.
            Empty string will hit only top level.
            Any other value must match the scope of the method to be matched.

        :param str expression:
            None or the expression to be evaluated.

        :param suspend_policy:
            Either "NONE" (to suspend only the current thread when the breakpoint is hit) or
            "ALL" (to suspend all threads when a breakpoint is hit).

        :param str hit_condition:
            An expression where `@HIT@` will be replaced by the number of hits.
            i.e.: `@HIT@ == x` or `@HIT@ >= x`

        :param bool is_logpoint:
            If True and an expression is passed, pydevd will create an io message command with the
            result of the evaluation.

```
