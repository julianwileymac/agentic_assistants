# Chunk: 2bc0838bccfa_5

- source: `.venv-lab/Lib/site-packages/babel/units.py`
- lines: 333-341
- chunk: 6/6

```
=locale,
            numbering_system=numbering_system,
        )

    # TODO: this doesn't support "compound_variations" (or "prefix"), and will fall back to the "x/y" representation
    per_pattern = locale._data["compound_unit_patterns"].get("per", {}).get(length, {}).get("compound", "{0}/{1}")

    return per_pattern.format(formatted_numerator, formatted_denominator)
```
