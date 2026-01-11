# Chunk: ed3e2ca2fcb4_4

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 424-523
- chunk: 5/20

```
        @see: L{POINT}
        @type  x: int
        @param x: Horizontal coordinate
        @type  y: int
        @param y: Vertical coordinate
        """
        self.x = x
        self.y = y

    def __iter__(self):
        return (self.x, self.y).__iter__()

    def __len__(self):
        return 2

    def __getitem__(self, index):
        return (self.x, self.y)[index]

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError("index out of range")

    @property
    def _as_parameter_(self):
        """
        Compatibility with ctypes.
        Allows passing transparently a Point object to an API call.
        """
        return POINT(self.x, self.y)

    def screen_to_client(self, hWnd):
        """
        Translates window screen coordinates to client coordinates.

        @see: L{client_to_screen}, L{translate}

        @type  hWnd: int or L{HWND} or L{system.Window}
        @param hWnd: Window handle.

        @rtype:  L{Point}
        @return: New object containing the translated coordinates.
        """
        return ScreenToClient(hWnd, self)

    def client_to_screen(self, hWnd):
        """
        Translates window client coordinates to screen coordinates.

        @see: L{screen_to_client}, L{translate}

        @type  hWnd: int or L{HWND} or L{system.Window}
        @param hWnd: Window handle.

        @rtype:  L{Point}
        @return: New object containing the translated coordinates.
        """
        return ClientToScreen(hWnd, self)

    def translate(self, hWndFrom=HWND_DESKTOP, hWndTo=HWND_DESKTOP):
        """
        Translate coordinates from one window to another.

        @note: To translate multiple points it's more efficient to use the
            L{MapWindowPoints} function instead.

        @see: L{client_to_screen}, L{screen_to_client}

        @type  hWndFrom: int or L{HWND} or L{system.Window}
        @param hWndFrom: Window handle to translate from.
            Use C{HWND_DESKTOP} for screen coordinates.

        @type  hWndTo: int or L{HWND} or L{system.Window}
        @param hWndTo: Window handle to translate to.
            Use C{HWND_DESKTOP} for screen coordinates.

        @rtype:  L{Point}
        @return: New object containing the translated coordinates.
        """
        return MapWindowPoints(hWndFrom, hWndTo, [self])


class Rect(object):
    """
    Python wrapper over the L{RECT} class.

    @type   left: int
    @ivar   left: Horizontal coordinate for the top left corner.
    @type    top: int
    @ivar    top: Vertical coordinate for the top left corner.
    @type  right: int
    @ivar  right: Horizontal coordinate for the bottom right corner.
    @type bottom: int
    @ivar bottom: Vertical coordinate for the bottom right corner.

    @type  width: int
```
