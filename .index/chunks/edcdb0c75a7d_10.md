# Chunk: edcdb0c75a7d_10

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 622-682
- chunk: 11/20

```
o_pybreakpoint = file_to_id_to_breakpoint[canonical_normalized_filename] = {}

        id_to_pybreakpoint[breakpoint_id] = added_breakpoint
        py_db.consolidate_breakpoints(canonical_normalized_filename, id_to_pybreakpoint, file_to_line_to_breakpoints)
        if py_db.plugin is not None:
            py_db.has_plugin_line_breaks = py_db.plugin.has_line_breaks(py_db)
            py_db.plugin.after_breakpoints_consolidated(
                py_db, canonical_normalized_filename, id_to_pybreakpoint, file_to_line_to_breakpoints
            )

        py_db.on_breakpoints_changed()
        return result

    def reapply_breakpoints(self, py_db):
        """
        Reapplies all the received breakpoints as they were received by the API (so, new
        translations are applied).
        """
        pydev_log.debug("Reapplying breakpoints.")
        values = list(py_db.api_received_breakpoints.values())  # Create a copy with items to reapply.
        self.remove_all_breakpoints(py_db, "*")
        for val in values:
            _new_filename, api_add_breakpoint_params = val
            self.add_breakpoint(py_db, *api_add_breakpoint_params)

    def remove_all_breakpoints(self, py_db, received_filename):
        """
        Removes all the breakpoints from a given file or from all files if received_filename == '*'.

        :param str received_filename:
            Note: must be sent as it was received in the protocol. It may be translated in this
            function.
        """
        assert received_filename.__class__ == str  # i.e.: bytes on py2 and str on py3
        changed = False
        lst = [py_db.file_to_id_to_line_breakpoint, py_db.file_to_id_to_plugin_breakpoint, py_db.breakpoints]
        if hasattr(py_db, "django_breakpoints"):
            lst.append(py_db.django_breakpoints)

        if hasattr(py_db, "jinja2_breakpoints"):
            lst.append(py_db.jinja2_breakpoints)

        if received_filename == "*":
            py_db.api_received_breakpoints.clear()

            for file_to_id_to_breakpoint in lst:
                if file_to_id_to_breakpoint:
                    file_to_id_to_breakpoint.clear()
                    changed = True

        else:
            received_filename_normalized = pydevd_file_utils.normcase_from_client(received_filename)
            items = list(py_db.api_received_breakpoints.items())  # Create a copy to remove items.
            translated_filenames = []
            for key, val in items:
                original_filename_normalized, _breakpoint_id = key
                if original_filename_normalized == received_filename_normalized:
                    canonical_normalized_filename, _api_add_breakpoint_params = val
                    # Note: there can be actually 1:N mappings due to source mapping (i.e.: ipython).
                    translated_filenames.append(canonical_normalized_filename)
```
