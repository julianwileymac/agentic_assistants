# Chunk: edcdb0c75a7d_9

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 567-627
- chunk: 10/20

```
)` returns False, we don't do this check.
                # This is because we don't have the module name given a file at this point (in
                # runtime it's gotten from the frame.f_globals).
                # An option could be calculate it based on the filename and current sys.path,
                # but on some occasions that may be wrong (for instance with `__main__` or if
                # the user dynamically changes the PYTHONPATH).

                # Note: depending on the use-case, filters may be changed, so, keep on going and add the
                # breakpoint even with the error code.
                result.error_code = self.ADD_BREAKPOINT_FILE_EXCLUDED_BY_FILTERS

        if breakpoint_type == "python-line":
            added_breakpoint = LineBreakpoint(
                breakpoint_id, line, condition, func_name, expression, suspend_policy, hit_condition=hit_condition, is_logpoint=is_logpoint
            )

            file_to_line_to_breakpoints = py_db.breakpoints
            file_to_id_to_breakpoint = py_db.file_to_id_to_line_breakpoint
            supported_type = True

        else:
            add_plugin_breakpoint_result = None
            plugin = py_db.get_plugin_lazy_init()
            if plugin is not None:
                add_plugin_breakpoint_result = plugin.add_breakpoint(
                    "add_line_breakpoint",
                    py_db,
                    breakpoint_type,
                    canonical_normalized_filename,
                    breakpoint_id,
                    line,
                    condition,
                    expression,
                    func_name,
                    hit_condition=hit_condition,
                    is_logpoint=is_logpoint,
                    add_breakpoint_result=result,
                    on_changed_breakpoint_state=on_changed_breakpoint_state,
                )

            if add_plugin_breakpoint_result is not None:
                supported_type = True
                added_breakpoint, file_to_line_to_breakpoints = add_plugin_breakpoint_result
                file_to_id_to_breakpoint = py_db.file_to_id_to_plugin_breakpoint
            else:
                supported_type = False

        if not supported_type:
            raise NameError(breakpoint_type)

        pydev_log.debug("Added breakpoint:%s - line:%s - func_name:%s\n", canonical_normalized_filename, line, func_name)

        if canonical_normalized_filename in file_to_id_to_breakpoint:
            id_to_pybreakpoint = file_to_id_to_breakpoint[canonical_normalized_filename]
        else:
            id_to_pybreakpoint = file_to_id_to_breakpoint[canonical_normalized_filename] = {}

        id_to_pybreakpoint[breakpoint_id] = added_breakpoint
        py_db.consolidate_breakpoints(canonical_normalized_filename, id_to_pybreakpoint, file_to_line_to_breakpoints)
        if py_db.plugin is not None:
```
