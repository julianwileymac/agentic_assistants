# Chunk: ed3e2ca2fcb4_18

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 1667-1757
- chunk: 19/20

```
Param)


SendNotifyMessage = GuessStringType(SendNotifyMessageA, SendNotifyMessageW)


# LRESULT SendDlgItemMessage(
#     HWND hDlg,
#     int nIDDlgItem,
#     UINT Msg,
#     WPARAM wParam,
#     LPARAM lParam
# );
def SendDlgItemMessageA(hDlg, nIDDlgItem, Msg, wParam=0, lParam=0):
    _SendDlgItemMessageA = windll.user32.SendDlgItemMessageA
    _SendDlgItemMessageA.argtypes = [HWND, ctypes.c_int, UINT, WPARAM, LPARAM]
    _SendDlgItemMessageA.restype = LRESULT

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    return _SendDlgItemMessageA(hDlg, nIDDlgItem, Msg, wParam, lParam)


def SendDlgItemMessageW(hDlg, nIDDlgItem, Msg, wParam=0, lParam=0):
    _SendDlgItemMessageW = windll.user32.SendDlgItemMessageW
    _SendDlgItemMessageW.argtypes = [HWND, ctypes.c_int, UINT, WPARAM, LPARAM]
    _SendDlgItemMessageW.restype = LRESULT

    wParam = MAKE_WPARAM(wParam)
    lParam = MAKE_LPARAM(lParam)
    return _SendDlgItemMessageW(hDlg, nIDDlgItem, Msg, wParam, lParam)


SendDlgItemMessage = GuessStringType(SendDlgItemMessageA, SendDlgItemMessageW)


# DWORD WINAPI WaitForInputIdle(
#   _In_  HANDLE hProcess,
#   _In_  DWORD dwMilliseconds
# );
def WaitForInputIdle(hProcess, dwMilliseconds=INFINITE):
    _WaitForInputIdle = windll.user32.WaitForInputIdle
    _WaitForInputIdle.argtypes = [HANDLE, DWORD]
    _WaitForInputIdle.restype = DWORD

    r = _WaitForInputIdle(hProcess, dwMilliseconds)
    if r == WAIT_FAILED:
        raise ctypes.WinError()
    return r


# UINT RegisterWindowMessage(
#     LPCTSTR lpString
# );
def RegisterWindowMessageA(lpString):
    _RegisterWindowMessageA = windll.user32.RegisterWindowMessageA
    _RegisterWindowMessageA.argtypes = [LPSTR]
    _RegisterWindowMessageA.restype = UINT
    _RegisterWindowMessageA.errcheck = RaiseIfZero
    return _RegisterWindowMessageA(lpString)


def RegisterWindowMessageW(lpString):
    _RegisterWindowMessageW = windll.user32.RegisterWindowMessageW
    _RegisterWindowMessageW.argtypes = [LPWSTR]
    _RegisterWindowMessageW.restype = UINT
    _RegisterWindowMessageW.errcheck = RaiseIfZero
    return _RegisterWindowMessageW(lpString)


RegisterWindowMessage = GuessStringType(RegisterWindowMessageA, RegisterWindowMessageW)


# UINT RegisterClipboardFormat(
#     LPCTSTR lpString
# );
def RegisterClipboardFormatA(lpString):
    _RegisterClipboardFormatA = windll.user32.RegisterClipboardFormatA
    _RegisterClipboardFormatA.argtypes = [LPSTR]
    _RegisterClipboardFormatA.restype = UINT
    _RegisterClipboardFormatA.errcheck = RaiseIfZero
    return _RegisterClipboardFormatA(lpString)


def RegisterClipboardFormatW(lpString):
    _RegisterClipboardFormatW = windll.user32.RegisterClipboardFormatW
    _RegisterClipboardFormatW.argtypes = [LPWSTR]
    _RegisterClipboardFormatW.restype = UINT
    _RegisterClipboardFormatW.errcheck = RaiseIfZero
    return _RegisterClipboardFormatW(lpString)
```
