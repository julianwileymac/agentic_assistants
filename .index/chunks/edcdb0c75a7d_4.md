# Chunk: edcdb0c75a7d_4

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 279-337
- chunk: 5/20

```
, line, func_name):
        """
        set_next_cmd_id may actually be one of:

        CMD_RUN_TO_LINE
        CMD_SET_NEXT_STATEMENT

        CMD_SMART_STEP_INTO -- note: request_smart_step_into is preferred if it's possible
                               to work with bytecode offset.

        :param Optional[str] original_filename:
            If available, the filename may be source translated, otherwise no translation will take
            place (the set next just needs the line afterwards as it executes locally, but for
            the Jupyter integration, the source mapping may change the actual lines and not only
            the filename).
        """
        t = pydevd_find_thread_by_id(thread_id)
        if t:
            if original_filename is not None:
                translated_filename = self.filename_to_server(original_filename)  # Apply user path mapping.
                pydev_log.debug("Set next (after path translation) in: %s line: %s", translated_filename, line)
                func_name = self.to_str(func_name)

                assert translated_filename.__class__ == str  # i.e.: bytes on py2 and str on py3
                assert func_name.__class__ == str  # i.e.: bytes on py2 and str on py3

                # Apply source mapping (i.e.: ipython).
                _source_mapped_filename, new_line, multi_mapping_applied = py_db.source_mapping.map_to_server(translated_filename, line)
                if multi_mapping_applied:
                    pydev_log.debug("Set next (after source mapping) in: %s line: %s", translated_filename, line)
                    line = new_line

            int_cmd = InternalSetNextStatementThread(thread_id, set_next_cmd_id, line, func_name, seq=seq)
            py_db.post_internal_command(int_cmd, thread_id)
        elif thread_id.startswith("__frame__:"):
            sys.stderr.write("Can't set next statement in tasklet: %s\n" % (thread_id,))

    def request_reload_code(self, py_db, seq, module_name, filename):
        """
        :param seq: if -1 no message will be sent back when the reload is done.

        Note: either module_name or filename may be None (but not both at the same time).
        """
        thread_id = "*"  # Any thread
        # Note: not going for the main thread because in this case it'd only do the load
        # when we stopped on a breakpoint.
        py_db.post_method_as_internal_command(thread_id, internal_reload_code, seq, module_name, filename)

    def request_change_variable(self, py_db, seq, thread_id, frame_id, scope, attr, value):
        """
        :param scope: 'FRAME' or 'GLOBAL'
        """
        py_db.post_method_as_internal_command(thread_id, internal_change_variable, seq, thread_id, frame_id, scope, attr, value)

    def request_get_variable(self, py_db, seq, thread_id, frame_id, scope, attrs):
        """
        :param scope: 'FRAME' or 'GLOBAL'
        """
```
