# Chunk: a5eaacbf302d_5

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/version.py`
- lines: 449-548
- chunk: 6/13

```

    return _GetSystemMetrics(nIndex)


# SIZE_T WINAPI GetLargePageMinimum(void);
def GetLargePageMinimum():
    _GetLargePageMinimum = windll.user32.GetLargePageMinimum
    _GetLargePageMinimum.argtypes = []
    _GetLargePageMinimum.restype = SIZE_T
    return _GetLargePageMinimum()


# HANDLE WINAPI GetCurrentProcess(void);
def GetCurrentProcess():
    ##    return 0xFFFFFFFFFFFFFFFFL
    _GetCurrentProcess = windll.kernel32.GetCurrentProcess
    _GetCurrentProcess.argtypes = []
    _GetCurrentProcess.restype = HANDLE
    return _GetCurrentProcess()


# HANDLE WINAPI GetCurrentThread(void);
def GetCurrentThread():
    ##    return 0xFFFFFFFFFFFFFFFEL
    _GetCurrentThread = windll.kernel32.GetCurrentThread
    _GetCurrentThread.argtypes = []
    _GetCurrentThread.restype = HANDLE
    return _GetCurrentThread()


# BOOL WINAPI IsWow64Process(
#   __in   HANDLE hProcess,
#   __out  PBOOL Wow64Process
# );
def IsWow64Process(hProcess):
    _IsWow64Process = windll.kernel32.IsWow64Process
    _IsWow64Process.argtypes = [HANDLE, PBOOL]
    _IsWow64Process.restype = bool
    _IsWow64Process.errcheck = RaiseIfZero

    Wow64Process = BOOL(FALSE)
    _IsWow64Process(hProcess, byref(Wow64Process))
    return bool(Wow64Process)


# DWORD WINAPI GetVersion(void);
def GetVersion():
    _GetVersion = windll.kernel32.GetVersion
    _GetVersion.argtypes = []
    _GetVersion.restype = DWORD
    _GetVersion.errcheck = RaiseIfZero

    # See the example code here:
    # http://msdn.microsoft.com/en-us/library/ms724439(VS.85).aspx

    dwVersion = _GetVersion()
    dwMajorVersion = dwVersion & 0x000000FF
    dwMinorVersion = (dwVersion & 0x0000FF00) >> 8
    if (dwVersion & 0x80000000) == 0:
        dwBuild = (dwVersion & 0x7FFF0000) >> 16
    else:
        dwBuild = None
    return int(dwMajorVersion), int(dwMinorVersion), int(dwBuild)


# BOOL WINAPI GetVersionEx(
#   __inout  LPOSVERSIONINFO lpVersionInfo
# );
def GetVersionExA():
    _GetVersionExA = windll.kernel32.GetVersionExA
    _GetVersionExA.argtypes = [POINTER(OSVERSIONINFOEXA)]
    _GetVersionExA.restype = bool
    _GetVersionExA.errcheck = RaiseIfZero

    osi = OSVERSIONINFOEXA()
    osi.dwOSVersionInfoSize = sizeof(osi)
    try:
        _GetVersionExA(byref(osi))
    except WindowsError:
        osi = OSVERSIONINFOA()
        osi.dwOSVersionInfoSize = sizeof(osi)
        _GetVersionExA.argtypes = [POINTER(OSVERSIONINFOA)]
        _GetVersionExA(byref(osi))
    return osi


def GetVersionExW():
    _GetVersionExW = windll.kernel32.GetVersionExW
    _GetVersionExW.argtypes = [POINTER(OSVERSIONINFOEXW)]
    _GetVersionExW.restype = bool
    _GetVersionExW.errcheck = RaiseIfZero

    osi = OSVERSIONINFOEXW()
    osi.dwOSVersionInfoSize = sizeof(osi)
    try:
        _GetVersionExW(byref(osi))
    except WindowsError:
        osi = OSVERSIONINFOW()
        osi.dwOSVersionInfoSize = sizeof(osi)
```
