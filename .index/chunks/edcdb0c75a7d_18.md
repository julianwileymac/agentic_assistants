# Chunk: edcdb0c75a7d_18

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 1099-1170
- chunk: 19/20

```
_new = False

            for pid in children_pids:
                if pid not in previously_found:
                    found_new = True
                    previously_found.add(pid)
                    self._call(["kill", "-KILL", str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if not found_new:
                break

    def _popen(self, cmdline, **kwargs):
        try:
            return subprocess.Popen(cmdline, **kwargs)
        except:
            if DebugInfoHolder.DEBUG_TRACE_LEVEL >= 1:
                pydev_log.exception("Error running: %s" % (" ".join(cmdline)))
            return None

    def _call(self, cmdline, **kwargs):
        try:
            subprocess.check_call(cmdline, **kwargs)
        except:
            if DebugInfoHolder.DEBUG_TRACE_LEVEL >= 1:
                pydev_log.exception("Error running: %s" % (" ".join(cmdline)))

    def set_terminate_child_processes(self, py_db, terminate_child_processes):
        py_db.terminate_child_processes = terminate_child_processes

    def set_terminate_keyboard_interrupt(self, py_db, terminate_keyboard_interrupt):
        py_db.terminate_keyboard_interrupt = terminate_keyboard_interrupt

    def terminate_process(self, py_db):
        """
        Terminates the current process (and child processes if the option to also terminate
        child processes is enabled).
        """
        try:
            if py_db.terminate_child_processes:
                pydev_log.debug("Terminating child processes.")
                if IS_WINDOWS:
                    self._terminate_child_processes_windows(py_db.dont_terminate_child_pids)
                else:
                    self._terminate_child_processes_linux_and_mac(py_db.dont_terminate_child_pids)
        finally:
            pydev_log.debug("Exiting process (os._exit(0)).")
            os._exit(0)

    def _terminate_if_commands_processed(self, py_db):
        py_db.dispose_and_kill_all_pydevd_threads()
        self.terminate_process(py_db)

    def request_terminate_process(self, py_db):
        if py_db.terminate_keyboard_interrupt:
            if not py_db.keyboard_interrupt_requested:
                py_db.keyboard_interrupt_requested = True
                interrupt_main_thread()
                return

        # We mark with a terminate_requested to avoid that paused threads start running
        # (we should terminate as is without letting any paused thread run).
        py_db.terminate_requested = True
        run_as_pydevd_daemon_thread(py_db, self._terminate_if_commands_processed, py_db)

    def setup_auto_reload_watcher(self, py_db, enable_auto_reload, watch_dirs, poll_target_time, exclude_patterns, include_patterns):
        py_db.setup_auto_reload_watcher(enable_auto_reload, watch_dirs, poll_target_time, exclude_patterns, include_patterns)


def _list_ppid_and_pid():
    _TH32CS_SNAPPROCESS = 0x00000002

```
