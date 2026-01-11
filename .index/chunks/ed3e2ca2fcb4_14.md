# Chunk: ed3e2ca2fcb4_14

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 1313-1411
- chunk: 15/20

```
dowPoints.argtypes = [HWND, HWND, LPPOINT, UINT]
    _MapWindowPoints.restype = ctypes.c_int

    cPoints = len(lpPoints)
    lpPoints = (POINT * cPoints)(*lpPoints)
    SetLastError(ERROR_SUCCESS)
    number = _MapWindowPoints(hWndFrom, hWndTo, byref(lpPoints), cPoints)
    if number == 0:
        errcode = GetLastError()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    x_delta = number & 0xFFFF
    y_delta = (number >> 16) & 0xFFFF
    return x_delta, y_delta, [(Point.x, Point.y) for Point in lpPoints]


# BOOL SetForegroundWindow(
#    HWND hWnd
# );
def SetForegroundWindow(hWnd):
    _SetForegroundWindow = windll.user32.SetForegroundWindow
    _SetForegroundWindow.argtypes = [HWND]
    _SetForegroundWindow.restype = bool
    _SetForegroundWindow.errcheck = RaiseIfZero
    return _SetForegroundWindow(hWnd)


# BOOL GetWindowPlacement(
#     HWND hWnd,
#     WINDOWPLACEMENT *lpwndpl
# );
def GetWindowPlacement(hWnd):
    _GetWindowPlacement = windll.user32.GetWindowPlacement
    _GetWindowPlacement.argtypes = [HWND, PWINDOWPLACEMENT]
    _GetWindowPlacement.restype = bool
    _GetWindowPlacement.errcheck = RaiseIfZero

    lpwndpl = WINDOWPLACEMENT()
    lpwndpl.length = sizeof(lpwndpl)
    _GetWindowPlacement(hWnd, byref(lpwndpl))
    return WindowPlacement(lpwndpl)


# BOOL SetWindowPlacement(
#     HWND hWnd,
#     WINDOWPLACEMENT *lpwndpl
# );
def SetWindowPlacement(hWnd, lpwndpl):
    _SetWindowPlacement = windll.user32.SetWindowPlacement
    _SetWindowPlacement.argtypes = [HWND, PWINDOWPLACEMENT]
    _SetWindowPlacement.restype = bool
    _SetWindowPlacement.errcheck = RaiseIfZero

    if isinstance(lpwndpl, WINDOWPLACEMENT):
        lpwndpl.length = sizeof(lpwndpl)
    _SetWindowPlacement(hWnd, byref(lpwndpl))


# BOOL WINAPI GetWindowRect(
#   __in   HWND hWnd,
#   __out  LPRECT lpRect
# );
def GetWindowRect(hWnd):
    _GetWindowRect = windll.user32.GetWindowRect
    _GetWindowRect.argtypes = [HWND, LPRECT]
    _GetWindowRect.restype = bool
    _GetWindowRect.errcheck = RaiseIfZero

    lpRect = RECT()
    _GetWindowRect(hWnd, byref(lpRect))
    return Rect(lpRect.left, lpRect.top, lpRect.right, lpRect.bottom)


# BOOL WINAPI GetClientRect(
#   __in   HWND hWnd,
#   __out  LPRECT lpRect
# );
def GetClientRect(hWnd):
    _GetClientRect = windll.user32.GetClientRect
    _GetClientRect.argtypes = [HWND, LPRECT]
    _GetClientRect.restype = bool
    _GetClientRect.errcheck = RaiseIfZero

    lpRect = RECT()
    _GetClientRect(hWnd, byref(lpRect))
    return Rect(lpRect.left, lpRect.top, lpRect.right, lpRect.bottom)


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
```
