# Chunk: edcdb0c75a7d_17

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 1030-1107
- chunk: 18/20

```

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
        for ppid, pid in _list_ppid_and_pid():
            if pid == this_pid:
                return ppid

        return None

    def _terminate_child_processes_windows(self, dont_terminate_child_pids):
        this_pid = os.getpid()
        for _ in range(50):  # Try this at most 50 times before giving up.
            # Note: we can't kill the process itself with taskkill, so, we
            # list immediate children, kill that tree and then exit this process.

            children_pids = []
            for ppid, pid in _list_ppid_and_pid():
                if ppid == this_pid:
                    if pid not in dont_terminate_child_pids:
                        children_pids.append(pid)

            if not children_pids:
                break
            else:
                for pid in children_pids:
                    self._call(["taskkill", "/F", "/PID", str(pid), "/T"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                del children_pids[:]

    def _terminate_child_processes_linux_and_mac(self, dont_terminate_child_pids):
        this_pid = os.getpid()

        def list_children_and_stop_forking(initial_pid, stop=True):
            children_pids = []
            if stop:
                # Ask to stop forking (shouldn't be called for this process, only subprocesses).
                self._call(["kill", "-STOP", str(initial_pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            list_popen = self._popen(["pgrep", "-P", str(initial_pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if list_popen is not None:
                stdout, _ = list_popen.communicate()
                for line in stdout.splitlines():
                    line = line.decode("ascii").strip()
                    if line:
                        pid = str(line)
                        if pid in dont_terminate_child_pids:
                            continue
                        children_pids.append(pid)
                        # Recursively get children.
                        children_pids.extend(list_children_and_stop_forking(pid))
            return children_pids

        previously_found = set()

        for _ in range(50):  # Try this at most 50 times before giving up.
            children_pids = list_children_and_stop_forking(this_pid, stop=False)
            found_new = False

            for pid in children_pids:
                if pid not in previously_found:
                    found_new = True
                    previously_found.add(pid)
                    self._call(["kill", "-KILL", str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

```
