# Chunk: 2bc0838bccfa_4

- source: `.venv-lab/Lib/site-packages/babel/units.py`
- lines: 267-340
- chunk: 5/6

```
l use the default numbering system of the locale.
    :return: A formatted compound value.
    :raise `UnsupportedNumberingSystemError`: If the numbering system is not supported by the locale.
    """
    locale = Locale.parse(locale or LC_NUMERIC)

    # Look for a specific compound unit first...

    if numerator_unit and denominator_unit and denominator_value == 1:
        compound_unit = _find_compound_unit(numerator_unit, denominator_unit, locale=locale)
        if compound_unit:
            return format_unit(
                numerator_value,
                compound_unit,
                length=length,
                format=format,
                locale=locale,
                numbering_system=numbering_system,
            )

    # ... failing that, construct one "by hand".

    if isinstance(numerator_value, str):  # Numerator is preformatted
        formatted_numerator = numerator_value
    elif numerator_unit:  # Numerator has unit
        formatted_numerator = format_unit(
            numerator_value,
            numerator_unit,
            length=length,
            format=format,
            locale=locale,
            numbering_system=numbering_system,
        )
    else:  # Unitless numerator
        formatted_numerator = format_decimal(
            numerator_value,
            format=format,
            locale=locale,
            numbering_system=numbering_system,
        )

    if isinstance(denominator_value, str):  # Denominator is preformatted
        formatted_denominator = denominator_value
    elif denominator_unit:  # Denominator has unit
        if denominator_value == 1:  # support perUnitPatterns when the denominator is 1
            denominator_unit = _find_unit_pattern(denominator_unit, locale=locale)
            per_pattern = locale._data["unit_patterns"].get(denominator_unit, {}).get(length, {}).get("per")
            if per_pattern:
                return per_pattern.format(formatted_numerator)
            # See TR-35's per-unit pattern algorithm, point 3.2.
            # For denominator 1, we replace the value to be formatted with the empty string;
            # this will make `format_unit` return " second" instead of "1 second".
            denominator_value = ""

        formatted_denominator = format_unit(
            denominator_value,
            measurement_unit=(denominator_unit or ""),
            length=length,
            format=format,
            locale=locale,
            numbering_system=numbering_system,
        ).strip()
    else:  # Bare denominator
        formatted_denominator = format_decimal(
            denominator_value,
            format=format,
            locale=locale,
            numbering_system=numbering_system,
        )

    # TODO: this doesn't support "compound_variations" (or "prefix"), and will fall back to the "x/y" representation
    per_pattern = locale._data["compound_unit_patterns"].get("per", {}).get(length, {}).get("compound", "{0}/{1}")
```
