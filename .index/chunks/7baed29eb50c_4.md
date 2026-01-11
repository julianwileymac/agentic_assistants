# Chunk: 7baed29eb50c_4

- source: `.venv-lab/Lib/site-packages/colorama-0.4.6.dist-info/METADATA`
- lines: 270-358
- chunk: 5/7

```
` and ``sys.stderr``
    with proxy objects, which override the ``.write()`` method to do their work.
    If this wrapping causes you problems, then this can be disabled by passing
    ``init(wrap=False)``. The default behaviour is to wrap if ``autoreset`` or
    ``strip`` or ``convert`` are True.

    When wrapping is disabled, colored printing on non-Windows platforms will
    continue to work as normal. To do cross-platform colored output, you can
    use Colorama's ``AnsiToWin32`` proxy directly:

    .. code-block:: python

        import sys
        from colorama import init, AnsiToWin32
        init(wrap=False)
        stream = AnsiToWin32(sys.stderr).stream

        # Python 2
        print >>stream, Fore.BLUE + 'blue text on stderr'

        # Python 3
        print(Fore.BLUE + 'blue text on stderr', file=stream)

Recognised ANSI Sequences
.........................

ANSI sequences generally take the form::

    ESC [ <param> ; <param> ... <command>

Where ``<param>`` is an integer, and ``<command>`` is a single letter. Zero or
more params are passed to a ``<command>``. If no params are passed, it is
generally synonymous with passing a single zero. No spaces exist in the
sequence; they have been inserted here simply to read more easily.

The only ANSI sequences that Colorama converts into win32 calls are::

    ESC [ 0 m       # reset all (colors and brightness)
    ESC [ 1 m       # bright
    ESC [ 2 m       # dim (looks same as normal brightness)
    ESC [ 22 m      # normal brightness

    # FOREGROUND:
    ESC [ 30 m      # black
    ESC [ 31 m      # red
    ESC [ 32 m      # green
    ESC [ 33 m      # yellow
    ESC [ 34 m      # blue
    ESC [ 35 m      # magenta
    ESC [ 36 m      # cyan
    ESC [ 37 m      # white
    ESC [ 39 m      # reset

    # BACKGROUND
    ESC [ 40 m      # black
    ESC [ 41 m      # red
    ESC [ 42 m      # green
    ESC [ 43 m      # yellow
    ESC [ 44 m      # blue
    ESC [ 45 m      # magenta
    ESC [ 46 m      # cyan
    ESC [ 47 m      # white
    ESC [ 49 m      # reset

    # cursor positioning
    ESC [ y;x H     # position cursor at x across, y down
    ESC [ y;x f     # position cursor at x across, y down
    ESC [ n A       # move cursor n lines up
    ESC [ n B       # move cursor n lines down
    ESC [ n C       # move cursor n characters forward
    ESC [ n D       # move cursor n characters backward

    # clear the screen
    ESC [ mode J    # clear the screen

    # clear the line
    ESC [ mode K    # clear the line

Multiple numeric params to the ``'m'`` command can be combined into a single
sequence::

    ESC [ 36 ; 45 ; 1 m     # bright cyan text on magenta background

All other ANSI sequences of the form ``ESC [ <param> ; <param> ... <command>``
are silently stripped from the output on Windows.

Any other form of ANSI sequence, such as single-character codes or alternative
initial characters, are not recognised or stripped. It would be cool to add
```
