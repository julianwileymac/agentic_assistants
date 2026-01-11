# Chunk: 1bfb27fbc0ca_2

- source: `.venv-lab/Lib/site-packages/pip/_vendor/rich/highlighter.py`
- lines: 156-197
- chunk: 3/4

```
[01]|0[1-9]|[12][0-9]))$",
        # Ordinal date (e.g. 2008-243). The hyphen is optional
        r"^(?P<date>(?P<year>[0-9]{4})-?(?P<day>36[0-6]|3[0-5][0-9]|[12][0-9]{2}|0[1-9][0-9]|00[1-9]))$",
        #
        # Weeks
        #
        # Week of the year (e.g., 2008-W35). The hyphen is optional
        r"^(?P<date>(?P<year>[0-9]{4})-?W(?P<week>5[0-3]|[1-4][0-9]|0[1-9]))$",
        # Week date (e.g., 2008-W35-6). The hyphens are optional
        r"^(?P<date>(?P<year>[0-9]{4})-?W(?P<week>5[0-3]|[1-4][0-9]|0[1-9])-?(?P<day>[1-7]))$",
        #
        # Times
        #
        # Hours and minutes (e.g., 17:21). The colon is optional
        r"^(?P<time>(?P<hour>2[0-3]|[01][0-9]):?(?P<minute>[0-5][0-9]))$",
        # Hours, minutes, and seconds w/o colons (e.g., 172159)
        r"^(?P<time>(?P<hour>2[0-3]|[01][0-9])(?P<minute>[0-5][0-9])(?P<second>[0-5][0-9]))$",
        # Time zone designator (e.g., Z, +07 or +07:00). The colons and the minutes are optional
        r"^(?P<timezone>(Z|[+-](?:2[0-3]|[01][0-9])(?::?(?:[0-5][0-9]))?))$",
        # Hours, minutes, and seconds with time zone designator (e.g., 17:21:59+07:00).
        # All the colons are optional. The minutes in the time zone designator are also optional
        r"^(?P<time>(?P<hour>2[0-3]|[01][0-9])(?P<minute>[0-5][0-9])(?P<second>[0-5][0-9]))(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9])(?::?(?:[0-5][0-9]))?)$",
        #
        # Date and Time
        #
        # Calendar date with hours, minutes, and seconds (e.g., 2008-08-30 17:21:59 or 20080830 172159).
        # A space is required between the date and the time. The hyphens and colons are optional.
        # This regex matches dates and times that specify some hyphens or colons but omit others.
        # This does not follow ISO 8601
        r"^(?P<date>(?P<year>[0-9]{4})(?P<hyphen>-)?(?P<month>1[0-2]|0[1-9])(?(hyphen)-)(?P<day>3[01]|0[1-9]|[12][0-9])) (?P<time>(?P<hour>2[0-3]|[01][0-9])(?(hyphen):)(?P<minute>[0-5][0-9])(?(hyphen):)(?P<second>[0-5][0-9]))$",
        #
        # XML Schema dates and times
        #
        # Date, with optional time zone (e.g., 2008-08-30 or 2008-08-30+07:00).
        # Hyphens are required. This is the XML Schema 'date' type
        r"^(?P<date>(?P<year>-?(?:[1-9][0-9]*)?[0-9]{4})-(?P<month>1[0-2]|0[1-9])-(?P<day>3[01]|0[1-9]|[12][0-9]))(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$",
        # Time, with optional fractional seconds and time zone (e.g., 01:45:36 or 01:45:36.123+07:00).
        # There is no limit on the number of digits for the fractional seconds. This is the XML Schema 'time' type
        r"^(?P<time>(?P<hour>2[0-3]|[01][0-9]):(?P<minute>[0-5][0-9]):(?P<second>[0-5][0-9])(?P<frac>\.[0-9]+)?)(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$",
        # Date and time, with optional fractional seconds and time zone (e.g., 2008-08-30T01:45:36 or 2008-08-30T01:45:36.123Z).
        # This is the XML Schema 'dateTime' type
```
