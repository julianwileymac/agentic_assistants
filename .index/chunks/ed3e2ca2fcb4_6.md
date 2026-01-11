# Chunk: ed3e2ca2fcb4_6

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/user32.py`
- lines: 599-683
- chunk: 7/20

```
 translated coordinates.
        """
        topleft = ScreenToClient(hWnd, (self.left, self.top))
        bottomright = ScreenToClient(hWnd, (self.bottom, self.right))
        return Rect(topleft.x, topleft.y, bottomright.x, bottomright.y)

    def client_to_screen(self, hWnd):
        """
        Translates window client coordinates to screen coordinates.

        @see: L{screen_to_client}, L{translate}

        @type  hWnd: int or L{HWND} or L{system.Window}
        @param hWnd: Window handle.

        @rtype:  L{Rect}
        @return: New object containing the translated coordinates.
        """
        topleft = ClientToScreen(hWnd, (self.left, self.top))
        bottomright = ClientToScreen(hWnd, (self.bottom, self.right))
        return Rect(topleft.x, topleft.y, bottomright.x, bottomright.y)

    def translate(self, hWndFrom=HWND_DESKTOP, hWndTo=HWND_DESKTOP):
        """
        Translate coordinates from one window to another.

        @see: L{client_to_screen}, L{screen_to_client}

        @type  hWndFrom: int or L{HWND} or L{system.Window}
        @param hWndFrom: Window handle to translate from.
            Use C{HWND_DESKTOP} for screen coordinates.

        @type  hWndTo: int or L{HWND} or L{system.Window}
        @param hWndTo: Window handle to translate to.
            Use C{HWND_DESKTOP} for screen coordinates.

        @rtype:  L{Rect}
        @return: New object containing the translated coordinates.
        """
        points = [(self.left, self.top), (self.right, self.bottom)]
        return MapWindowPoints(hWndFrom, hWndTo, points)


class WindowPlacement(object):
    """
    Python wrapper over the L{WINDOWPLACEMENT} class.
    """

    def __init__(self, wp=None):
        """
        @type  wp: L{WindowPlacement} or L{WINDOWPLACEMENT}
        @param wp: Another window placement object.
        """

        # Initialize all properties with empty values.
        self.flags = 0
        self.showCmd = 0
        self.ptMinPosition = Point()
        self.ptMaxPosition = Point()
        self.rcNormalPosition = Rect()

        # If a window placement was given copy it's properties.
        if wp:
            self.flags = wp.flags
            self.showCmd = wp.showCmd
            self.ptMinPosition = Point(wp.ptMinPosition.x, wp.ptMinPosition.y)
            self.ptMaxPosition = Point(wp.ptMaxPosition.x, wp.ptMaxPosition.y)
            self.rcNormalPosition = Rect(
                wp.rcNormalPosition.left,
                wp.rcNormalPosition.top,
                wp.rcNormalPosition.right,
                wp.rcNormalPosition.bottom,
            )

    @property
    def _as_parameter_(self):
        """
        Compatibility with ctypes.
        Allows passing transparently a Point object to an API call.
        """
        wp = WINDOWPLACEMENT()
        wp.length = sizeof(wp)
        wp.flags = self.flags
        wp.showCmd = self.showCmd
```
