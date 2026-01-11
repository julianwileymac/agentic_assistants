# Chunk: ed3e2ca2fcb4_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 65-208
- chunk: 2/20

```
M type.
    Used automatically by SendMessage, PostMessage, etc.
    You shouldn't need to call this function.
    """
    return ctypes.cast(lParam, LPARAM)


class __WindowEnumerator(object):
    """
    Window enumerator class. Used internally by the window enumeration APIs.
    """

    def __init__(self):
        self.hwnd = list()

    def __call__(self, hwnd, lParam):
        ##        print hwnd  # XXX DEBUG
        self.hwnd.append(hwnd)
        return TRUE


# --- Types --------------------------------------------------------------------

WNDENUMPROC = WINFUNCTYPE(BOOL, HWND, PVOID)

# --- Constants ----------------------------------------------------------------

HWND_DESKTOP = 0
HWND_TOP = 1
HWND_BOTTOM = 1
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
HWND_MESSAGE = -3

# GetWindowLong / SetWindowLong
GWL_WNDPROC = -4
GWL_HINSTANCE = -6
GWL_HWNDPARENT = -8
GWL_ID = -12
GWL_STYLE = -16
GWL_EXSTYLE = -20
GWL_USERDATA = -21

# GetWindowLongPtr / SetWindowLongPtr
GWLP_WNDPROC = GWL_WNDPROC
GWLP_HINSTANCE = GWL_HINSTANCE
GWLP_HWNDPARENT = GWL_HWNDPARENT
GWLP_STYLE = GWL_STYLE
GWLP_EXSTYLE = GWL_EXSTYLE
GWLP_USERDATA = GWL_USERDATA
GWLP_ID = GWL_ID

# ShowWindow
SW_HIDE = 0
SW_SHOWNORMAL = 1
SW_NORMAL = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3
SW_MAXIMIZE = 3
SW_SHOWNOACTIVATE = 4
SW_SHOW = 5
SW_MINIMIZE = 6
SW_SHOWMINNOACTIVE = 7
SW_SHOWNA = 8
SW_RESTORE = 9
SW_SHOWDEFAULT = 10
SW_FORCEMINIMIZE = 11

# SendMessageTimeout flags
SMTO_NORMAL = 0
SMTO_BLOCK = 1
SMTO_ABORTIFHUNG = 2
SMTO_NOTIMEOUTIFNOTHUNG = 8
SMTO_ERRORONEXIT = 0x20

# WINDOWPLACEMENT flags
WPF_SETMINPOSITION = 1
WPF_RESTORETOMAXIMIZED = 2
WPF_ASYNCWINDOWPLACEMENT = 4

# GetAncestor flags
GA_PARENT = 1
GA_ROOT = 2
GA_ROOTOWNER = 3

# GetWindow flags
GW_HWNDFIRST = 0
GW_HWNDLAST = 1
GW_HWNDNEXT = 2
GW_HWNDPREV = 3
GW_OWNER = 4
GW_CHILD = 5
GW_ENABLEDPOPUP = 6

# --- Window messages ----------------------------------------------------------

WM_USER = 0x400
WM_APP = 0x800

WM_NULL = 0
WM_CREATE = 1
WM_DESTROY = 2
WM_MOVE = 3
WM_SIZE = 5
WM_ACTIVATE = 6
WA_INACTIVE = 0
WA_ACTIVE = 1
WA_CLICKACTIVE = 2
WM_SETFOCUS = 7
WM_KILLFOCUS = 8
WM_ENABLE = 0x0A
WM_SETREDRAW = 0x0B
WM_SETTEXT = 0x0C
WM_GETTEXT = 0x0D
WM_GETTEXTLENGTH = 0x0E
WM_PAINT = 0x0F
WM_CLOSE = 0x10
WM_QUERYENDSESSION = 0x11
WM_QUIT = 0x12
WM_QUERYOPEN = 0x13
WM_ERASEBKGND = 0x14
WM_SYSCOLORCHANGE = 0x15
WM_ENDSESSION = 0x16
WM_SHOWWINDOW = 0x18
WM_WININICHANGE = 0x1A
WM_SETTINGCHANGE = WM_WININICHANGE
WM_DEVMODECHANGE = 0x1B
WM_ACTIVATEAPP = 0x1C
WM_FONTCHANGE = 0x1D
WM_TIMECHANGE = 0x1E
WM_CANCELMODE = 0x1F
WM_SETCURSOR = 0x20
WM_MOUSEACTIVATE = 0x21
WM_CHILDACTIVATE = 0x22
WM_QUEUESYNC = 0x23
WM_GETMINMAXINFO = 0x24
WM_PAINTICON = 0x26
WM_ICONERASEBKGND = 0x27
WM_NEXTDLGCTL = 0x28
WM_SPOOLERSTATUS = 0x2A
WM_DRAWITEM = 0x2B
WM_MEASUREITEM = 0x2C
WM_DELETEITEM = 0x2D
```
