# Chunk: ed3e2ca2fcb4_7

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 673-765
- chunk: 8/20

```
operty
    def _as_parameter_(self):
        """
        Compatibility with ctypes.
        Allows passing transparently a Point object to an API call.
        """
        wp = WINDOWPLACEMENT()
        wp.length = sizeof(wp)
        wp.flags = self.flags
        wp.showCmd = self.showCmd
        wp.ptMinPosition.x = self.ptMinPosition.x
        wp.ptMinPosition.y = self.ptMinPosition.y
        wp.ptMaxPosition.x = self.ptMaxPosition.x
        wp.ptMaxPosition.y = self.ptMaxPosition.y
        wp.rcNormalPosition.left = self.rcNormalPosition.left
        wp.rcNormalPosition.top = self.rcNormalPosition.top
        wp.rcNormalPosition.right = self.rcNormalPosition.right
        wp.rcNormalPosition.bottom = self.rcNormalPosition.bottom
        return wp


# --- user32.dll ---------------------------------------------------------------


# void WINAPI SetLastErrorEx(
#   __in  DWORD dwErrCode,
#   __in  DWORD dwType
# );
def SetLastErrorEx(dwErrCode, dwType=0):
    _SetLastErrorEx = windll.user32.SetLastErrorEx
    _SetLastErrorEx.argtypes = [DWORD, DWORD]
    _SetLastErrorEx.restype = None
    _SetLastErrorEx(dwErrCode, dwType)


# HWND FindWindow(
#     LPCTSTR lpClassName,
#     LPCTSTR lpWindowName
# );
def FindWindowA(lpClassName=None, lpWindowName=None):
    _FindWindowA = windll.user32.FindWindowA
    _FindWindowA.argtypes = [LPSTR, LPSTR]
    _FindWindowA.restype = HWND

    hWnd = _FindWindowA(lpClassName, lpWindowName)
    if not hWnd:
        errcode = GetLastError()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return hWnd


def FindWindowW(lpClassName=None, lpWindowName=None):
    _FindWindowW = windll.user32.FindWindowW
    _FindWindowW.argtypes = [LPWSTR, LPWSTR]
    _FindWindowW.restype = HWND

    hWnd = _FindWindowW(lpClassName, lpWindowName)
    if not hWnd:
        errcode = GetLastError()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return hWnd


FindWindow = GuessStringType(FindWindowA, FindWindowW)


# HWND WINAPI FindWindowEx(
#   __in_opt  HWND hwndParent,
#   __in_opt  HWND hwndChildAfter,
#   __in_opt  LPCTSTR lpszClass,
#   __in_opt  LPCTSTR lpszWindow
# );
def FindWindowExA(hwndParent=None, hwndChildAfter=None, lpClassName=None, lpWindowName=None):
    _FindWindowExA = windll.user32.FindWindowExA
    _FindWindowExA.argtypes = [HWND, HWND, LPSTR, LPSTR]
    _FindWindowExA.restype = HWND

    hWnd = _FindWindowExA(hwndParent, hwndChildAfter, lpClassName, lpWindowName)
    if not hWnd:
        errcode = GetLastError()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return hWnd


def FindWindowExW(hwndParent=None, hwndChildAfter=None, lpClassName=None, lpWindowName=None):
    _FindWindowExW = windll.user32.FindWindowExW
    _FindWindowExW.argtypes = [HWND, HWND, LPWSTR, LPWSTR]
    _FindWindowExW.restype = HWND

```
