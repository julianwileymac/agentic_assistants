# Chunk: dbc74eebf959_5

- source: `.venv-lab/Lib/site-packages/tinycss2/color4.py`
- lines: 368-467
- chunk: 6/7

```
)),
        None if args[0].type == 'ident' else hue,
    ]
    return Color('oklch', coordinates, alpha)


def _parse_color(space, args, alpha):
    """Parse a color space name list of coordinates.

    Ranges are [0, 1].

    """
    if not _types(args) <= {'number', 'percentage'}:
        return
    if space.type != 'ident' or (space := space.lower_value) not in _FUNCTION_SPACES:
        return
    if space == 'xyz':
        space = 'xyz-d65'
    coordinates = [
        arg.value if arg.type == 'number' else
        arg.value / 100 if arg.type == 'percentage' else None
        for arg in args]
    return Color(space, coordinates, alpha)


def _parse_hue(token):
    """Parse hue token.

    Range is [0, 360). ``none`` value is 0.

    """
    if token.type == 'number':
        return token.value % 360
    elif token.type == 'dimension':
        if token.unit == 'deg':
            return token.value % 360
        elif token.unit == 'grad':
            return token.value / 400 * 360 % 360
        elif token.unit == 'rad':
            return degrees(token.value) % 360
        elif token.unit == 'turn':
            return token.value * 360 % 360
    elif token.type == 'ident' and token.lower_value == 'none':
        return 0


def _types(tokens):
    """Get a set of token types, ignoring ``none`` values."""
    types = set()
    for token in tokens:
        if token.type == 'ident' and token.lower_value == 'none':
            continue
        types.add(token.type)
    return types


# Code adapted from https://www.w3.org/TR/css-color-4/#color-conversion-code.
_κ = 24389 / 27
_ε = 216 / 24389
_LMS_TO_XYZ = (
    (1.2268798733741557, -0.5578149965554813, 0.28139105017721583),
    (-0.04057576262431372, 1.1122868293970594, -0.07171106666151701),
    (-0.07637294974672142, -0.4214933239627914, 1.5869240244272418),
)
_OKLAB_TO_LMS = (
    (0.99999999845051981432, 0.39633779217376785678, 0.21580375806075880339),
    (1.0000000088817607767, -0.1055613423236563494, -0.063854174771705903402),
    (1.0000000546724109177, -0.089484182094965759684, -1.2914855378640917399),
)

def _xyz_to_lab(X, Y, Z, d):
    x = X / d[0]
    y = Y / d[1]
    z = Z / d[2]
    f0 = x ** (1 / 3) if x > _ε else (_κ * x + 16) / 116
    f1 = y ** (1 / 3) if y > _ε else (_κ * y + 16) / 116
    f2 = z ** (1 / 3) if z > _ε else (_κ * z + 16) / 116
    L = (116 * f1) - 16
    a = 500 * (f0 - f1)
    b = 200 * (f1 - f2)
    return L, a, b


def _lab_to_xyz(L, a, b, d):
    f1 = (L + 16) / 116
    f0 = a / 500 + f1
    f2 = f1 - b / 200
    x = (f0 ** 3 if f0 ** 3 > _ε else (116 * f0 - 16) / _κ)
    y = (((L + 16) / 116) ** 3 if L > _κ * _ε else L / _κ)
    z = (f2 ** 3 if f2 ** 3 > _ε else (116 * f2 - 16) / _κ)
    X = x * d[0]
    Y = y * d[1]
    Z = z * d[2]
    return X, Y, Z


def _oklab_to_xyz(L, a, b):
    lab = (L, a, b)
    lms = [sum(_OKLAB_TO_LMS[i][j] * lab[j] for j in range(3)) for i in range(3)]
```
