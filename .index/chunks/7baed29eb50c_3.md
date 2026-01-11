# Chunk: 7baed29eb50c_3

- source: `.venv-lab/Lib/site-packages/colorama-0.4.6.dist-info/METADATA`
- lines: 199-276
- chunk: 4/7

```
ject/blessings/>`_,
or the incredible `_Rich <https://pypi.org/project/rich/>`_.

If you wish Colorama's Fore, Back and Style constants were more capable,
then consider using one of the above highly capable libraries to generate
colors, etc, and use Colorama just for its primary purpose: to convert
those ANSI sequences to also work on Windows:

SIMILARLY, do not send PRs adding the generation of new ANSI types to Colorama.
We are only interested in converting ANSI codes to win32 API calls, not
shortcuts like the above to generate ANSI characters.

.. code-block:: python

    from colorama import just_fix_windows_console
    from termcolor import colored

    # use Colorama to make Termcolor work on Windows too
    just_fix_windows_console()

    # then use Termcolor for all colored text output
    print(colored('Hello, World!', 'green', 'on_red'))

Available formatting constants are::

    Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    Style: DIM, NORMAL, BRIGHT, RESET_ALL

``Style.RESET_ALL`` resets foreground, background, and brightness. Colorama will
perform this reset automatically on program exit.

These are fairly well supported, but not part of the standard::

    Fore: LIGHTBLACK_EX, LIGHTRED_EX, LIGHTGREEN_EX, LIGHTYELLOW_EX, LIGHTBLUE_EX, LIGHTMAGENTA_EX, LIGHTCYAN_EX, LIGHTWHITE_EX
    Back: LIGHTBLACK_EX, LIGHTRED_EX, LIGHTGREEN_EX, LIGHTYELLOW_EX, LIGHTBLUE_EX, LIGHTMAGENTA_EX, LIGHTCYAN_EX, LIGHTWHITE_EX

Cursor Positioning
..................

ANSI codes to reposition the cursor are supported. See ``demos/demo06.py`` for
an example of how to generate them.

Init Keyword Args
.................

``init()`` accepts some ``**kwargs`` to override default behaviour.

init(autoreset=False):
    If you find yourself repeatedly sending reset sequences to turn off color
    changes at the end of every print, then ``init(autoreset=True)`` will
    automate that:

    .. code-block:: python

        from colorama import init
        init(autoreset=True)
        print(Fore.RED + 'some red text')
        print('automatically back to default color again')

init(strip=None):
    Pass ``True`` or ``False`` to override whether ANSI codes should be
    stripped from the output. The default behaviour is to strip if on Windows
    or if output is redirected (not a tty).

init(convert=None):
    Pass ``True`` or ``False`` to override whether to convert ANSI codes in the
    output into win32 calls. The default behaviour is to convert if on Windows
    and output is to a tty (terminal).

init(wrap=True):
    On Windows, Colorama works by replacing ``sys.stdout`` and ``sys.stderr``
    with proxy objects, which override the ``.write()`` method to do their work.
    If this wrapping causes you problems, then this can be disabled by passing
    ``init(wrap=False)``. The default behaviour is to wrap if ``autoreset`` or
    ``strip`` or ``convert`` are True.
```
