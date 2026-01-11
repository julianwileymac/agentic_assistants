# Chunk: edcdb0c75a7d_8

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 519-571
- chunk: 9/20

```
debug("Breakpoint (after source mapping) in: %s line: %s", source_mapped_filename, new_line)
            # Note that source mapping is internal and does not change the resulting filename nor line
            # (we want the outside world to see the line in the original file and not in the ipython
            # cell, otherwise the editor wouldn't be correct as the returned line is the line to
            # which the breakpoint will be moved in the editor).
            result = self._AddBreakpointResult(breakpoint_id, original_filename, line, original_line)

            # If a multi-mapping was applied, consider it the canonical / source mapped version (translated to ipython cell).
            translated_absolute_filename = source_mapped_filename
            canonical_normalized_filename = pydevd_file_utils.normcase(source_mapped_filename)
            line = new_line

        else:
            translated_absolute_filename = pydevd_file_utils.absolute_path(translated_filename)
            canonical_normalized_filename = pydevd_file_utils.canonical_normalized_path(translated_filename)

            if adjust_line and not translated_absolute_filename.startswith("<"):
                # Validate file_to_line_to_breakpoints and adjust their positions.
                try:
                    lines = sorted(_get_code_lines(translated_absolute_filename))
                except Exception:
                    pass
                else:
                    if line not in lines:
                        # Adjust to the first preceding valid line.
                        idx = bisect.bisect_left(lines, line)
                        if idx > 0:
                            line = lines[idx - 1]

            result = self._AddBreakpointResult(breakpoint_id, original_filename, line, original_line)

        py_db.api_received_breakpoints[(original_filename_normalized, breakpoint_id)] = (
            canonical_normalized_filename,
            api_add_breakpoint_params,
        )

        if not translated_absolute_filename.startswith("<"):
            # Note: if a mapping pointed to a file starting with '<', don't validate.

            if not pydevd_file_utils.exists(translated_absolute_filename):
                result.error_code = self.ADD_BREAKPOINT_FILE_NOT_FOUND
                return result

            if (
                py_db.is_files_filter_enabled
                and not py_db.get_require_module_for_filters()
                and py_db.apply_files_filter(self._DummyFrame(translated_absolute_filename), translated_absolute_filename, False)
            ):
                # Note that if `get_require_module_for_filters()` returns False, we don't do this check.
                # This is because we don't have the module name given a file at this point (in
                # runtime it's gotten from the frame.f_globals).
                # An option could be calculate it based on the filename and current sys.path,
```
