# Chunk: daf39dc884ba_9

- source: `.venv-lab/Lib/site-packages/pip/_internal/cli/cmdoptions.py`
- lines: 841-952
- chunk: 10/12

```
p="Disable isolation when building a modern source distribution. "
    "Build dependencies specified by PEP 518 must be already installed "
    "if this option is used.",
)

check_build_deps: Callable[..., Option] = partial(
    Option,
    "--check-build-dependencies",
    dest="check_build_deps",
    action="store_true",
    default=False,
    help="Check the build dependencies.",
)


use_pep517: Any = partial(
    Option,
    "--use-pep517",
    dest="use_pep517",
    action="store_true",
    default=True,
    help=SUPPRESS_HELP,
)


def _handle_config_settings(
    option: Option, opt_str: str, value: str, parser: OptionParser
) -> None:
    key, sep, val = value.partition("=")
    if sep != "=":
        parser.error(f"Arguments to {opt_str} must be of the form KEY=VAL")
    dest = getattr(parser.values, option.dest)
    if dest is None:
        dest = {}
        setattr(parser.values, option.dest, dest)
    if key in dest:
        if isinstance(dest[key], list):
            dest[key].append(val)
        else:
            dest[key] = [dest[key], val]
    else:
        dest[key] = val


config_settings: Callable[..., Option] = partial(
    Option,
    "-C",
    "--config-settings",
    dest="config_settings",
    type=str,
    action="callback",
    callback=_handle_config_settings,
    metavar="settings",
    help="Configuration settings to be passed to the build backend. "
    "Settings take the form KEY=VALUE. Use multiple --config-settings options "
    "to pass multiple keys to the backend.",
)

no_clean: Callable[..., Option] = partial(
    Option,
    "--no-clean",
    action="store_true",
    default=False,
    help="Don't clean up build directories.",
)

pre: Callable[..., Option] = partial(
    Option,
    "--pre",
    action="store_true",
    default=False,
    help="Include pre-release and development versions. By default, "
    "pip only finds stable versions.",
)

json: Callable[..., Option] = partial(
    Option,
    "--json",
    action="store_true",
    default=False,
    help="Output data in a machine-readable JSON format.",
)

disable_pip_version_check: Callable[..., Option] = partial(
    Option,
    "--disable-pip-version-check",
    dest="disable_pip_version_check",
    action="store_true",
    default=False,
    help="Don't periodically check PyPI to determine whether a new version "
    "of pip is available for download. Implied with --no-index.",
)

root_user_action: Callable[..., Option] = partial(
    Option,
    "--root-user-action",
    dest="root_user_action",
    default="warn",
    choices=["warn", "ignore"],
    help="Action if pip is run as a root user [warn, ignore] (default: warn)",
)


def _handle_merge_hash(
    option: Option, opt_str: str, value: str, parser: OptionParser
) -> None:
    """Given a value spelled "algo:digest", append the digest to a list
    pointed to in a dict by the algo name."""
    if not parser.values.hashes:
        parser.values.hashes = {}
    try:
```
