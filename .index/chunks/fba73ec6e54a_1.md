# Chunk: fba73ec6e54a_1

- source: `.venv-lab/Lib/site-packages/prometheus_client/parser.py`
- lines: 87-177
- chunk: 2/5

```
          i += 1
            # The label value is between the first and last quote
            quote_end = i + 1
            if quote_end != len(value_term):
                raise ValueError("unexpected text after quote: " + labels_string)

            label_value, _ = _unquote_unescape(value_term)
            if label_name == '__name__':
                _validate_metric_name(label_name)
            else:
                _validate_labelname(label_name)
            if label_name in labels:
                raise ValueError("invalid line, duplicate label name: " + labels_string)
            labels[label_name] = label_value
        return labels
    except ValueError:
        raise ValueError("Invalid labels: " + labels_string)
    

def _next_term(text: str, openmetrics: bool) -> Tuple[str, str, str]:
    """Extract the next comma-separated label term from the text. The results
    are stripped terms for the label name, label value, and then the remainder
    of the string including the final , or }.
    
    Raises ValueError if the term is empty and we're in openmetrics mode.
    """
    
    # There may be a leading comma, which is fine here.
    if text[0] == ',':
        text = text[1:]
        if not text:
            return "", "", ""
        if text[0] == ',':
            raise ValueError("multiple commas")

    splitpos = _next_unquoted_char(text, '=,}')
    if splitpos >= 0 and text[splitpos] == "=":
        labelname = text[:splitpos]
        text = text[splitpos + 1:]
        splitpos = _next_unquoted_char(text, ',}')
    else:
        labelname = "__name__"

    if splitpos == -1:
        splitpos = len(text)
    term = text[:splitpos]
    if not term and openmetrics:
        raise ValueError("empty term:", term)
    
    rest = text[splitpos:]
    return labelname, term.strip(), rest.strip()


def _next_unquoted_char(text: str, chs: Optional[str], startidx: int = 0) -> int:
    """Return position of next unquoted character in tuple, or -1 if not found.
    
    It is always assumed that the first character being checked is not already
    inside quotes.
    """
    in_quotes = False
    if chs is None:
        chs = string.whitespace

    for i, c in enumerate(text[startidx:]):
        if c == '"' and not _is_character_escaped(text, startidx + i):
            in_quotes = not in_quotes
        if not in_quotes:
            if c in chs:
                return startidx + i
    return -1


def _last_unquoted_char(text: str, chs: Optional[str]) -> int:
    """Return position of last unquoted character in list, or -1 if not found."""
    i = len(text) - 1
    in_quotes = False
    if chs is None:
        chs = string.whitespace
    while i > 0:
        if text[i] == '"' and not _is_character_escaped(text, i):
            in_quotes = not in_quotes
            
        if not in_quotes:
            if text[i] in chs:
                return i
        i -= 1
    return -1


def _split_quoted(text, separator, maxsplit=0):
```
