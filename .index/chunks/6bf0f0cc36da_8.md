# Chunk: 6bf0f0cc36da_8

- source: `.venv-lab/Lib/site-packages/tornado/options.py`
- lines: 575-661
- chunk: 9/10

```
:
                    # allow ranges of the form X:Y (inclusive at both ends)
                    lo_str, _, hi_str = part.partition(":")
                    lo = _parse(lo_str)
                    hi = _parse(hi_str) if hi_str else lo
                    self._value.extend(range(lo, hi + 1))
                else:
                    self._value.append(_parse(part))
        else:
            self._value = _parse(value)
        if self.callback is not None:
            self.callback(self._value)
        return self.value()

    def set(self, value: Any) -> None:
        if self.multiple:
            if not isinstance(value, list):
                raise Error(
                    "Option %r is required to be a list of %s"
                    % (self.name, self.type.__name__)
                )
            for item in value:
                if item is not None and not isinstance(item, self.type):
                    raise Error(
                        "Option %r is required to be a list of %s"
                        % (self.name, self.type.__name__)
                    )
        else:
            if value is not None and not isinstance(value, self.type):
                raise Error(
                    "Option %r is required to be a %s (%s given)"
                    % (self.name, self.type.__name__, type(value))
                )
        self._value = value
        if self.callback is not None:
            self.callback(self._value)

    # Supported date/time formats in our options
    _DATETIME_FORMATS = [
        "%a %b %d %H:%M:%S %Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M",
        "%Y%m%d %H:%M:%S",
        "%Y%m%d %H:%M",
        "%Y-%m-%d",
        "%Y%m%d",
        "%H:%M:%S",
        "%H:%M",
    ]

    def _parse_datetime(self, value: str) -> datetime.datetime:
        for format in self._DATETIME_FORMATS:
            try:
                return datetime.datetime.strptime(value, format)
            except ValueError:
                pass
        raise Error("Unrecognized date/time format: %r" % value)

    _TIMEDELTA_ABBREV_DICT = {
        "h": "hours",
        "m": "minutes",
        "min": "minutes",
        "s": "seconds",
        "sec": "seconds",
        "ms": "milliseconds",
        "us": "microseconds",
        "d": "days",
        "w": "weeks",
    }

    _FLOAT_PATTERN = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"

    _TIMEDELTA_PATTERN = re.compile(
        r"\s*(%s)\s*(\w*)\s*" % _FLOAT_PATTERN, re.IGNORECASE
    )

    def _parse_timedelta(self, value: str) -> datetime.timedelta:
        try:
            sum = datetime.timedelta()
            start = 0
            while start < len(value):
                m = self._TIMEDELTA_PATTERN.match(value, start)
                if not m:
                    raise Exception()
                num = float(m.group(1))
```
