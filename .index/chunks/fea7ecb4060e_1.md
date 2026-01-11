# Chunk: fea7ecb4060e_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_plugins/pydevd_line_validation.py`
- lines: 57-106
- chunk: 2/3

```
normalized_filename_to_last_template_lines[canonical_normalized_filename] = valid_lines_frozenset, sorted_lines
        self._verify_breakpoints_with_lines_collected(
            py_db, canonical_normalized_filename, template_breakpoints_for_file, valid_lines_frozenset, sorted_lines
        )

    def verify_breakpoints_from_template_cached_lines(self, py_db, canonical_normalized_filename, template_breakpoints_for_file):
        """
        This is used when the lines are already available (if just the template is available,
        `verify_breakpoints` should be used instead).
        """
        cached = self._canonical_normalized_filename_to_last_template_lines.get(canonical_normalized_filename)
        if cached is not None:
            valid_lines_frozenset, sorted_lines = cached
            self._verify_breakpoints_with_lines_collected(
                py_db, canonical_normalized_filename, template_breakpoints_for_file, valid_lines_frozenset, sorted_lines
            )

    def _verify_breakpoints_with_lines_collected(
        self, py_db, canonical_normalized_filename, template_breakpoints_for_file, valid_lines_frozenset, sorted_lines
    ):
        for line, template_bp in list(template_breakpoints_for_file.items()):  # Note: iterate in a copy (we may mutate it).
            if template_bp.verified_cache_key != valid_lines_frozenset:
                template_bp.verified_cache_key = valid_lines_frozenset
                valid = line in valid_lines_frozenset

                if not valid:
                    new_line = -1
                    if sorted_lines:
                        # Adjust to the first preceding valid line.
                        idx = bisect.bisect_left(sorted_lines, line)
                        if idx > 0:
                            new_line = sorted_lines[idx - 1]

                    if new_line >= 0 and new_line not in template_breakpoints_for_file:
                        # We just add it if found and if there's no existing breakpoint at that
                        # location.
                        if (
                            template_bp.add_breakpoint_result.error_code != PyDevdAPI.ADD_BREAKPOINT_NO_ERROR
                            and template_bp.add_breakpoint_result.translated_line != new_line
                        ):
                            pydev_log.debug(
                                "Template breakpoint in %s in line: %s moved to line: %s", canonical_normalized_filename, line, new_line
                            )
                            template_bp.add_breakpoint_result.error_code = PyDevdAPI.ADD_BREAKPOINT_NO_ERROR
                            template_bp.add_breakpoint_result.translated_line = new_line

                            # Add it to a new line.
                            template_breakpoints_for_file.pop(line, None)
                            template_breakpoints_for_file[new_line] = template_bp
```
