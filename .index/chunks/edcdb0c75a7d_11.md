# Chunk: edcdb0c75a7d_11

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 678-736
- chunk: 12/20

```
 received_filename_normalized:
                    canonical_normalized_filename, _api_add_breakpoint_params = val
                    # Note: there can be actually 1:N mappings due to source mapping (i.e.: ipython).
                    translated_filenames.append(canonical_normalized_filename)
                    del py_db.api_received_breakpoints[key]

            for canonical_normalized_filename in translated_filenames:
                for file_to_id_to_breakpoint in lst:
                    if canonical_normalized_filename in file_to_id_to_breakpoint:
                        file_to_id_to_breakpoint.pop(canonical_normalized_filename, None)
                        changed = True

        if changed:
            py_db.on_breakpoints_changed(removed=True)

    def remove_breakpoint(self, py_db, received_filename, breakpoint_type, breakpoint_id):
        """
        :param str received_filename:
            Note: must be sent as it was received in the protocol. It may be translated in this
            function.

        :param str breakpoint_type:
            One of: 'python-line', 'django-line', 'jinja2-line'.

        :param int breakpoint_id:
        """
        received_filename_normalized = pydevd_file_utils.normcase_from_client(received_filename)
        for key, val in list(py_db.api_received_breakpoints.items()):
            original_filename_normalized, existing_breakpoint_id = key
            _new_filename, _api_add_breakpoint_params = val
            if received_filename_normalized == original_filename_normalized and existing_breakpoint_id == breakpoint_id:
                del py_db.api_received_breakpoints[key]
                break
        else:
            pydev_log.info("Did not find breakpoint to remove: %s (breakpoint id: %s)", received_filename, breakpoint_id)

        file_to_id_to_breakpoint = None
        received_filename = self.filename_to_server(received_filename)
        canonical_normalized_filename = pydevd_file_utils.canonical_normalized_path(received_filename)

        if breakpoint_type == "python-line":
            file_to_line_to_breakpoints = py_db.breakpoints
            file_to_id_to_breakpoint = py_db.file_to_id_to_line_breakpoint

        elif py_db.plugin is not None:
            result = py_db.plugin.get_breakpoints(py_db, breakpoint_type)
            if result is not None:
                file_to_id_to_breakpoint = py_db.file_to_id_to_plugin_breakpoint
                file_to_line_to_breakpoints = result

        if file_to_id_to_breakpoint is None:
            pydev_log.critical("Error removing breakpoint. Cannot handle breakpoint of type %s", breakpoint_type)

        else:
            try:
                id_to_pybreakpoint = file_to_id_to_breakpoint.get(canonical_normalized_filename, {})
                if DebugInfoHolder.DEBUG_TRACE_LEVEL >= 1:
                    existing = id_to_pybreakpoint[breakpoint_id]
```
