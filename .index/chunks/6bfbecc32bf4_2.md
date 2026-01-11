# Chunk: 6bfbecc32bf4_2

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/output/vt100.py`
- lines: 196-293
- chunk: 3/9

```
0x00, 0x00))  # 0
        colors.append((0xCD, 0x00, 0x00))  # 1
        colors.append((0x00, 0xCD, 0x00))  # 2
        colors.append((0xCD, 0xCD, 0x00))  # 3
        colors.append((0x00, 0x00, 0xEE))  # 4
        colors.append((0xCD, 0x00, 0xCD))  # 5
        colors.append((0x00, 0xCD, 0xCD))  # 6
        colors.append((0xE5, 0xE5, 0xE5))  # 7
        colors.append((0x7F, 0x7F, 0x7F))  # 8
        colors.append((0xFF, 0x00, 0x00))  # 9
        colors.append((0x00, 0xFF, 0x00))  # 10
        colors.append((0xFF, 0xFF, 0x00))  # 11
        colors.append((0x5C, 0x5C, 0xFF))  # 12
        colors.append((0xFF, 0x00, 0xFF))  # 13
        colors.append((0x00, 0xFF, 0xFF))  # 14
        colors.append((0xFF, 0xFF, 0xFF))  # 15

        # colors 16..232: the 6x6x6 color cube
        valuerange = (0x00, 0x5F, 0x87, 0xAF, 0xD7, 0xFF)

        for i in range(217):
            r = valuerange[(i // 36) % 6]
            g = valuerange[(i // 6) % 6]
            b = valuerange[i % 6]
            colors.append((r, g, b))

        # colors 233..253: grayscale
        for i in range(1, 22):
            v = 8 + i * 10
            colors.append((v, v, v))

        self.colors = colors

    def __missing__(self, value: tuple[int, int, int]) -> int:
        r, g, b = value

        # Find closest color.
        # (Thanks to Pygments for this!)
        distance = 257 * 257 * 3  # "infinity" (>distance from #000000 to #ffffff)
        match = 0

        for i, (r2, g2, b2) in enumerate(self.colors):
            if i >= 16:  # XXX: We ignore the 16 ANSI colors when mapping RGB
                # to the 256 colors, because these highly depend on
                # the color scheme of the terminal.
                d = (r - r2) ** 2 + (g - g2) ** 2 + (b - b2) ** 2

                if d < distance:
                    match = i
                    distance = d

        # Turn color name into code.
        self[value] = match
        return match


_16_fg_colors = _16ColorCache(bg=False)
_16_bg_colors = _16ColorCache(bg=True)
_256_colors = _256ColorCache()


class _EscapeCodeCache(Dict[Attrs, str]):
    """
    Cache for VT100 escape codes. It maps
    (fgcolor, bgcolor, bold, underline, strike, italic, blink, reverse, hidden, dim) tuples to VT100
    escape sequences.

    :param true_color: When True, use 24bit colors instead of 256 colors.
    """

    def __init__(self, color_depth: ColorDepth) -> None:
        self.color_depth = color_depth

    def __missing__(self, attrs: Attrs) -> str:
        (
            fgcolor,
            bgcolor,
            bold,
            underline,
            strike,
            italic,
            blink,
            reverse,
            hidden,
            dim,
        ) = attrs
        parts: list[str] = []

        parts.extend(self._colors_to_code(fgcolor or "", bgcolor or ""))

        if bold:
            parts.append("1")
        if dim:
            parts.append("2")
        if italic:
            parts.append("3")
        if blink:
```
