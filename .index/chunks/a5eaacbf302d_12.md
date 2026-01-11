# Chunk: a5eaacbf302d_12

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/version.py`
- lines: 1012-1086
- chunk: 13/13

```
ersionInfoA
    _GetFileVersionInfoA.argtypes = [LPSTR, DWORD, DWORD, LPVOID]
    _GetFileVersionInfoA.restype = bool
    _GetFileVersionInfoA.errcheck = RaiseIfZero

    _GetFileVersionInfoSizeA = windll.version.GetFileVersionInfoSizeA
    _GetFileVersionInfoSizeA.argtypes = [LPSTR, LPVOID]
    _GetFileVersionInfoSizeA.restype = DWORD
    _GetFileVersionInfoSizeA.errcheck = RaiseIfZero

    dwLen = _GetFileVersionInfoSizeA(lptstrFilename, None)
    lpData = ctypes.create_string_buffer(dwLen)
    _GetFileVersionInfoA(lptstrFilename, 0, dwLen, byref(lpData))
    return lpData


def GetFileVersionInfoW(lptstrFilename):
    _GetFileVersionInfoW = windll.version.GetFileVersionInfoW
    _GetFileVersionInfoW.argtypes = [LPWSTR, DWORD, DWORD, LPVOID]
    _GetFileVersionInfoW.restype = bool
    _GetFileVersionInfoW.errcheck = RaiseIfZero

    _GetFileVersionInfoSizeW = windll.version.GetFileVersionInfoSizeW
    _GetFileVersionInfoSizeW.argtypes = [LPWSTR, LPVOID]
    _GetFileVersionInfoSizeW.restype = DWORD
    _GetFileVersionInfoSizeW.errcheck = RaiseIfZero

    dwLen = _GetFileVersionInfoSizeW(lptstrFilename, None)
    lpData = ctypes.create_string_buffer(dwLen)  # not a string!
    _GetFileVersionInfoW(lptstrFilename, 0, dwLen, byref(lpData))
    return lpData


GetFileVersionInfo = GuessStringType(GetFileVersionInfoA, GetFileVersionInfoW)


# BOOL WINAPI VerQueryValue(
#   _In_   LPCVOID pBlock,
#   _In_   LPCTSTR lpSubBlock,
#   _Out_  LPVOID *lplpBuffer,
#   _Out_  PUINT puLen
# );
def VerQueryValueA(pBlock, lpSubBlock):
    _VerQueryValueA = windll.version.VerQueryValueA
    _VerQueryValueA.argtypes = [LPVOID, LPSTR, LPVOID, POINTER(UINT)]
    _VerQueryValueA.restype = bool
    _VerQueryValueA.errcheck = RaiseIfZero

    lpBuffer = LPVOID(0)
    uLen = UINT(0)
    _VerQueryValueA(pBlock, lpSubBlock, byref(lpBuffer), byref(uLen))
    return lpBuffer, uLen.value


def VerQueryValueW(pBlock, lpSubBlock):
    _VerQueryValueW = windll.version.VerQueryValueW
    _VerQueryValueW.argtypes = [LPVOID, LPWSTR, LPVOID, POINTER(UINT)]
    _VerQueryValueW.restype = bool
    _VerQueryValueW.errcheck = RaiseIfZero

    lpBuffer = LPVOID(0)
    uLen = UINT(0)
    _VerQueryValueW(pBlock, lpSubBlock, byref(lpBuffer), byref(uLen))
    return lpBuffer, uLen.value


VerQueryValue = GuessStringType(VerQueryValueA, VerQueryValueW)

# ==============================================================================
# This calculates the list of exported symbols.
_all = set(vars().keys()).difference(_all)
__all__ = [_x for _x in _all if not _x.startswith("_")]
__all__.sort()
# ==============================================================================
```
