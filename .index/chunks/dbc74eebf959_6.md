# Chunk: dbc74eebf959_6

- source: `.venv-lab/Lib/site-packages/tinycss2/color4.py`
- lines: 456-475
- chunk: 7/7

```
116) ** 3 if L > _κ * _ε else L / _κ)
    z = (f2 ** 3 if f2 ** 3 > _ε else (116 * f2 - 16) / _κ)
    X = x * d[0]
    Y = y * d[1]
    Z = z * d[2]
    return X, Y, Z


def _oklab_to_xyz(L, a, b):
    lab = (L, a, b)
    lms = [sum(_OKLAB_TO_LMS[i][j] * lab[j] for j in range(3)) for i in range(3)]
    X, Y, Z = [sum(_LMS_TO_XYZ[i][j] * lms[j]**3 for j in range(3)) for i in range(3)]
    return X, Y, Z


# (r, g, b) in 0..255
_EXTENDED_COLOR_KEYWORDS = _EXTENDED_COLOR_KEYWORDS.copy()
_EXTENDED_COLOR_KEYWORDS.append(('rebeccapurple', (102, 51, 153)))
_COLOR_KEYWORDS = dict(_BASIC_COLOR_KEYWORDS + _EXTENDED_COLOR_KEYWORDS)
```
