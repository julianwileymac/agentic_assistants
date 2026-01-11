# Chunk: 7baed29eb50c_2

- source: `.venv-lab/Lib/site-packages/colorama-0.4.6.dist-info/METADATA`
- lines: 132-205
- chunk: 3/7

```
ect to ANSI escape handling.

It's safe to call this function multiple times. It's safe to call this function
on non-Windows platforms, but it won't do anything. It's safe to call this
function when one or both of your stdout/stderr are redirected to a file – it
won't do anything to those streams.

Alternatively, you can use the older interface with more features (but also more
potential footguns):

.. code-block:: python

    from colorama import init
    init()

This does the same thing as ``just_fix_windows_console``, except for the
following differences:

- It's not safe to call ``init`` multiple times; you can end up with multiple
  layers of wrapping and broken ANSI support.

- Colorama will apply a heuristic to guess whether stdout/stderr support ANSI,
  and if it thinks they don't, then it will wrap ``sys.stdout`` and
  ``sys.stderr`` in a magic file object that strips out ANSI escape sequences
  before printing them. This happens on all platforms, and can be convenient if
  you want to write your code to emit ANSI escape sequences unconditionally, and
  let Colorama decide whether they should actually be output. But note that
  Colorama's heuristic is not particularly clever.

- ``init`` also accepts explicit keyword args to enable/disable various
  functionality – see below.

To stop using Colorama before your program exits, simply call ``deinit()``.
This will restore ``stdout`` and ``stderr`` to their original values, so that
Colorama is disabled. To resume using Colorama again, call ``reinit()``; it is
cheaper than calling ``init()`` again (but does the same thing).

Most users should depend on ``colorama >= 0.4.6``, and use
``just_fix_windows_console``. The old ``init`` interface will be supported
indefinitely for backwards compatibility, but we don't plan to fix any issues
with it, also for backwards compatibility.

Colored Output
..............

Cross-platform printing of colored text can then be done using Colorama's
constant shorthand for ANSI escape sequences. These are deliberately
rudimentary, see below.

.. code-block:: python

    from colorama import Fore, Back, Style
    print(Fore.RED + 'some red text')
    print(Back.GREEN + 'and with a green background')
    print(Style.DIM + 'and in dim text')
    print(Style.RESET_ALL)
    print('back to normal now')

...or simply by manually printing ANSI sequences from your own code:

.. code-block:: python

    print('\033[31m' + 'some red text')
    print('\033[39m') # and reset to default color

...or, Colorama can be used in conjunction with existing ANSI libraries
such as the venerable `Termcolor <https://pypi.org/project/termcolor/>`_
the fabulous `Blessings <https://pypi.org/project/blessings/>`_,
or the incredible `_Rich <https://pypi.org/project/rich/>`_.

If you wish Colorama's Fore, Back and Style constants were more capable,
then consider using one of the above highly capable libraries to generate
colors, etc, and use Colorama just for its primary purpose: to convert
```
