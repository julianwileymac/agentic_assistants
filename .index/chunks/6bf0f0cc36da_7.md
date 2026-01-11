# Chunk: 6bf0f0cc36da_7

- source: `.venv-lab/Lib/site-packages/tornado/options.py`
- lines: 502-581
- chunk: 8/10

```
of setting a new one (assuming that
    the object does not capture ``__setattr__``, so the patch
    created a new attribute in ``__dict__``).

    _Mockable's getattr and setattr pass through to the underlying
    OptionParser, and delattr undoes the effect of a previous setattr.
    """

    def __init__(self, options: OptionParser) -> None:
        # Modify __dict__ directly to bypass __setattr__
        self.__dict__["_options"] = options
        self.__dict__["_originals"] = {}

    def __getattr__(self, name: str) -> Any:
        return getattr(self._options, name)

    def __setattr__(self, name: str, value: Any) -> None:
        assert name not in self._originals, "don't reuse mockable objects"
        self._originals[name] = getattr(self._options, name)
        setattr(self._options, name, value)

    def __delattr__(self, name: str) -> None:
        setattr(self._options, name, self._originals.pop(name))


class _Option:
    # This class could almost be made generic, but the way the types
    # interact with the multiple argument makes this tricky. (default
    # and the callback use List[T], but type is still Type[T]).
    UNSET = object()

    def __init__(
        self,
        name: str,
        default: Any = None,
        type: Optional[type] = None,
        help: Optional[str] = None,
        metavar: Optional[str] = None,
        multiple: bool = False,
        file_name: Optional[str] = None,
        group_name: Optional[str] = None,
        callback: Optional[Callable[[Any], None]] = None,
    ) -> None:
        if default is None and multiple:
            default = []
        self.name = name
        if type is None:
            raise ValueError("type must not be None")
        self.type = type
        self.help = help
        self.metavar = metavar
        self.multiple = multiple
        self.file_name = file_name
        self.group_name = group_name
        self.callback = callback
        self.default = default
        self._value = _Option.UNSET  # type: Any

    def value(self) -> Any:
        return self.default if self._value is _Option.UNSET else self._value

    def parse(self, value: str) -> Any:
        _parse = {
            datetime.datetime: self._parse_datetime,
            datetime.timedelta: self._parse_timedelta,
            bool: self._parse_bool,
            basestring_type: self._parse_string,
        }.get(
            self.type, self.type
        )  # type: Callable[[str], Any]
        if self.multiple:
            self._value = []
            for part in value.split(","):
                if issubclass(self.type, numbers.Integral):
                    # allow ranges of the form X:Y (inclusive at both ends)
                    lo_str, _, hi_str = part.partition(":")
                    lo = _parse(lo_str)
                    hi = _parse(hi_str) if hi_str else lo
                    self._value.extend(range(lo, hi + 1))
```
