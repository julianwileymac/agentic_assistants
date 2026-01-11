# Chunk: 7f4eab938bae_1

- source: `.venv-lab/Lib/site-packages/tinycss2/nth.py`
- lines: 75-101
- chunk: 2/2

```
 parse_b(tokens, a):
    token = _next_significant(tokens)
    if token is None:
        return (a, 0)
    elif token == '+':
        return parse_signless_b(tokens, a, 1)
    elif token == '-':
        return parse_signless_b(tokens, a, -1)
    elif (token.type == 'number' and token.is_integer and
          token.representation[0] in '-+'):
        return parse_end(tokens, a, token.int_value)


def parse_signless_b(tokens, a, b_sign):
    token = _next_significant(tokens)
    if (token.type == 'number' and token.is_integer and
            token.representation[0] not in '-+'):
        return parse_end(tokens, a, b_sign * token.int_value)


def parse_end(tokens, a, b):
    if _next_significant(tokens) is None:
        return (a, b)


N_DASH_DIGITS_RE = re.compile('^n(-[0-9]+)$')
```
