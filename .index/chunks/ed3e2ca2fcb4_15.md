# Chunk: ed3e2ca2fcb4_15

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 1398-1508
- chunk: 16/20

```
turn Rect(lpRect.left, lpRect.top, lpRect.right, lpRect.bottom)


# BOOL MoveWindow(
#    HWND hWnd,
#    int X,
#    int Y,
#    int nWidth,
#    int nHeight,
#    BOOL bRepaint
# );
def MoveWindow(hWnd, X, Y, nWidth, nHeight, bRepaint=True):
    _MoveWindow = windll.user32.MoveWindow
    _MoveWindow.argtypes = [HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, BOOL]
    _MoveWindow.restype = bool
    _MoveWindow.errcheck = RaiseIfZero
    _MoveWindow(hWnd, X, Y, nWidth, nHeight, bool(bRepaint))


# BOOL GetGUIThreadInfo(
#     DWORD idThread,
#     LPGUITHREADINFO lpgui
# );
def GetGUIThreadInfo(idThread):
    _GetGUIThreadInfo = windll.user32.GetGUIThreadInfo
    _GetGUIThreadInfo.argtypes = [DWORD, LPGUITHREADINFO]
    _GetGUIThreadInfo.restype = bool
    _GetGUIThreadInfo.errcheck = RaiseIfZero

    gui = GUITHREADINFO()
    _GetGUIThreadInfo(idThread, byref(gui))
    return gui


# BOOL CALLBACK EnumWndProc(
#     HWND hwnd,
#     LPARAM lParam
# );
class __EnumWndProc(__WindowEnumerator):
    pass


# BOOL EnumWindows(
#     WNDENUMPROC lpEnumFunc,
#     LPARAM lParam
# );
def EnumWindows():
    _EnumWindows = windll.user32.EnumWindows
    _EnumWindows.argtypes = [WNDENUMPROC, LPARAM]
    _EnumWindows.restype = bool

    EnumFunc = __EnumWndProc()
    lpEnumFunc = WNDENUMPROC(EnumFunc)
    if not _EnumWindows(lpEnumFunc, NULL):
        errcode = GetLastError()
        if errcode not in (ERROR_NO_MORE_FILES, ERROR_SUCCESS):
            raise ctypes.WinError(errcode)
    return EnumFunc.hwnd


# BOOL CALLBACK EnumThreadWndProc(
#     HWND hwnd,
#     LPARAM lParam
# );
class __EnumThreadWndProc(__WindowEnumerator):
    pass


# BOOL EnumThreadWindows(
#     DWORD dwThreadId,
#     WNDENUMPROC lpfn,
#     LPARAM lParam
# );
def EnumThreadWindows(dwThreadId):
    _EnumThreadWindows = windll.user32.EnumThreadWindows
    _EnumThreadWindows.argtypes = [DWORD, WNDENUMPROC, LPARAM]
    _EnumThreadWindows.restype = bool

    fn = __EnumThreadWndProc()
    lpfn = WNDENUMPROC(fn)
    if not _EnumThreadWindows(dwThreadId, lpfn, NULL):
        errcode = GetLastError()
        if errcode not in (ERROR_NO_MORE_FILES, ERROR_SUCCESS):
            raise ctypes.WinError(errcode)
    return fn.hwnd


# BOOL CALLBACK EnumChildProc(
#     HWND hwnd,
#     LPARAM lParam
# );
class __EnumChildProc(__WindowEnumerator):
    pass


# BOOL EnumChildWindows(
#     HWND hWndParent,
#     WNDENUMPROC lpEnumFunc,
#     LPARAM lParam
# );
def EnumChildWindows(hWndParent=NULL):
    _EnumChildWindows = windll.user32.EnumChildWindows
    _EnumChildWindows.argtypes = [HWND, WNDENUMPROC, LPARAM]
    _EnumChildWindows.restype = bool

    EnumFunc = __EnumChildProc()
    lpEnumFunc = WNDENUMPROC(EnumFunc)
    SetLastError(ERROR_SUCCESS)
    _EnumChildWindows(hWndParent, lpEnumFunc, NULL)
    errcode = GetLastError()
```
