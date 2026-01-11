# Chunk: ed3e2ca2fcb4_9

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 845-947
- chunk: 10/20

```
pes = [HWND, LPWSTR, ctypes.c_int]
    _GetWindowTextW.restype = ctypes.c_int

    nMaxCount = 0x1000
    dwCharSize = sizeof(CHAR)
    while 1:
        lpString = ctypes.create_string_buffer("", nMaxCount)
        nCount = _GetWindowTextW(hWnd, lpString, nMaxCount)
        if nCount == 0:
            raise ctypes.WinError()
        if nCount < nMaxCount - dwCharSize:
            break
        nMaxCount += 0x1000
    return lpString.value


GetWindowText = GuessStringType(GetWindowTextA, GetWindowTextW)


# BOOL WINAPI SetWindowText(
#   __in      HWND hWnd,
#   __in_opt  LPCTSTR lpString
# );
def SetWindowTextA(hWnd, lpString=None):
    _SetWindowTextA = windll.user32.SetWindowTextA
    _SetWindowTextA.argtypes = [HWND, LPSTR]
    _SetWindowTextA.restype = bool
    _SetWindowTextA.errcheck = RaiseIfZero
    _SetWindowTextA(hWnd, lpString)


def SetWindowTextW(hWnd, lpString=None):
    _SetWindowTextW = windll.user32.SetWindowTextW
    _SetWindowTextW.argtypes = [HWND, LPWSTR]
    _SetWindowTextW.restype = bool
    _SetWindowTextW.errcheck = RaiseIfZero
    _SetWindowTextW(hWnd, lpString)


SetWindowText = GuessStringType(SetWindowTextA, SetWindowTextW)


# LONG GetWindowLong(
#     HWND hWnd,
#     int nIndex
# );
def GetWindowLongA(hWnd, nIndex=0):
    _GetWindowLongA = windll.user32.GetWindowLongA
    _GetWindowLongA.argtypes = [HWND, ctypes.c_int]
    _GetWindowLongA.restype = DWORD

    SetLastError(ERROR_SUCCESS)
    retval = _GetWindowLongA(hWnd, nIndex)
    if retval == 0:
        errcode = GetLastError()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return retval


def GetWindowLongW(hWnd, nIndex=0):
    _GetWindowLongW = windll.user32.GetWindowLongW
    _GetWindowLongW.argtypes = [HWND, ctypes.c_int]
    _GetWindowLongW.restype = DWORD

    SetLastError(ERROR_SUCCESS)
    retval = _GetWindowLongW(hWnd, nIndex)
    if retval == 0:
        errcode = GetLastError()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return retval


GetWindowLong = DefaultStringType(GetWindowLongA, GetWindowLongW)

# LONG_PTR WINAPI GetWindowLongPtr(
#   _In_  HWND hWnd,
#   _In_  int nIndex
# );

if bits == 32:
    GetWindowLongPtrA = GetWindowLongA
    GetWindowLongPtrW = GetWindowLongW
    GetWindowLongPtr = GetWindowLong

else:

    def GetWindowLongPtrA(hWnd, nIndex=0):
        _GetWindowLongPtrA = windll.user32.GetWindowLongPtrA
        _GetWindowLongPtrA.argtypes = [HWND, ctypes.c_int]
        _GetWindowLongPtrA.restype = SIZE_T

        SetLastError(ERROR_SUCCESS)
        retval = _GetWindowLongPtrA(hWnd, nIndex)
        if retval == 0:
            errcode = GetLastError()
            if errcode != ERROR_SUCCESS:
                raise ctypes.WinError(errcode)
        return retval

    def GetWindowLongPtrW(hWnd, nIndex=0):
```
