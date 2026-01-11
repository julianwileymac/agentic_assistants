# Chunk: ed3e2ca2fcb4_19

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 1751-1833
- chunk: 20/20

```
ClipboardFormatW(lpString):
    _RegisterClipboardFormatW = windll.user32.RegisterClipboardFormatW
    _RegisterClipboardFormatW.argtypes = [LPWSTR]
    _RegisterClipboardFormatW.restype = UINT
    _RegisterClipboardFormatW.errcheck = RaiseIfZero
    return _RegisterClipboardFormatW(lpString)


RegisterClipboardFormat = GuessStringType(RegisterClipboardFormatA, RegisterClipboardFormatW)


# HANDLE WINAPI GetProp(
#   __in  HWND hWnd,
#   __in  LPCTSTR lpString
# );
def GetPropA(hWnd, lpString):
    _GetPropA = windll.user32.GetPropA
    _GetPropA.argtypes = [HWND, LPSTR]
    _GetPropA.restype = HANDLE
    return _GetPropA(hWnd, lpString)


def GetPropW(hWnd, lpString):
    _GetPropW = windll.user32.GetPropW
    _GetPropW.argtypes = [HWND, LPWSTR]
    _GetPropW.restype = HANDLE
    return _GetPropW(hWnd, lpString)


GetProp = GuessStringType(GetPropA, GetPropW)


# BOOL WINAPI SetProp(
#   __in      HWND hWnd,
#   __in      LPCTSTR lpString,
#   __in_opt  HANDLE hData
# );
def SetPropA(hWnd, lpString, hData):
    _SetPropA = windll.user32.SetPropA
    _SetPropA.argtypes = [HWND, LPSTR, HANDLE]
    _SetPropA.restype = BOOL
    _SetPropA.errcheck = RaiseIfZero
    _SetPropA(hWnd, lpString, hData)


def SetPropW(hWnd, lpString, hData):
    _SetPropW = windll.user32.SetPropW
    _SetPropW.argtypes = [HWND, LPWSTR, HANDLE]
    _SetPropW.restype = BOOL
    _SetPropW.errcheck = RaiseIfZero
    _SetPropW(hWnd, lpString, hData)


SetProp = GuessStringType(SetPropA, SetPropW)


# HANDLE WINAPI RemoveProp(
#   __in  HWND hWnd,
#   __in  LPCTSTR lpString
# );
def RemovePropA(hWnd, lpString):
    _RemovePropA = windll.user32.RemovePropA
    _RemovePropA.argtypes = [HWND, LPSTR]
    _RemovePropA.restype = HANDLE
    return _RemovePropA(hWnd, lpString)


def RemovePropW(hWnd, lpString):
    _RemovePropW = windll.user32.RemovePropW
    _RemovePropW.argtypes = [HWND, LPWSTR]
    _RemovePropW.restype = HANDLE
    return _RemovePropW(hWnd, lpString)


RemoveProp = GuessStringType(RemovePropA, RemovePropW)

# ==============================================================================
# This calculates the list of exported symbols.
_all = set(vars().keys()).difference(_all)
__all__ = [_x for _x in _all if not _x.startswith("_")]
__all__.sort()
# ==============================================================================
```
