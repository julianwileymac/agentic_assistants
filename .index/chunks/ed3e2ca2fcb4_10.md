# Chunk: ed3e2ca2fcb4_10

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 938-1031
- chunk: 11/20

```
tLastError(ERROR_SUCCESS)
        retval = _GetWindowLongPtrA(hWnd, nIndex)
        if retval == 0:
            errcode = GetLastError()
            if errcode != ERROR_SUCCESS:
                raise ctypes.WinError(errcode)
        return retval

    def GetWindowLongPtrW(hWnd, nIndex=0):
        _GetWindowLongPtrW = windll.user32.GetWindowLongPtrW
        _GetWindowLongPtrW.argtypes = [HWND, ctypes.c_int]
        _GetWindowLongPtrW.restype = DWORD

        SetLastError(ERROR_SUCCESS)
        retval = _GetWindowLongPtrW(hWnd, nIndex)
        if retval == 0:
            errcode = GetLastError()
            if errcode != ERROR_SUCCESS:
                raise ctypes.WinError(errcode)
        return retval

    GetWindowLongPtr = DefaultStringType(GetWindowLongPtrA, GetWindowLongPtrW)

# LONG WINAPI SetWindowLong(
#   _In_  HWND hWnd,
#   _In_  int nIndex,
#   _In_  LONG dwNewLong
# );


def SetWindowLongA(hWnd, nIndex, dwNewLong):
    _SetWindowLongA = windll.user32.SetWindowLongA
    _SetWindowLongA.argtypes = [HWND, ctypes.c_int, DWORD]
    _SetWindowLongA.restype = DWORD

    SetLastError(ERROR_SUCCESS)
    retval = _SetWindowLongA(hWnd, nIndex, dwNewLong)
    if retval == 0:
        errcode = GetLastError()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return retval


def SetWindowLongW(hWnd, nIndex, dwNewLong):
    _SetWindowLongW = windll.user32.SetWindowLongW
    _SetWindowLongW.argtypes = [HWND, ctypes.c_int, DWORD]
    _SetWindowLongW.restype = DWORD

    SetLastError(ERROR_SUCCESS)
    retval = _SetWindowLongW(hWnd, nIndex, dwNewLong)
    if retval == 0:
        errcode = GetLastError()
        if errcode != ERROR_SUCCESS:
            raise ctypes.WinError(errcode)
    return retval


SetWindowLong = DefaultStringType(SetWindowLongA, SetWindowLongW)

# LONG_PTR WINAPI SetWindowLongPtr(
#   _In_  HWND hWnd,
#   _In_  int nIndex,
#   _In_  LONG_PTR dwNewLong
# );

if bits == 32:
    SetWindowLongPtrA = SetWindowLongA
    SetWindowLongPtrW = SetWindowLongW
    SetWindowLongPtr = SetWindowLong

else:

    def SetWindowLongPtrA(hWnd, nIndex, dwNewLong):
        _SetWindowLongPtrA = windll.user32.SetWindowLongPtrA
        _SetWindowLongPtrA.argtypes = [HWND, ctypes.c_int, SIZE_T]
        _SetWindowLongPtrA.restype = SIZE_T

        SetLastError(ERROR_SUCCESS)
        retval = _SetWindowLongPtrA(hWnd, nIndex, dwNewLong)
        if retval == 0:
            errcode = GetLastError()
            if errcode != ERROR_SUCCESS:
                raise ctypes.WinError(errcode)
        return retval

    def SetWindowLongPtrW(hWnd, nIndex, dwNewLong):
        _SetWindowLongPtrW = windll.user32.SetWindowLongPtrW
        _SetWindowLongPtrW.argtypes = [HWND, ctypes.c_int, SIZE_T]
        _SetWindowLongPtrW.restype = SIZE_T

        SetLastError(ERROR_SUCCESS)
        retval = _SetWindowLongPtrW(hWnd, nIndex, dwNewLong)
```
