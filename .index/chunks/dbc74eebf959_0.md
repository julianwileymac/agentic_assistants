# Chunk: dbc74eebf959_0

- source: `.venv-lab/Lib/site-packages/tinycss2/color4.py`
- lines: 1-87
- chunk: 1/7

```
from colorsys import hls_to_rgb
from math import cos, degrees, radians, sin

from .color3 import _BASIC_COLOR_KEYWORDS, _EXTENDED_COLOR_KEYWORDS, _HASH_REGEXPS
from .parser import parse_one_component_value

D50 = (0.3457 / 0.3585, 1, (1 - 0.3457 - 0.3585) / 0.3585)
D65 = (0.3127 / 0.3290, 1, (1 - 0.3127 - 0.3290) / 0.3290)
_FUNCTION_SPACES = {
    'srgb', 'srgb-linear',
    'display-p3', 'a98-rgb', 'prophoto-rgb', 'rec2020',
    'xyz', 'xyz-d50', 'xyz-d65'
}
COLOR_SPACES = _FUNCTION_SPACES | {'hsl', 'hwb', 'lab', 'lch', 'oklab', 'oklch'}


class Color:
    """A specified color in a defined color space.

    The color space is one of ``COLOR_SPACES``.

    Coordinates are floats with undefined ranges, but alpha channel is clipped
    to [0, 1]. Coordinates can also be set to ``None`` when undefined.

    """
    def __init__(self, space, coordinates, alpha):
        assert space in COLOR_SPACES, f"{space} is not a supported color space"
        self.space = space
        self.coordinates = tuple(
            None if coordinate is None else float(coordinate)
            for coordinate in coordinates)
        self.alpha = max(0., min(1., float(alpha)))

    def __repr__(self):
        coordinates = ' '.join(str(coordinate) for coordinate in self.coordinates)
        return f'color({self.space} {coordinates} / {self.alpha})'

    def __iter__(self):
        yield from self.coordinates
        yield self.alpha

    def __getitem__(self, key):
        return (*self.coordinates, self.alpha)[key]

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, str):
            return False
        elif isinstance(other, tuple):
            return tuple(self) == other
        elif isinstance(other, Color):
            return self.space == other.space and self.coordinates == other.coordinates
        return super().__eq__(other)

    def to(self, space):
        """Return new instance with coordinates transformed to given ``space``.

        The destination color space is one of ``SPACES``.

        ``None`` coordinates are always transformed into ``0`` values.

        Here are the supported combinations:

        - from hsl and hwb to srgb;
        - from lab and lch to xyz-d50;
        - from oklab and oklch to xyz-d65;
        - from xyz-d50, xyz-d65, lch, oklab and oklch to lab.

        """
        coordinates = tuple(coordinate or 0 for coordinate in self.coordinates)
        if space == 'xyz':
            space = 'xyz-d65'
        if space == self.space:
            return Color(space, coordinates, self.alpha)
        elif space == 'srgb':
            if self.space == 'hsl':
                rgb = hls_to_rgb(
                    coordinates[0] / 360,
                    coordinates[2] / 100,
                    coordinates[1] / 100,
                )
                return Color(space, rgb, self.alpha)
            elif self.space == 'hwb':
                white, black = coordinates[1:]
```
