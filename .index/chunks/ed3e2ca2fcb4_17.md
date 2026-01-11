# Chunk: ed3e2ca2fcb4_17

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 1590-1681
- chunk: 18/20

```
readMessageW(idThread, Msg, wParam=0, lParam=0):
    _PostThreadMessageW = windll.user32.PostThreadMessageW
    _PostThreadMessageW.argtypes = [DWORD, UINT, WPARAM, LPARAM]
    _PostThreadMessageW.restype = bool
    _PostThreadMessageW.errcheck = RaiseIfZero

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    _PostThreadMessageW(idThread, Msg, wParam, lParam)


PostThreadMessage = GuessStringType(PostThreadMessageA, PostThreadMessageW)


# LRESULT c(
#     HWND hWnd,
#     UINT Msg,
#     WPARAM wParam,
#     LPARAM lParam,
#     UINT fuFlags,
#     UINT uTimeout,
#     PDWORD_PTR lpdwResult
# );
def SendMessageTimeoutA(hWnd, Msg, wParam=0, lParam=0, fuFlags=0, uTimeout=0):
    _SendMessageTimeoutA = windll.user32.SendMessageTimeoutA
    _SendMessageTimeoutA.argtypes = [HWND, UINT, WPARAM, LPARAM, UINT, UINT, PDWORD_PTR]
    _SendMessageTimeoutA.restype = LRESULT
    _SendMessageTimeoutA.errcheck = RaiseIfZero

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    dwResult = DWORD(0)
    _SendMessageTimeoutA(hWnd, Msg, wParam, lParam, fuFlags, uTimeout, byref(dwResult))
    return dwResult.value


def SendMessageTimeoutW(hWnd, Msg, wParam=0, lParam=0):
    _SendMessageTimeoutW = windll.user32.SendMessageTimeoutW
    _SendMessageTimeoutW.argtypes = [HWND, UINT, WPARAM, LPARAM, UINT, UINT, PDWORD_PTR]
    _SendMessageTimeoutW.restype = LRESULT
    _SendMessageTimeoutW.errcheck = RaiseIfZero

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    dwResult = DWORD(0)
    _SendMessageTimeoutW(hWnd, Msg, wParam, lParam, fuFlags, uTimeout, byref(dwResult))
    return dwResult.value


SendMessageTimeout = GuessStringType(SendMessageTimeoutA, SendMessageTimeoutW)


# BOOL SendNotifyMessage(
#     HWND hWnd,
#     UINT Msg,
#     WPARAM wParam,
#     LPARAM lParam
# );
def SendNotifyMessageA(hWnd, Msg, wParam=0, lParam=0):
    _SendNotifyMessageA = windll.user32.SendNotifyMessageA
    _SendNotifyMessageA.argtypes = [HWND, UINT, WPARAM, LPARAM]
    _SendNotifyMessageA.restype = bool
    _SendNotifyMessageA.errcheck = RaiseIfZero

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    _SendNotifyMessageA(hWnd, Msg, wParam, lParam)


def SendNotifyMessageW(hWnd, Msg, wParam=0, lParam=0):
    _SendNotifyMessageW = windll.user32.SendNotifyMessageW
    _SendNotifyMessageW.argtypes = [HWND, UINT, WPARAM, LPARAM]
    _SendNotifyMessageW.restype = bool
    _SendNotifyMessageW.errcheck = RaiseIfZero

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    _SendNotifyMessageW(hWnd, Msg, wParam, lParam)


SendNotifyMessage = GuessStringType(SendNotifyMessageA, SendNotifyMessageW)


# LRESULT SendDlgItemMessage(
#     HWND hDlg,
#     int nIDDlgItem,
#     UINT Msg,
#     WPARAM wParam,
#     LPARAM lParam
# );
def SendDlgItemMessageA(hDlg, nIDDlgItem, Msg, wParam=0, lParam=0):
```
