# Chunk: daf39dc884ba_2

- source: `.venv-lab/Lib/site-packages/pip/_internal/cli/cmdoptions.py`
- lines: 166-291
- chunk: 3/12

```
, Option] = partial(
    Option,
    "--isolated",
    dest="isolated_mode",
    action="store_true",
    default=False,
    help=(
        "Run pip in an isolated mode, ignoring environment variables and user "
        "configuration."
    ),
)

require_virtualenv: Callable[..., Option] = partial(
    Option,
    "--require-virtualenv",
    "--require-venv",
    dest="require_venv",
    action="store_true",
    default=False,
    help=(
        "Allow pip to only run in a virtual environment; exit with an error otherwise."
    ),
)

override_externally_managed: Callable[..., Option] = partial(
    Option,
    "--break-system-packages",
    dest="override_externally_managed",
    action="store_true",
    help="Allow pip to modify an EXTERNALLY-MANAGED Python installation",
)

python: Callable[..., Option] = partial(
    Option,
    "--python",
    dest="python",
    help="Run pip with the specified Python interpreter.",
)

verbose: Callable[..., Option] = partial(
    Option,
    "-v",
    "--verbose",
    dest="verbose",
    action="count",
    default=0,
    help="Give more output. Option is additive, and can be used up to 3 times.",
)

no_color: Callable[..., Option] = partial(
    Option,
    "--no-color",
    dest="no_color",
    action="store_true",
    default=False,
    help="Suppress colored output.",
)

version: Callable[..., Option] = partial(
    Option,
    "-V",
    "--version",
    dest="version",
    action="store_true",
    help="Show version and exit.",
)

quiet: Callable[..., Option] = partial(
    Option,
    "-q",
    "--quiet",
    dest="quiet",
    action="count",
    default=0,
    help=(
        "Give less output. Option is additive, and can be used up to 3"
        " times (corresponding to WARNING, ERROR, and CRITICAL logging"
        " levels)."
    ),
)

progress_bar: Callable[..., Option] = partial(
    Option,
    "--progress-bar",
    dest="progress_bar",
    type="choice",
    choices=["auto", "on", "off", "raw"],
    default="auto",
    help=(
        "Specify whether the progress bar should be used. In 'auto'"
        " mode, --quiet will suppress all progress bars."
        " [auto, on, off, raw] (default: auto)"
    ),
)

log: Callable[..., Option] = partial(
    PipOption,
    "--log",
    "--log-file",
    "--local-log",
    dest="log",
    metavar="path",
    type="path",
    help="Path to a verbose appending log.",
)

no_input: Callable[..., Option] = partial(
    Option,
    # Don't ask for input
    "--no-input",
    dest="no_input",
    action="store_true",
    default=False,
    help="Disable prompting for input.",
)

keyring_provider: Callable[..., Option] = partial(
    Option,
    "--keyring-provider",
    dest="keyring_provider",
    choices=["auto", "disabled", "import", "subprocess"],
    default="auto",
    help=(
        "Enable the credential lookup via the keyring library if user input is allowed."
        " Specify which mechanism to use [auto, disabled, import, subprocess]."
```
