# Chunk: dbc74eebf959_2

- source: `.venv-lab/Lib/site-packages/tinycss2/color4.py`
- lines: 132-213
- chunk: 3/7

```
lpha)
        raise NotImplementedError


def parse_color(input):
    """Parse a color value as defined in CSS Color Level 4.

    https://www.w3.org/TR/css-color-4/

    :type input: :obj:`str` or :term:`iterable`
    :param input: A string or an iterable of :term:`component values`.
    :returns:
        * :obj:`None` if the input is not a valid color value.
          (No exception is raised.)
        * The string ``'currentcolor'`` for the ``currentcolor`` keyword
        * A :class:`Color` object for every other values, including keywords.

    """
    if isinstance(input, str):
        token = parse_one_component_value(input, skip_comments=True)
    else:
        token = input
    if token.type == 'ident':
        if token.lower_value == 'currentcolor':
            return 'currentcolor'
        elif token.lower_value == 'transparent':
            return Color('srgb', (0, 0, 0), 0)
        elif color := _COLOR_KEYWORDS.get(token.lower_value):
            rgb = tuple(channel / 255 for channel in color)
            return Color('srgb', rgb, 1)
    elif token.type == 'hash':
        for multiplier, regexp in _HASH_REGEXPS:
            match = regexp(token.value)
            if match:
                channels = [
                    int(group * multiplier, 16) / 255
                    for group in match.groups()]
                alpha = channels.pop() if len(channels) == 4 else 1
                return Color('srgb', channels, alpha)
    elif token.type == 'function':
        tokens = [
            token for token in token.arguments
            if token.type not in ('whitespace', 'comment')]
        name = token.lower_name
        if name == 'color':
            space, *tokens = tokens
        length = len(tokens)
        if length in (5, 7) and all(token == ',' for token in tokens[1::2]):
            old_syntax = True
            tokens = tokens[::2]
        elif length == 3:
            old_syntax = False
        elif length == 5 and tokens[3] == '/':
            tokens.pop(3)
            old_syntax = False
        else:
            return
        args, alpha = tokens[:3], _parse_alpha(tokens[3:])
        if alpha is None:
            return
        if name in ('rgb', 'rgba'):
            return _parse_rgb(args, alpha)
        elif name in ('hsl', 'hsla'):
            return _parse_hsl(args, alpha)
        elif name == 'hwb':
            return _parse_hwb(args, alpha)
        elif name == 'lab' and not old_syntax:
            return _parse_lab(args, alpha)
        elif name == 'lch' and not old_syntax:
            return _parse_lch(args, alpha)
        elif name == 'oklab' and not old_syntax:
            return _parse_oklab(args, alpha)
        elif name == 'oklch' and not old_syntax:
            return _parse_oklch(args, alpha)
        elif name == 'color' and not old_syntax:
            return _parse_color(space, args, alpha)


def _parse_alpha(args):
    """Parse a list of one alpha value.
```
