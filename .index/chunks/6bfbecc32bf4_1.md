# Chunk: 6bfbecc32bf4_1

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/output/vt100.py`
- lines: 105-203
- chunk: 2/9

```
O_RGB) == set(ANSI_COLOR_NAMES)


def _get_closest_ansi_color(r: int, g: int, b: int, exclude: Sequence[str] = ()) -> str:
    """
    Find closest ANSI color. Return it by name.

    :param r: Red (Between 0 and 255.)
    :param g: Green (Between 0 and 255.)
    :param b: Blue (Between 0 and 255.)
    :param exclude: A tuple of color names to exclude. (E.g. ``('ansired', )``.)
    """
    exclude = list(exclude)

    # When we have a bit of saturation, avoid the gray-like colors, otherwise,
    # too often the distance to the gray color is less.
    saturation = abs(r - g) + abs(g - b) + abs(b - r)  # Between 0..510

    if saturation > 30:
        exclude.extend(["ansilightgray", "ansidarkgray", "ansiwhite", "ansiblack"])

    # Take the closest color.
    # (Thanks to Pygments for this part.)
    distance = 257 * 257 * 3  # "infinity" (>distance from #000000 to #ffffff)
    match = "ansidefault"

    for name, (r2, g2, b2) in ANSI_COLORS_TO_RGB.items():
        if name != "ansidefault" and name not in exclude:
            d = (r - r2) ** 2 + (g - g2) ** 2 + (b - b2) ** 2

            if d < distance:
                match = name
                distance = d

    return match


_ColorCodeAndName = Tuple[int, str]


class _16ColorCache:
    """
    Cache which maps (r, g, b) tuples to 16 ansi colors.

    :param bg: Cache for background colors, instead of foreground.
    """

    def __init__(self, bg: bool = False) -> None:
        self.bg = bg
        self._cache: dict[Hashable, _ColorCodeAndName] = {}

    def get_code(
        self, value: tuple[int, int, int], exclude: Sequence[str] = ()
    ) -> _ColorCodeAndName:
        """
        Return a (ansi_code, ansi_name) tuple. (E.g. ``(44, 'ansiblue')``.) for
        a given (r,g,b) value.
        """
        key: Hashable = (value, tuple(exclude))
        cache = self._cache

        if key not in cache:
            cache[key] = self._get(value, exclude)

        return cache[key]

    def _get(
        self, value: tuple[int, int, int], exclude: Sequence[str] = ()
    ) -> _ColorCodeAndName:
        r, g, b = value
        match = _get_closest_ansi_color(r, g, b, exclude=exclude)

        # Turn color name into code.
        if self.bg:
            code = BG_ANSI_COLORS[match]
        else:
            code = FG_ANSI_COLORS[match]

        return code, match


class _256ColorCache(Dict[Tuple[int, int, int], int]):
    """
    Cache which maps (r, g, b) tuples to 256 colors.
    """

    def __init__(self) -> None:
        # Build color table.
        colors: list[tuple[int, int, int]] = []

        # colors 0..15: 16 basic colors
        colors.append((0x00, 0x00, 0x00))  # 0
        colors.append((0xCD, 0x00, 0x00))  # 1
        colors.append((0x00, 0xCD, 0x00))  # 2
        colors.append((0xCD, 0xCD, 0x00))  # 3
        colors.append((0x00, 0x00, 0xEE))  # 4
        colors.append((0xCD, 0x00, 0xCD))  # 5
        colors.append((0x00, 0xCD, 0xCD))  # 6
```
