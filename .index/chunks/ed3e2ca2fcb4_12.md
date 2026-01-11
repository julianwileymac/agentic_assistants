# Chunk: ed3e2ca2fcb4_12

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 1117-1237
- chunk: 13/20

```
(
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
#     int nCmdShow
# );
def ShowWindow(hWnd, nCmdShow=SW_SHOW):
    _ShowWindow = windll.user32.ShowWindow
    _ShowWindow.argtypes = [HWND, ctypes.c_int]
    _ShowWindow.restype = bool
    return _ShowWindow(hWnd, nCmdShow)


# BOOL ShowWindowAsync(
#     HWND hWnd,
#     int nCmdShow
# );
def ShowWindowAsync(hWnd, nCmdShow=SW_SHOW):
    _ShowWindowAsync = windll.user32.ShowWindowAsync
    _ShowWindowAsync.argtypes = [HWND, ctypes.c_int]
    _ShowWindowAsync.restype = bool
    return _ShowWindowAsync(hWnd, nCmdShow)


# HWND GetDesktopWindow(VOID);
def GetDesktopWindow():
    _GetDesktopWindow = windll.user32.GetDesktopWindow
    _GetDesktopWindow.argtypes = []
    _GetDesktopWindow.restype = HWND
    _GetDesktopWindow.errcheck = RaiseIfZero
    return _GetDesktopWindow()


# HWND GetForegroundWindow(VOID);
def GetForegroundWindow():
    _GetForegroundWindow = windll.user32.GetForegroundWindow
    _GetForegroundWindow.argtypes = []
    _GetForegroundWindow.restype = HWND
    _GetForegroundWindow.errcheck = RaiseIfZero
    return _GetForegroundWindow()


# BOOL IsWindow(
#     HWND hWnd
# );
def IsWindow(hWnd):
    _IsWindow = windll.user32.IsWindow
    _IsWindow.argtypes = [HWND]
    _IsWindow.restype = bool
    return _IsWindow(hWnd)


# BOOL IsWindowVisible(
#     HWND hWnd
# );
def IsWindowVisible(hWnd):
    _IsWindowVisible = windll.user32.IsWindowVisible
    _IsWindowVisible.argtypes = [HWND]
    _IsWindowVisible.restype = bool
    return _IsWindowVisible(hWnd)


# BOOL IsWindowEnabled(
#     HWND hWnd
# );
def IsWindowEnabled(hWnd):
    _IsWindowEnabled = windll.user32.IsWindowEnabled
    _IsWindowEnabled.argtypes = [HWND]
    _IsWindowEnabled.restype = bool
    return _IsWindowEnabled(hWnd)


# BOOL IsZoomed(
#     HWND hWnd
# );
def IsZoomed(hWnd):
    _IsZoomed = windll.user32.IsZoomed
    _IsZoomed.argtypes = [HWND]
    _IsZoomed.restype = bool
    return _IsZoomed(hWnd)


# BOOL IsIconic(
#     HWND hWnd
# );
def IsIconic(hWnd):
    _IsIconic = windll.user32.IsIconic
    _IsIconic.argtypes = [HWND]
    _IsIconic.restype = bool
    return _IsIconic(hWnd)


# BOOL IsChild(
#     HWND hWnd
# );
def IsChild(hWnd):
    _IsChild = windll.user32.IsChild
    _IsChild.argtypes = [HWND]
    _IsChild.restype = bool
    return _IsChild(hWnd)


# HWND WindowFromPoint(
#     POINT Point
# );
def WindowFromPoint(point):
    _WindowFromPoint = windll.user32.WindowFromPoint
    _WindowFromPoint.argtypes = [POINT]
    _WindowFromPoint.restype = HWND
    _WindowFromPoint.errcheck = RaiseIfZero
    if isinstance(point, tuple):
```
