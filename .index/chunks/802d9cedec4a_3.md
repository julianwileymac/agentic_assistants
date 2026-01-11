# Chunk: 802d9cedec4a_3

- source: `.venv-lab/Lib/site-packages/babel/util.py`
- lines: 258-297
- chunk: 4/4

```
s east from UTC."""

    def __init__(self, offset: float, name: str | None = None) -> None:

        self._offset = datetime.timedelta(minutes=offset)
        if name is None:
            name = 'Etc/GMT%+d' % offset
        self.zone = name

    def __str__(self) -> str:
        return self.zone

    def __repr__(self) -> str:
        return f'<FixedOffset "{self.zone}" {self._offset}>'

    def utcoffset(self, dt: datetime.datetime) -> datetime.timedelta:
        return self._offset

    def tzname(self, dt: datetime.datetime) -> str:
        return self.zone

    def dst(self, dt: datetime.datetime) -> datetime.timedelta:
        return ZERO


# Export the localtime functionality here because that's
# where it was in the past.
# TODO(3.0): remove these aliases
UTC = dates.UTC
LOCALTZ = dates.LOCALTZ
get_localzone = localtime.get_localzone
STDOFFSET = localtime.STDOFFSET
DSTOFFSET = localtime.DSTOFFSET
DSTDIFF = localtime.DSTDIFF
ZERO = localtime.ZERO


def _cmp(a: Any, b: Any):
    return (a > b) - (a < b)
```
