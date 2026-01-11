# Chunk: fba73ec6e54a_2

- source: `.venv-lab/Lib/site-packages/prometheus_client/parser.py`
- lines: 164-259
- chunk: 3/5

```
pace
    while i > 0:
        if text[i] == '"' and not _is_character_escaped(text, i):
            in_quotes = not in_quotes
            
        if not in_quotes:
            if text[i] in chs:
                return i
        i -= 1
    return -1


def _split_quoted(text, separator, maxsplit=0):
    """Splits on split_ch similarly to strings.split, skipping separators if
    they are inside quotes.
    """

    tokens = ['']
    x = 0
    while x < len(text):
        split_pos = _next_unquoted_char(text, separator, x)
        if split_pos == -1:
            tokens[-1] = text[x:]
            x = len(text)
            continue
        # If the first character is the separator keep going. This happens when
        # there are double whitespace characters separating symbols.
        if split_pos == x:
            x += 1
            continue

        if maxsplit > 0 and len(tokens) > maxsplit:
            tokens[-1] = text[x:]
            break
        tokens[-1] = text[x:split_pos]
        x = split_pos + 1
        tokens.append('')
    return tokens


def _unquote_unescape(text):
    """Returns the string, and true if it was quoted."""
    if not text:
        return text, False
    quoted = False
    text = text.strip()
    if text[0] == '"':
        if len(text) == 1 or text[-1] != '"':
            raise ValueError("missing close quote")
        text = text[1:-1]
        quoted = True
    if "\\" in text:
        text = _replace_escaping(text)
    return text, quoted


# If we have multiple values only consider the first
def _parse_value_and_timestamp(s: str) -> Tuple[float, Optional[float]]:
    s = s.lstrip()
    separator = " "
    if separator not in s:
        separator = "\t"
    values = [value.strip() for value in s.split(separator) if value.strip()]
    if not values:
        return float(s), None
    value = _parse_value(values[0])
    timestamp = (_parse_value(values[-1]) / 1000) if len(values) > 1 else None
    return value, timestamp


def _parse_value(value):
    value = ''.join(value)
    if value != value.strip() or '_' in value:
        raise ValueError(f"Invalid value: {value!r}")
    try:
        return int(value)
    except ValueError:
        return float(value)
    

def _parse_sample(text):
    separator = " # "
    # Detect the labels in the text
    label_start = _next_unquoted_char(text, '{')
    if label_start == -1 or separator in text[:label_start]:
        # We don't have labels, but there could be an exemplar.
        name_end = _next_unquoted_char(text, ' \t')
        name = text[:name_end].strip()
        if not _is_valid_legacy_metric_name(name):
            raise ValueError("invalid metric name:" + text)
        # Parse the remaining text after the name
        remaining_text = text[name_end + 1:]
        value, timestamp = _parse_value_and_timestamp(remaining_text)
        return Sample(name, {}, value, timestamp)
    name = text[:label_start].strip()
```
