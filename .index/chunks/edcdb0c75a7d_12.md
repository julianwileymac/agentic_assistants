# Chunk: edcdb0c75a7d_12

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 729-786
- chunk: 13/20

```
point of type %s", breakpoint_type)

        else:
            try:
                id_to_pybreakpoint = file_to_id_to_breakpoint.get(canonical_normalized_filename, {})
                if DebugInfoHolder.DEBUG_TRACE_LEVEL >= 1:
                    existing = id_to_pybreakpoint[breakpoint_id]
                    pydev_log.info(
                        "Removed breakpoint:%s - line:%s - func_name:%s (id: %s)\n"
                        % (canonical_normalized_filename, existing.line, existing.func_name, breakpoint_id)
                    )

                del id_to_pybreakpoint[breakpoint_id]
                py_db.consolidate_breakpoints(canonical_normalized_filename, id_to_pybreakpoint, file_to_line_to_breakpoints)
                if py_db.plugin is not None:
                    py_db.has_plugin_line_breaks = py_db.plugin.has_line_breaks(py_db)
                    py_db.plugin.after_breakpoints_consolidated(
                        py_db, canonical_normalized_filename, id_to_pybreakpoint, file_to_line_to_breakpoints
                    )

            except KeyError:
                pydev_log.info(
                    "Error removing breakpoint: Breakpoint id not found: %s id: %s. Available ids: %s\n",
                    canonical_normalized_filename,
                    breakpoint_id,
                    list(id_to_pybreakpoint),
                )

        py_db.on_breakpoints_changed(removed=True)

    def set_function_breakpoints(self, py_db, function_breakpoints):
        function_breakpoint_name_to_breakpoint = {}
        for function_breakpoint in function_breakpoints:
            function_breakpoint_name_to_breakpoint[function_breakpoint.func_name] = function_breakpoint

        py_db.function_breakpoint_name_to_breakpoint = function_breakpoint_name_to_breakpoint
        py_db.on_breakpoints_changed()

    def request_exec_or_evaluate(self, py_db, seq, thread_id, frame_id, expression, is_exec, trim_if_too_big, attr_to_set_result):
        py_db.post_method_as_internal_command(
            thread_id, internal_evaluate_expression, seq, thread_id, frame_id, expression, is_exec, trim_if_too_big, attr_to_set_result
        )

    def request_exec_or_evaluate_json(self, py_db, request, thread_id):
        py_db.post_method_as_internal_command(thread_id, internal_evaluate_expression_json, request, thread_id)

    def request_set_expression_json(self, py_db, request, thread_id):
        py_db.post_method_as_internal_command(thread_id, internal_set_expression_json, request, thread_id)

    def request_console_exec(self, py_db, seq, thread_id, frame_id, expression):
        int_cmd = InternalConsoleExec(seq, thread_id, frame_id, expression)
        py_db.post_internal_command(int_cmd, thread_id)

    def request_load_source(self, py_db, seq, filename):
        """
        :param str filename:
            Note: must be sent as it was received in the protocol. It may be translated in this
```
