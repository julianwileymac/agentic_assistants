# Chunk: 6bf0f0cc36da_9

- source: `.venv-lab/Lib/site-packages/tornado/options.py`
- lines: 652-746
- chunk: 10/10

```
timedelta:
        try:
            sum = datetime.timedelta()
            start = 0
            while start < len(value):
                m = self._TIMEDELTA_PATTERN.match(value, start)
                if not m:
                    raise Exception()
                num = float(m.group(1))
                units = m.group(2) or "seconds"
                units = self._TIMEDELTA_ABBREV_DICT.get(units, units)

                sum += datetime.timedelta(**{units: num})
                start = m.end()
            return sum
        except Exception:
            raise

    def _parse_bool(self, value: str) -> bool:
        return value.lower() not in ("false", "0", "f")

    def _parse_string(self, value: str) -> str:
        return _unicode(value)


options = OptionParser()
"""Global options object.

All defined options are available as attributes on this object.
"""


def define(
    name: str,
    default: Any = None,
    type: Optional[type] = None,
    help: Optional[str] = None,
    metavar: Optional[str] = None,
    multiple: bool = False,
    group: Optional[str] = None,
    callback: Optional[Callable[[Any], None]] = None,
) -> None:
    """Defines an option in the global namespace.

    See `OptionParser.define`.
    """
    return options.define(
        name,
        default=default,
        type=type,
        help=help,
        metavar=metavar,
        multiple=multiple,
        group=group,
        callback=callback,
    )


def parse_command_line(
    args: Optional[List[str]] = None, final: bool = True
) -> List[str]:
    """Parses global options from the command line.

    See `OptionParser.parse_command_line`.
    """
    return options.parse_command_line(args, final=final)


def parse_config_file(path: str, final: bool = True) -> None:
    """Parses global options from a config file.

    See `OptionParser.parse_config_file`.
    """
    return options.parse_config_file(path, final=final)


def print_help(file: Optional[TextIO] = None) -> None:
    """Prints all the command line options to stderr (or another file).

    See `OptionParser.print_help`.
    """
    return options.print_help(file)


def add_parse_callback(callback: Callable[[], None]) -> None:
    """Adds a parse callback, to be invoked when option parsing is done.

    See `OptionParser.add_parse_callback`
    """
    options.add_parse_callback(callback)


# Default options
define_logging_options(options)
```
