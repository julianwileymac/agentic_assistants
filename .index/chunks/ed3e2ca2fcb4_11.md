# Chunk: ed3e2ca2fcb4_11

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 1024-1130
- chunk: 12/20

```
d, nIndex, dwNewLong):
        _SetWindowLongPtrW = windll.user32.SetWindowLongPtrW
        _SetWindowLongPtrW.argtypes = [HWND, ctypes.c_int, SIZE_T]
        _SetWindowLongPtrW.restype = SIZE_T

        SetLastError(ERROR_SUCCESS)
        retval = _SetWindowLongPtrW(hWnd, nIndex, dwNewLong)
        if retval == 0:
            errcode = GetLastError()
            if errcode != ERROR_SUCCESS:
                raise ctypes.WinError(errcode)
        return retval

    SetWindowLongPtr = DefaultStringType(SetWindowLongPtrA, SetWindowLongPtrW)


# HWND GetShellWindow(VOID);
def GetShellWindow():
    _GetShellWindow = windll.user32.GetShellWindow
    _GetShellWindow.argtypes = []
    _GetShellWindow.restype = HWND
    _GetShellWindow.errcheck = RaiseIfZero
    return _GetShellWindow()


# DWORD GetWindowThreadProcessId(
#     HWND hWnd,
#     LPDWORD lpdwProcessId
# );
def GetWindowThreadProcessId(hWnd):
    _GetWindowThreadProcessId = windll.user32.GetWindowThreadProcessId
    _GetWindowThreadProcessId.argtypes = [HWND, LPDWORD]
    _GetWindowThreadProcessId.restype = DWORD
    _GetWindowThreadProcessId.errcheck = RaiseIfZero

    dwProcessId = DWORD(0)
    dwThreadId = _GetWindowThreadProcessId(hWnd, byref(dwProcessId))
    return (dwThreadId, dwProcessId.value)


# HWND WINAPI GetWindow(
#   __in  HWND hwnd,
#   __in  UINT uCmd
# );
def GetWindow(hWnd, uCmd):
    _GetWindow = windll.user32.GetWindow
    _GetWindow.argtypes = [HWND, UINT]
    _GetWindow.restype = HWND

    SetLastError(ERROR_SUCCESS)
    hWndTarget = _GetWindow(hWnd, uCmd)
    if not hWndTarget:
        winerr = GetLastError()
        if winerr != ERROR_SUCCESS:
            raise ctypes.WinError(winerr)
    return hWndTarget


# HWND GetParent(
#       HWND hWnd
# );
def GetParent(hWnd):
    _GetParent = windll.user32.GetParent
    _GetParent.argtypes = [HWND]
    _GetParent.restype = HWND

    SetLastError(ERROR_SUCCESS)
    hWndParent = _GetParent(hWnd)
    if not hWndParent:
        winerr = GetLastError()
        if winerr != ERROR_SUCCESS:
            raise ctypes.WinError(winerr)
    return hWndParent


# HWND WINAPI GetAncestor(
#   __in  HWND hwnd,
#   __in  UINT gaFlags
# );
def GetAncestor(hWnd, gaFlags=GA_PARENT):
    _GetAncestor = windll.user32.GetAncestor
    _GetAncestor.argtypes = [HWND, UINT]
    _GetAncestor.restype = HWND

    SetLastError(ERROR_SUCCESS)
    hWndParent = _GetAncestor(hWnd, gaFlags)
    if not hWndParent:
        winerr = GetLastError()
        if winerr != ERROR_SUCCESS:
            raise ctypes.WinError(winerr)
    return hWndParent


# BOOL EnableWindow(
#     HWND hWnd,
#     BOOL bEnable
# );
def EnableWindow(hWnd, bEnable=True):
    _EnableWindow = windll.user32.EnableWindow
    _EnableWindow.argtypes = [HWND, BOOL]
    _EnableWindow.restype = bool
    return _EnableWindow(hWnd, bool(bEnable))


# BOOL ShowWindow(
#     HWND hWnd,
```
