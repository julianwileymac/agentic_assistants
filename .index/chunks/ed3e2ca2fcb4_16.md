# Chunk: ed3e2ca2fcb4_16

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 1499-1597
- chunk: 17/20

```
indows
    _EnumChildWindows.argtypes = [HWND, WNDENUMPROC, LPARAM]
    _EnumChildWindows.restype = bool

    EnumFunc = __EnumChildProc()
    lpEnumFunc = WNDENUMPROC(EnumFunc)
    SetLastError(ERROR_SUCCESS)
    _EnumChildWindows(hWndParent, lpEnumFunc, NULL)
    errcode = GetLastError()
    if errcode != ERROR_SUCCESS and errcode not in (ERROR_NO_MORE_FILES, ERROR_SUCCESS):
        raise ctypes.WinError(errcode)
    return EnumFunc.hwnd


# LRESULT SendMessage(
#     HWND hWnd,
#     UINT Msg,
#     WPARAM wParam,
#     LPARAM lParam
# );
def SendMessageA(hWnd, Msg, wParam=0, lParam=0):
    _SendMessageA = windll.user32.SendMessageA
    _SendMessageA.argtypes = [HWND, UINT, WPARAM, LPARAM]
    _SendMessageA.restype = LRESULT

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    return _SendMessageA(hWnd, Msg, wParam, lParam)


def SendMessageW(hWnd, Msg, wParam=0, lParam=0):
    _SendMessageW = windll.user32.SendMessageW
    _SendMessageW.argtypes = [HWND, UINT, WPARAM, LPARAM]
    _SendMessageW.restype = LRESULT

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    return _SendMessageW(hWnd, Msg, wParam, lParam)


SendMessage = GuessStringType(SendMessageA, SendMessageW)


# BOOL PostMessage(
#     HWND hWnd,
#     UINT Msg,
#     WPARAM wParam,
#     LPARAM lParam
# );
def PostMessageA(hWnd, Msg, wParam=0, lParam=0):
    _PostMessageA = windll.user32.PostMessageA
    _PostMessageA.argtypes = [HWND, UINT, WPARAM, LPARAM]
    _PostMessageA.restype = bool
    _PostMessageA.errcheck = RaiseIfZero

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    _PostMessageA(hWnd, Msg, wParam, lParam)


def PostMessageW(hWnd, Msg, wParam=0, lParam=0):
    _PostMessageW = windll.user32.PostMessageW
    _PostMessageW.argtypes = [HWND, UINT, WPARAM, LPARAM]
    _PostMessageW.restype = bool
    _PostMessageW.errcheck = RaiseIfZero

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    _PostMessageW(hWnd, Msg, wParam, lParam)


PostMessage = GuessStringType(PostMessageA, PostMessageW)


# BOOL PostThreadMessage(
#     DWORD idThread,
#     UINT Msg,
#     WPARAM wParam,
#     LPARAM lParam
# );
def PostThreadMessageA(idThread, Msg, wParam=0, lParam=0):
    _PostThreadMessageA = windll.user32.PostThreadMessageA
    _PostThreadMessageA.argtypes = [DWORD, UINT, WPARAM, LPARAM]
    _PostThreadMessageA.restype = bool
    _PostThreadMessageA.errcheck = RaiseIfZero

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    _PostThreadMessageA(idThread, Msg, wParam, lParam)


def PostThreadMessageW(idThread, Msg, wParam=0, lParam=0):
    _PostThreadMessageW = windll.user32.PostThreadMessageW
    _PostThreadMessageW.argtypes = [DWORD, UINT, WPARAM, LPARAM]
    _PostThreadMessageW.restype = bool
    _PostThreadMessageW.errcheck = RaiseIfZero

    wParam = MAKE_WPARAM(wParam)
```
