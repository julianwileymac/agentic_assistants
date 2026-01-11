# Chunk: dbc74eebf959_1

- source: `.venv-lab/Lib/site-packages/tinycss2/color4.py`
- lines: 79-144
- chunk: 2/7

```
rgb = hls_to_rgb(
                    coordinates[0] / 360,
                    coordinates[2] / 100,
                    coordinates[1] / 100,
                )
                return Color(space, rgb, self.alpha)
            elif self.space == 'hwb':
                white, black = coordinates[1:]
                if white + black >= 100:
                    rgb = (white / (white + black),) * 3
                else:
                    rgb = (
                        ((channel * (100 - white - black)) + white) / 100
                        for channel in hls_to_rgb(coordinates[0] / 360, 0.5, 1))
                return Color(space, rgb, self.alpha)
        elif space == 'xyz-d50':
            if self.space == 'lab':
                xyz = _lab_to_xyz(*coordinates, D50)
                return Color(space, xyz, self.alpha)
            elif self.space == 'lch':
                a = coordinates[1] * cos(radians(coordinates[2]))
                b = coordinates[1] * sin(radians(coordinates[2]))
                xyz = _lab_to_xyz(coordinates[0], a, b, D50)
                return Color(space, xyz, self.alpha)
        elif space == 'xyz-d65':
            if self.space == 'oklab':
                xyz = _oklab_to_xyz(*coordinates)
                return Color(space, xyz, self.alpha)
            elif self.space == 'oklch':
                a = coordinates[1] * cos(radians(coordinates[2]))
                b = coordinates[1] * sin(radians(coordinates[2]))
                xyz = _oklab_to_xyz(coordinates[0], a, b)
                return Color(space, xyz, self.alpha)
        elif space == 'lab':
            if self.space == 'xyz-d50':
                lab = _xyz_to_lab(*coordinates, D50)
                return Color(space, lab, self.alpha)
            elif self.space == 'xyz-d65':
                lab = _xyz_to_lab(*coordinates, D65)
                return Color(space, lab, self.alpha)
            elif self.space == 'lch':
                a = coordinates[1] * cos(radians(coordinates[2]))
                b = coordinates[1] * sin(radians(coordinates[2]))
                return Color(space, (coordinates[0], a, b), self.alpha)
            elif self.space == 'oklab':
                xyz = _oklab_to_xyz(*coordinates)
                lab = _xyz_to_lab(*xyz, D65)
                return Color(space, lab, self.alpha)
            elif self.space == 'oklch':
                a = coordinates[1] * cos(radians(coordinates[2]))
                b = coordinates[1] * sin(radians(coordinates[2]))
                xyz = _oklab_to_xyz(coordinates[0], a, b)
                lab = _xyz_to_lab(*xyz, D65)
                return Color(space, lab, self.alpha)
        raise NotImplementedError


def parse_color(input):
    """Parse a color value as defined in CSS Color Level 4.

    https://www.w3.org/TR/css-color-4/

    :type input: :obj:`str` or :term:`iterable`
    :param input: A string or an iterable of :term:`component values`.
    :returns:
```
