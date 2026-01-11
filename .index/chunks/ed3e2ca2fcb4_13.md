# Chunk: ed3e2ca2fcb4_13

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 1225-1321
- chunk: 14/20

```
Wnd)


# HWND WindowFromPoint(
#     POINT Point
# );
def WindowFromPoint(point):
    _WindowFromPoint = windll.user32.WindowFromPoint
    _WindowFromPoint.argtypes = [POINT]
    _WindowFromPoint.restype = HWND
    _WindowFromPoint.errcheck = RaiseIfZero
    if isinstance(point, tuple):
        point = POINT(*point)
    return _WindowFromPoint(point)


# HWND ChildWindowFromPoint(
#     HWND hWndParent,
#     POINT Point
# );
def ChildWindowFromPoint(hWndParent, point):
    _ChildWindowFromPoint = windll.user32.ChildWindowFromPoint
    _ChildWindowFromPoint.argtypes = [HWND, POINT]
    _ChildWindowFromPoint.restype = HWND
    _ChildWindowFromPoint.errcheck = RaiseIfZero
    if isinstance(point, tuple):
        point = POINT(*point)
    return _ChildWindowFromPoint(hWndParent, point)


# HWND RealChildWindowFromPoint(
#    HWND hwndParent,
#    POINT ptParentClientCoords
# );
def RealChildWindowFromPoint(hWndParent, ptParentClientCoords):
    _RealChildWindowFromPoint = windll.user32.RealChildWindowFromPoint
    _RealChildWindowFromPoint.argtypes = [HWND, POINT]
    _RealChildWindowFromPoint.restype = HWND
    _RealChildWindowFromPoint.errcheck = RaiseIfZero
    if isinstance(ptParentClientCoords, tuple):
        ptParentClientCoords = POINT(*ptParentClientCoords)
    return _RealChildWindowFromPoint(hWndParent, ptParentClientCoords)


# BOOL ScreenToClient(
#   __in  HWND hWnd,
#         LPPOINT lpPoint
# );
def ScreenToClient(hWnd, lpPoint):
    _ScreenToClient = windll.user32.ScreenToClient
    _ScreenToClient.argtypes = [HWND, LPPOINT]
    _ScreenToClient.restype = bool
    _ScreenToClient.errcheck = RaiseIfZero

    if isinstance(lpPoint, tuple):
        lpPoint = POINT(*lpPoint)
    else:
        lpPoint = POINT(lpPoint.x, lpPoint.y)
    _ScreenToClient(hWnd, byref(lpPoint))
    return Point(lpPoint.x, lpPoint.y)


# BOOL ClientToScreen(
#   HWND hWnd,
#   LPPOINT lpPoint
# );
def ClientToScreen(hWnd, lpPoint):
    _ClientToScreen = windll.user32.ClientToScreen
    _ClientToScreen.argtypes = [HWND, LPPOINT]
    _ClientToScreen.restype = bool
    _ClientToScreen.errcheck = RaiseIfZero

    if isinstance(lpPoint, tuple):
        lpPoint = POINT(*lpPoint)
    else:
        lpPoint = POINT(lpPoint.x, lpPoint.y)
    _ClientToScreen(hWnd, byref(lpPoint))
    return Point(lpPoint.x, lpPoint.y)


# int MapWindowPoints(
#   __in     HWND hWndFrom,
#   __in     HWND hWndTo,
#   __inout  LPPOINT lpPoints,
#   __in     UINT cPoints
# );
def MapWindowPoints(hWndFrom, hWndTo, lpPoints):
    _MapWindowPoints = windll.user32.MapWindowPoints
    _MapWindowPoints.argtypes = [HWND, HWND, LPPOINT, UINT]
    _MapWindowPoints.restype = ctypes.c_int

    cPoints = len(lpPoints)
    lpPoints = (POINT * cPoints)(*lpPoints)
    SetLastError(ERROR_SUCCESS)
    number = _MapWindowPoints(hWndFrom, hWndTo, byref(lpPoints), cPoints)
    if number == 0:
```
