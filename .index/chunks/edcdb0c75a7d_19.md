# Chunk: edcdb0c75a7d_19

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_api.py`
- lines: 1163-1201
- chunk: 20/20

```
(self, py_db, enable_auto_reload, watch_dirs, poll_target_time, exclude_patterns, include_patterns):
        py_db.setup_auto_reload_watcher(enable_auto_reload, watch_dirs, poll_target_time, exclude_patterns, include_patterns)


def _list_ppid_and_pid():
    _TH32CS_SNAPPROCESS = 0x00000002

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", ctypes.c_uint32),
            ("cntUsage", ctypes.c_uint32),
            ("th32ProcessID", ctypes.c_uint32),
            ("th32DefaultHeapID", ctypes.c_size_t),
            ("th32ModuleID", ctypes.c_uint32),
            ("cntThreads", ctypes.c_uint32),
            ("th32ParentProcessID", ctypes.c_uint32),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", ctypes.c_uint32),
            ("szExeFile", ctypes.c_char * 260),
        ]

    kernel32 = ctypes.windll.kernel32
    snapshot = kernel32.CreateToolhelp32Snapshot(_TH32CS_SNAPPROCESS, 0)
    ppid_and_pids = []
    try:
        process_entry = PROCESSENTRY32()
        process_entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
        if not kernel32.Process32First(ctypes.c_void_p(snapshot), ctypes.byref(process_entry)):
            pydev_log.critical("Process32First failed (getting process from CreateToolhelp32Snapshot).")
        else:
            while True:
                ppid_and_pids.append((process_entry.th32ParentProcessID, process_entry.th32ProcessID))
                if not kernel32.Process32Next(ctypes.c_void_p(snapshot), ctypes.byref(process_entry)):
                    break
    finally:
        kernel32.CloseHandle(snapshot)

    return ppid_and_pids
```
