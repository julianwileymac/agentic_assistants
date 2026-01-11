# Chunk: edcdb0c75a7d_7

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 462-522
- chunk: 8/20

```
      An expression where `@HIT@` will be replaced by the number of hits.
            i.e.: `@HIT@ == x` or `@HIT@ >= x`

        :param bool is_logpoint:
            If True and an expression is passed, pydevd will create an io message command with the
            result of the evaluation.

        :param bool adjust_line:
            If True, the breakpoint line should be adjusted if the current line doesn't really
            match an executable line (if possible).

        :param callable on_changed_breakpoint_state:
            This is called when something changed internally on the breakpoint after it was initially
            added (for instance, template file_to_line_to_breakpoints could be signaled as invalid initially and later
            when the related template is loaded, if the line is valid it could be marked as valid).

            The signature for the callback should be:
                on_changed_breakpoint_state(breakpoint_id: int, add_breakpoint_result: _AddBreakpointResult)

                Note that the add_breakpoint_result should not be modified by the callback (the
                implementation may internally reuse the same instance multiple times).

        :return _AddBreakpointResult:
        """
        assert original_filename.__class__ == str, "Expected str, found: %s" % (
            original_filename.__class__,
        )  # i.e.: bytes on py2 and str on py3

        original_filename_normalized = pydevd_file_utils.normcase_from_client(original_filename)

        pydev_log.debug("Request for breakpoint in: %s line: %s", original_filename, line)
        original_line = line
        # Parameters to reapply breakpoint.
        api_add_breakpoint_params = (
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
        )

        translated_filename = self.filename_to_server(original_filename)  # Apply user path mapping.
        pydev_log.debug("Breakpoint (after path translation) in: %s line: %s", translated_filename, line)
        func_name = self.to_str(func_name)

        assert translated_filename.__class__ == str  # i.e.: bytes on py2 and str on py3
        assert func_name.__class__ == str  # i.e.: bytes on py2 and str on py3

        # Apply source mapping (i.e.: ipython).
        source_mapped_filename, new_line, multi_mapping_applied = py_db.source_mapping.map_to_server(translated_filename, line)

        if multi_mapping_applied:
            pydev_log.debug("Breakpoint (after source mapping) in: %s line: %s", source_mapped_filename, new_line)
            # Note that source mapping is internal and does not change the resulting filename nor line
            # (we want the outside world to see the line in the original file and not in the ipython
```
