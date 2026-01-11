# Chunk: 6bfbecc32bf4_4

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/output/vt100.py`
- lines: 363-442
- chunk: 5/9

```
return [code]

                # True colors. (Only when this feature is enabled.)
                elif self.color_depth == ColorDepth.DEPTH_24_BIT:
                    r, g, b = rgb
                    return [(48 if bg else 38), 2, r, g, b]

                # 256 RGB colors.
                else:
                    return [(48 if bg else 38), 5, _256_colors[rgb]]

        result: list[int] = []
        result.extend(get(fg_color, False))
        result.extend(get(bg_color, True))

        return map(str, result)


def _get_size(fileno: int) -> tuple[int, int]:
    """
    Get the size of this pseudo terminal.

    :param fileno: stdout.fileno()
    :returns: A (rows, cols) tuple.
    """
    size = os.get_terminal_size(fileno)
    return size.lines, size.columns


class Vt100_Output(Output):
    """
    :param get_size: A callable which returns the `Size` of the output terminal.
    :param stdout: Any object with has a `write` and `flush` method + an 'encoding' property.
    :param term: The terminal environment variable. (xterm, xterm-256color, linux, ...)
    :param enable_cpr: When `True` (the default), send "cursor position
        request" escape sequences to the output in order to detect the cursor
        position. That way, we can properly determine how much space there is
        available for the UI (especially for drop down menus) to render. The
        `Renderer` will still try to figure out whether the current terminal
        does respond to CPR escapes. When `False`, never attempt to send CPR
        requests.
    """

    # For the error messages. Only display "Output is not a terminal" once per
    # file descriptor.
    _fds_not_a_terminal: set[int] = set()

    def __init__(
        self,
        stdout: TextIO,
        get_size: Callable[[], Size],
        term: str | None = None,
        default_color_depth: ColorDepth | None = None,
        enable_bell: bool = True,
        enable_cpr: bool = True,
    ) -> None:
        assert all(hasattr(stdout, a) for a in ("write", "flush"))

        self._buffer: list[str] = []
        self.stdout: TextIO = stdout
        self.default_color_depth = default_color_depth
        self._get_size = get_size
        self.term = term
        self.enable_bell = enable_bell
        self.enable_cpr = enable_cpr

        # Cache for escape codes.
        self._escape_code_caches: dict[ColorDepth, _EscapeCodeCache] = {
            ColorDepth.DEPTH_1_BIT: _EscapeCodeCache(ColorDepth.DEPTH_1_BIT),
            ColorDepth.DEPTH_4_BIT: _EscapeCodeCache(ColorDepth.DEPTH_4_BIT),
            ColorDepth.DEPTH_8_BIT: _EscapeCodeCache(ColorDepth.DEPTH_8_BIT),
            ColorDepth.DEPTH_24_BIT: _EscapeCodeCache(ColorDepth.DEPTH_24_BIT),
        }

        # Keep track of whether the cursor shape was ever changed.
        # (We don't restore the cursor shape if it was never changed - by
        # default, we don't change them.)
        self._cursor_shape_changed = False
```
