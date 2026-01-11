# Chunk: edcdb0c75a7d_15

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 912-976
- chunk: 16/20

```
, py_db, project_roots):
        """
        :param str project_roots:
        """
        py_db.set_project_roots(project_roots)

    def set_stepping_resumes_all_threads(self, py_db, stepping_resumes_all_threads):
        py_db.stepping_resumes_all_threads = stepping_resumes_all_threads

    # Add it to the namespace so that it's available as PyDevdAPI.ExcludeFilter
    from _pydevd_bundle.pydevd_filtering import ExcludeFilter  # noqa

    def set_exclude_filters(self, py_db, exclude_filters):
        """
        :param list(PyDevdAPI.ExcludeFilter) exclude_filters:
        """
        py_db.set_exclude_filters(exclude_filters)

    def set_use_libraries_filter(self, py_db, use_libraries_filter):
        py_db.set_use_libraries_filter(use_libraries_filter)

    def request_get_variable_json(self, py_db, request, thread_id):
        """
        :param VariablesRequest request:
        """
        py_db.post_method_as_internal_command(thread_id, internal_get_variable_json, request)

    def request_change_variable_json(self, py_db, request, thread_id):
        """
        :param SetVariableRequest request:
        """
        py_db.post_method_as_internal_command(thread_id, internal_change_variable_json, request)

    def set_dont_trace_start_end_patterns(self, py_db, start_patterns, end_patterns):
        # Note: start/end patterns normalized internally.
        start_patterns = tuple(pydevd_file_utils.normcase(x) for x in start_patterns)
        end_patterns = tuple(pydevd_file_utils.normcase(x) for x in end_patterns)

        # After it's set the first time, we can still change it, but we need to reset the
        # related caches.
        reset_caches = False
        dont_trace_start_end_patterns_previously_set = py_db.dont_trace_external_files.__name__ == "custom_dont_trace_external_files"

        if not dont_trace_start_end_patterns_previously_set and not start_patterns and not end_patterns:
            # If it wasn't set previously and start and end patterns are empty we don't need to do anything.
            return

        if not py_db.is_cache_file_type_empty():
            # i.e.: custom function set in set_dont_trace_start_end_patterns.
            if dont_trace_start_end_patterns_previously_set:
                reset_caches = (
                    py_db.dont_trace_external_files.start_patterns != start_patterns
                    or py_db.dont_trace_external_files.end_patterns != end_patterns
                )

            else:
                reset_caches = True

        def custom_dont_trace_external_files(abs_path):
            normalized_abs_path = pydevd_file_utils.normcase(abs_path)
            return normalized_abs_path.startswith(start_patterns) or normalized_abs_path.endswith(end_patterns)

        custom_dont_trace_external_files.start_patterns = start_patterns
        custom_dont_trace_external_files.end_patterns = end_patterns
```
