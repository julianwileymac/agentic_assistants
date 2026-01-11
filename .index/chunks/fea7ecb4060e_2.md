# Chunk: fea7ecb4060e_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_plugins/pydevd_line_validation.py`
- lines: 101-121
- chunk: 3/3

```
                         template_bp.add_breakpoint_result.translated_line = new_line

                            # Add it to a new line.
                            template_breakpoints_for_file.pop(line, None)
                            template_breakpoints_for_file[new_line] = template_bp
                            template_bp.on_changed_breakpoint_state(template_bp.breakpoint_id, template_bp.add_breakpoint_result)
                    else:
                        if template_bp.add_breakpoint_result.error_code != PyDevdAPI.ADD_BREAKPOINT_INVALID_LINE:
                            pydev_log.debug(
                                "Template breakpoint in %s in line: %s invalid (valid lines: %s)",
                                canonical_normalized_filename,
                                line,
                                valid_lines_frozenset,
                            )
                            template_bp.add_breakpoint_result.error_code = PyDevdAPI.ADD_BREAKPOINT_INVALID_LINE
                            template_bp.on_changed_breakpoint_state(template_bp.breakpoint_id, template_bp.add_breakpoint_result)
                else:
                    if template_bp.add_breakpoint_result.error_code != PyDevdAPI.ADD_BREAKPOINT_NO_ERROR:
                        template_bp.add_breakpoint_result.error_code = PyDevdAPI.ADD_BREAKPOINT_NO_ERROR
                        template_bp.on_changed_breakpoint_state(template_bp.breakpoint_id, template_bp.add_breakpoint_result)
```
