# Chunk: 2bc0838bccfa_2

- source: `.venv-lab/Lib/site-packages/babel/units.py`
- lines: 146-220
- chunk: 3/6

```
      formatted_value = format_decimal(value, format, locale, numbering_system=numbering_system)
        plural_form = locale.plural_form(value)

    if plural_form in unit_patterns:
        return unit_patterns[plural_form].format(formatted_value)

    # Fall back to a somewhat bad representation.
    # nb: This is marked as no-cover, as the current CLDR seemingly has no way for this to happen.
    fallback_name = get_unit_name(measurement_unit, length=length, locale=locale)  # pragma: no cover
    return f"{formatted_value} {fallback_name or measurement_unit}"  # pragma: no cover


def _find_compound_unit(
    numerator_unit: str,
    denominator_unit: str,
    locale: Locale | str | None = None,
) -> str | None:
    """
    Find a predefined compound unit pattern.

    Used internally by format_compound_unit.

    >>> _find_compound_unit("kilometer", "hour", locale="en")
    'speed-kilometer-per-hour'

    >>> _find_compound_unit("mile", "gallon", locale="en")
    'consumption-mile-per-gallon'

    If no predefined compound pattern can be found, `None` is returned.

    >>> _find_compound_unit("gallon", "mile", locale="en")

    >>> _find_compound_unit("horse", "purple", locale="en")

    :param numerator_unit: The numerator unit's identifier
    :param denominator_unit: The denominator unit's identifier
    :param locale: the `Locale` object or locale identifier. Defaults to the system numeric locale.
    :return: A key to the `unit_patterns` mapping, or None.
    :rtype: str|None
    """
    locale = Locale.parse(locale or LC_NUMERIC)

    # Qualify the numerator and denominator units.  This will turn possibly partial
    # units like "kilometer" or "hour" into actual units like "length-kilometer" and
    # "duration-hour".

    resolved_numerator_unit = _find_unit_pattern(numerator_unit, locale=locale)
    resolved_denominator_unit = _find_unit_pattern(denominator_unit, locale=locale)

    # If either was not found, we can't possibly build a suitable compound unit either.
    if not (resolved_numerator_unit and resolved_denominator_unit):
        return None

    # Since compound units are named "speed-kilometer-per-hour", we'll have to slice off
    # the quantities (i.e. "length", "duration") from both qualified units.

    bare_numerator_unit = resolved_numerator_unit.split("-", 1)[-1]
    bare_denominator_unit = resolved_denominator_unit.split("-", 1)[-1]

    # Now we can try and rebuild a compound unit specifier, then qualify it:

    return _find_unit_pattern(f"{bare_numerator_unit}-per-{bare_denominator_unit}", locale=locale)


def format_compound_unit(
    numerator_value: str | float | decimal.Decimal,
    numerator_unit: str | None = None,
    denominator_value: str | float | decimal.Decimal = 1,
    denominator_unit: str | None = None,
    length: Literal["short", "long", "narrow"] = "long",
    format: str | None = None,
    locale: Locale | str | None = None,
    *,
    numbering_system: Literal["default"] | str = "latn",
```
