# Chunk: edcdb0c75a7d_14

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 848-921
- chunk: 15/20

```
     notify_on_user_unhandled_exceptions=notify_on_user_unhandled_exceptions,
            notify_on_first_raise_only=notify_on_first_raise_only,
            ignore_libraries=ignore_libraries,
        )

        if exception_breakpoint is not None:
            py_db.on_breakpoints_changed()

    def add_plugins_exception_breakpoint(self, py_db, breakpoint_type, exception):
        supported_type = False
        plugin = py_db.get_plugin_lazy_init()
        if plugin is not None:
            supported_type = plugin.add_breakpoint("add_exception_breakpoint", py_db, breakpoint_type, exception)

        if supported_type:
            py_db.has_plugin_exception_breaks = py_db.plugin.has_exception_breaks(py_db)
            py_db.on_breakpoints_changed()
        else:
            raise NameError(breakpoint_type)

    def remove_python_exception_breakpoint(self, py_db, exception):
        try:
            cp = py_db.break_on_uncaught_exceptions.copy()
            cp.pop(exception, None)
            py_db.break_on_uncaught_exceptions = cp

            cp = py_db.break_on_caught_exceptions.copy()
            cp.pop(exception, None)
            py_db.break_on_caught_exceptions = cp

            cp = py_db.break_on_user_uncaught_exceptions.copy()
            cp.pop(exception, None)
            py_db.break_on_user_uncaught_exceptions = cp
        except:
            pydev_log.exception("Error while removing exception %s", sys.exc_info()[0])

        py_db.on_breakpoints_changed(removed=True)

    def remove_plugins_exception_breakpoint(self, py_db, exception_type, exception):
        # I.e.: no need to initialize lazy (if we didn't have it in the first place, we can't remove
        # anything from it anyways).
        plugin = py_db.plugin
        if plugin is None:
            return

        supported_type = plugin.remove_exception_breakpoint(py_db, exception_type, exception)

        if supported_type:
            py_db.has_plugin_exception_breaks = py_db.plugin.has_exception_breaks(py_db)
        else:
            pydev_log.info("No exception of type: %s was previously registered.", exception_type)

        py_db.on_breakpoints_changed(removed=True)

    def remove_all_exception_breakpoints(self, py_db):
        py_db.break_on_uncaught_exceptions = {}
        py_db.break_on_caught_exceptions = {}
        py_db.break_on_user_uncaught_exceptions = {}

        plugin = py_db.plugin
        if plugin is not None:
            plugin.remove_all_exception_breakpoints(py_db)
        py_db.on_breakpoints_changed(removed=True)

    def set_project_roots(self, py_db, project_roots):
        """
        :param str project_roots:
        """
        py_db.set_project_roots(project_roots)

    def set_stepping_resumes_all_threads(self, py_db, stepping_resumes_all_threads):
        py_db.stepping_resumes_all_threads = stepping_resumes_all_threads

```
