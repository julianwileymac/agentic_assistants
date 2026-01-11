# Chunk: dbc74eebf959_4

- source: `.venv-lab/Lib/site-packages/tinycss2/color4.py`
- lines: 290-382
- chunk: 5/7

```
 :class:`Color`. Otherwise, return None.

    L range is [0, 100]. a, b ranges are [-125, 125].

    """
    if not _types(args) <= {'number', 'percentage'}:
        return
    coordinates = [
        None if args[0].type == 'ident' else args[0].value,
        None if args[1].type == 'ident' else (
            args[1].value * (1 if args[1].type == 'number' else 1.25)),
        None if args[2].type == 'ident' else (
            args[2].value * (1 if args[2].type == 'number' else 1.25)),
    ]
    return Color('lab', coordinates, alpha)


def _parse_lch(args, alpha):
    """Parse a list of CIE LCH channels.

    If args is a list of 2 NUMBER or PERCENTAGE tokens and 1 NUMBER or ANGLE
    token, return LCH :class:`Color`. Otherwise, return None.

    L range is [0, 100]. C range is [0, 150]. H ranges is [0, 360).

    """
    if not _types(args[:2]) <= {'number', 'percentage'}:
        return
    if (hue := _parse_hue(args[2])) is None:
        return
    coordinates = [
        None if args[0].type == 'ident' else args[0].value,
        None if args[1].type == 'ident' else (
            args[1].value * (1 if args[1].type == 'number' else 1.5)),
        None if args[0].type == 'ident' else hue,
    ]
    return Color('lch', coordinates, alpha)


def _parse_oklab(args, alpha):
    """Parse a list of Oklab channels.

    If args is a list of 3 NUMBER or PERCENTAGE tokens, return Oklab
    :class:`Color`. Otherwise, return None.

    L range is [0, 100]. a, b ranges are [-0.4, 0.4].

    """
    if not _types(args) <= {'number', 'percentage'}:
        return
    coordinates = [
        None if args[0].type == 'ident' else (
            args[0].value * (1 if args[0].type == 'number' else 0.01)),
        None if args[1].type == 'ident' else (
            args[1].value * (1 if args[1].type == 'number' else 0.004)),
        None if args[2].type == 'ident' else (
            args[2].value * (1 if args[2].type == 'number' else 0.004)),
    ]
    return Color('oklab', coordinates, alpha)


def _parse_oklch(args, alpha):
    """Parse a list of Oklch channels.

    If args is a list of 2 NUMBER or PERCENTAGE tokens and 1 NUMBER or ANGLE
    token, return Oklch :class:`Color`. Otherwise, return None.

    L range is [0, 1]. C range is [0, 0.4]. H range is [0, 360).

    """
    if not _types(args[:2]) <= {'number', 'percentage'}:
        return
    if (hue := _parse_hue(args[2])) is None:
        return
    coordinates = [
        None if args[0].type == 'ident' else (
            args[0].value * (1 if args[0].type == 'number' else 0.01)),
        None if args[1].type == 'ident' else (
            args[1].value * (1 if args[1].type == 'number' else 0.004)),
        None if args[0].type == 'ident' else hue,
    ]
    return Color('oklch', coordinates, alpha)


def _parse_color(space, args, alpha):
    """Parse a color space name list of coordinates.

    Ranges are [0, 1].

    """
    if not _types(args) <= {'number', 'percentage'}:
        return
```
