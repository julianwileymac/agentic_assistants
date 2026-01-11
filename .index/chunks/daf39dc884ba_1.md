# Chunk: daf39dc884ba_1

- source: `.venv-lab/Lib/site-packages/pip/_internal/cli/cmdoptions.py`
- lines: 83-179
- chunk: 2/12

```
ictions must not combine
    # source distributions and dist-specific wheels, as they are not
    # guaranteed to be locally compatible.
    if dist_restriction_set and sdist_dependencies_allowed:
        raise CommandError(
            "When restricting platform and interpreter constraints using "
            "--python-version, --platform, --abi, or --implementation, "
            "either --no-deps must be set, or --only-binary=:all: must be "
            "set and --no-binary must not be set (or must be set to "
            ":none:)."
        )

    if check_target:
        if not options.dry_run and dist_restriction_set and not options.target_dir:
            raise CommandError(
                "Can not use any platform or abi specific options unless "
                "installing via '--target' or using '--dry-run'"
            )


def check_build_constraints(options: Values) -> None:
    """Function for validating build constraints options.

    :param options: The OptionParser options.
    """
    if hasattr(options, "build_constraints") and options.build_constraints:
        if not options.build_isolation:
            raise CommandError(
                "--build-constraint cannot be used with --no-build-isolation."
            )

        # Import here to avoid circular imports
        from pip._internal.network.session import PipSession
        from pip._internal.req.req_file import get_file_content

        # Eagerly check build constraints file contents
        # is valid so that we don't fail in when trying
        # to check constraints in isolated build process
        with PipSession() as session:
            for constraint_file in options.build_constraints:
                get_file_content(constraint_file, session)


def _path_option_check(option: Option, opt: str, value: str) -> str:
    return os.path.expanduser(value)


def _package_name_option_check(option: Option, opt: str, value: str) -> str:
    return canonicalize_name(value)


class PipOption(Option):
    TYPES = Option.TYPES + ("path", "package_name")
    TYPE_CHECKER = Option.TYPE_CHECKER.copy()
    TYPE_CHECKER["package_name"] = _package_name_option_check
    TYPE_CHECKER["path"] = _path_option_check


###########
# options #
###########

help_: Callable[..., Option] = partial(
    Option,
    "-h",
    "--help",
    dest="help",
    action="help",
    help="Show help.",
)

debug_mode: Callable[..., Option] = partial(
    Option,
    "--debug",
    dest="debug_mode",
    action="store_true",
    default=False,
    help=(
        "Let unhandled exceptions propagate outside the main subroutine, "
        "instead of logging them to stderr."
    ),
)

isolated_mode: Callable[..., Option] = partial(
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
```
