# Chunk: dbc74eebf959_3

- source: `.venv-lab/Lib/site-packages/tinycss2/color4.py`
- lines: 203-300
- chunk: 4/7

```
     return _parse_oklab(args, alpha)
        elif name == 'oklch' and not old_syntax:
            return _parse_oklch(args, alpha)
        elif name == 'color' and not old_syntax:
            return _parse_color(space, args, alpha)


def _parse_alpha(args):
    """Parse a list of one alpha value.

    If args is a list of a single INTEGER, NUMBER or PERCENTAGE token,
    return its value clipped to the 0..1 range. Otherwise, return None.

    """
    if len(args) == 0:
        return 1.
    elif len(args) == 1:
        if args[0].type == 'number':
            return min(1, max(0, args[0].value))
        elif args[0].type == 'percentage':
            return min(1, max(0, args[0].value / 100))


def _parse_rgb(args, alpha):
    """Parse a list of RGB channels.

    If args is a list of 3 NUMBER tokens or 3 PERCENTAGE tokens, return
    sRGB :class:`Color`. Otherwise, return None.

    Input R, G, B ranges are [0, 255], output are [0, 1].

    """
    if _types(args) not in (set(), {'number'}, {'percentage'}):
        return
    coordinates = [
        arg.value / 255 if arg.type == 'number' else
        arg.value / 100 if arg.type == 'percentage' else None
        for arg in args]
    return Color('srgb', coordinates, alpha)


def _parse_hsl(args, alpha):
    """Parse a list of HSL channels.

    If args is a list of 1 NUMBER or ANGLE token and 2 PERCENTAGE tokens,
    return HSL :class:`Color`. Otherwise, return None.

    H range is [0, 360). S, L ranges are [0, 100].

    """
    if _types(args[1:]) not in (set(), {'number'}, {'percentage'}):
        return
    if (hue := _parse_hue(args[0])) is None:
        return
    coordinates = [
        None if args[0].type == 'ident' else hue,
        None if args[1].type == 'ident' else args[1].value,
        None if args[2].type == 'ident' else args[2].value,
    ]
    return Color('hsl', coordinates, alpha)


def _parse_hwb(args, alpha):
    """Parse a list of HWB channels.

    If args is a list of 1 NUMBER or ANGLE token and 2 NUMBER or PERCENTAGE
    tokens, return HWB :class:`Color`. Otherwise, return None.

    H range is [0, 360). W, B ranges are [0, 100].

    """
    if not _types(args[1:]) <= {'number', 'percentage'}:
        return
    if (hue := _parse_hue(args[0])) is None:
        return
    coordinates = [
        None if args[0].type == 'ident' else hue,
        None if args[1].type == 'ident' else args[1].value,
        None if args[2].type == 'ident' else args[2].value,
    ]
    return Color('hwb', coordinates, alpha)


def _parse_lab(args, alpha):
    """Parse a list of CIE Lab channels.

    If args is a list of 3 NUMBER or PERCENTAGE tokens, return Lab
    :class:`Color`. Otherwise, return None.

    L range is [0, 100]. a, b ranges are [-125, 125].

    """
    if not _types(args) <= {'number', 'percentage'}:
        return
    coordinates = [
        None if args[0].type == 'ident' else args[0].value,
        None if args[1].type == 'ident' else (
```
