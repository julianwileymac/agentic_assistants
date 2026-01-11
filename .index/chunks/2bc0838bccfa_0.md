# Chunk: 2bc0838bccfa_0

- source: `.venv-lab/Lib/site-packages/babel/units.py`
- lines: 1-92
- chunk: 1/6

```
from __future__ import annotations

import decimal
from typing import Literal

from babel.core import Locale
from babel.numbers import LC_NUMERIC, format_decimal


class UnknownUnitError(ValueError):
    def __init__(self, unit: str, locale: Locale) -> None:
        ValueError.__init__(self, f"{unit} is not a known unit in {locale}")


def get_unit_name(
    measurement_unit: str,
    length: Literal['short', 'long', 'narrow'] = 'long',
    locale: Locale | str | None = None,
) -> str | None:
    """
    Get the display name for a measurement unit in the given locale.

    >>> get_unit_name("radian", locale="en")
    'radians'

    Unknown units will raise exceptions:

    >>> get_unit_name("battery", locale="fi")
    Traceback (most recent call last):
        ...
    UnknownUnitError: battery/long is not a known unit/length in fi

    :param measurement_unit: the code of a measurement unit.
                             Known units can be found in the CLDR Unit Validity XML file:
                             https://unicode.org/repos/cldr/tags/latest/common/validity/unit.xml

    :param length: "short", "long" or "narrow"
    :param locale: the `Locale` object or locale identifier. Defaults to the system numeric locale.
    :return: The unit display name, or None.
    """
    locale = Locale.parse(locale or LC_NUMERIC)
    unit = _find_unit_pattern(measurement_unit, locale=locale)
    if not unit:
        raise UnknownUnitError(unit=measurement_unit, locale=locale)
    return locale.unit_display_names.get(unit, {}).get(length)


def _find_unit_pattern(unit_id: str, locale: Locale | str | None = None) -> str | None:
    """
    Expand a unit into a qualified form.

    Known units can be found in the CLDR Unit Validity XML file:
    https://unicode.org/repos/cldr/tags/latest/common/validity/unit.xml

    >>> _find_unit_pattern("radian", locale="en")
    'angle-radian'

    Unknown values will return None.

    >>> _find_unit_pattern("horse", locale="en")

    :param unit_id: the code of a measurement unit.
    :return: A key to the `unit_patterns` mapping, or None.
    """
    locale = Locale.parse(locale or LC_NUMERIC)
    unit_patterns: dict[str, str] = locale._data["unit_patterns"]
    if unit_id in unit_patterns:
        return unit_id
    for unit_pattern in sorted(unit_patterns, key=len):
        if unit_pattern.endswith(unit_id):
            return unit_pattern
    return None


def format_unit(
    value: str | float | decimal.Decimal,
    measurement_unit: str,
    length: Literal['short', 'long', 'narrow'] = 'long',
    format: str | None = None,
    locale: Locale | str | None = None,
    *,
    numbering_system: Literal["default"] | str = "latn",
) -> str:
    """Format a value of a given unit.

    Values are formatted according to the locale's usual pluralization rules
    and number formats.

    >>> format_unit(12, 'length-meter', locale='ro_RO')
    u'12 metri'
    >>> format_unit(15.5, 'length-mile', locale='fi_FI')
```
