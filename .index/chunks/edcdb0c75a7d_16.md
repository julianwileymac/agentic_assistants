# Chunk: edcdb0c75a7d_16

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 971-1045
- chunk: 17/20

```
 = pydevd_file_utils.normcase(abs_path)
            return normalized_abs_path.startswith(start_patterns) or normalized_abs_path.endswith(end_patterns)

        custom_dont_trace_external_files.start_patterns = start_patterns
        custom_dont_trace_external_files.end_patterns = end_patterns
        py_db.dont_trace_external_files = custom_dont_trace_external_files

        if reset_caches:
            py_db.clear_dont_trace_start_end_patterns_caches()

    def stop_on_entry(self):
        main_thread = pydevd_utils.get_main_thread()
        if main_thread is None:
            pydev_log.critical("Could not find main thread while setting Stop on Entry.")
        else:
            info = set_additional_thread_info(main_thread)
            info.pydev_original_step_cmd = CMD_STOP_ON_START
            info.pydev_step_cmd = CMD_STEP_INTO_MY_CODE
            info.update_stepping_info()
            if PYDEVD_USE_SYS_MONITORING:
                pydevd_sys_monitoring.update_monitor_events(suspend_requested=True)
                pydevd_sys_monitoring.restart_events()

    def set_ignore_system_exit_codes(self, py_db, ignore_system_exit_codes):
        py_db.set_ignore_system_exit_codes(ignore_system_exit_codes)

    SourceMappingEntry = pydevd_source_mapping.SourceMappingEntry

    def set_source_mapping(self, py_db, source_filename, mapping):
        """
        :param str source_filename:
            The filename for the source mapping (bytes on py2 and str on py3).
            This filename will be made absolute in this function.

        :param list(SourceMappingEntry) mapping:
            A list with the source mapping entries to be applied to the given filename.

        :return str:
            An error message if it was not possible to set the mapping or an empty string if
            everything is ok.
        """
        source_filename = self.filename_to_server(source_filename)
        absolute_source_filename = pydevd_file_utils.absolute_path(source_filename)
        for map_entry in mapping:
            map_entry.source_filename = absolute_source_filename
        error_msg = py_db.source_mapping.set_source_mapping(absolute_source_filename, mapping)
        if error_msg:
            return error_msg

        self.reapply_breakpoints(py_db)
        return ""

    def set_variable_presentation(self, py_db, variable_presentation):
        assert isinstance(variable_presentation, self.VariablePresentation)
        py_db.variable_presentation = variable_presentation

    def get_ppid(self):
        """
        Provides the parent pid (even for older versions of Python on Windows).
        """
        ppid = None

        try:
            ppid = os.getppid()
        except AttributeError:
            pass

        if ppid is None and IS_WINDOWS:
            ppid = self._get_windows_ppid()

        return ppid

    def _get_windows_ppid(self):
        this_pid = os.getpid()
```
