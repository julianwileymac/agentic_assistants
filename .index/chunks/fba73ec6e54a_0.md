# Chunk: fba73ec6e54a_0

- source: `.venv-lab/Lib/site-packages/prometheus_client/parser.py`
- lines: 1-94
- chunk: 1/5

```
import io as StringIO
import re
import string
from typing import Dict, Iterable, List, Match, Optional, TextIO, Tuple

from .metrics_core import Metric
from .samples import Sample
from .validation import (
    _is_valid_legacy_metric_name, _validate_labelname, _validate_metric_name,
)


def text_string_to_metric_families(text: str) -> Iterable[Metric]:
    """Parse Prometheus text format from a unicode string.

    See text_fd_to_metric_families.
    """
    yield from text_fd_to_metric_families(StringIO.StringIO(text))


ESCAPE_SEQUENCES = {
    '\\\\': '\\',
    '\\n': '\n',
    '\\"': '"',
}


def replace_escape_sequence(match: Match[str]) -> str:
    return ESCAPE_SEQUENCES[match.group(0)]


HELP_ESCAPING_RE = re.compile(r'\\[\\n]')
ESCAPING_RE = re.compile(r'\\[\\n"]')


def _replace_help_escaping(s: str) -> str:
    return HELP_ESCAPING_RE.sub(replace_escape_sequence, s)


def _replace_escaping(s: str) -> str:
    return ESCAPING_RE.sub(replace_escape_sequence, s)


def _is_character_escaped(s: str, charpos: int) -> bool:
    num_bslashes = 0
    while (charpos > num_bslashes
           and s[charpos - 1 - num_bslashes] == '\\'):
        num_bslashes += 1
    return num_bslashes % 2 == 1


def parse_labels(labels_string: str, openmetrics: bool = False) -> Dict[str, str]:
    labels: Dict[str, str] = {}

    # Copy original labels
    sub_labels = labels_string.strip()
    if openmetrics and sub_labels and sub_labels[0] == ',':
        raise ValueError("leading comma: " + labels_string)
    try:
        # Process one label at a time
        while sub_labels:
            # The label name is before the equal, or if there's no equal, that's the
            # metric name.
            
            name_term, value_term, sub_labels = _next_term(sub_labels, openmetrics)
            if not value_term:
                if openmetrics:
                    raise ValueError("empty term in line: " + labels_string)
                continue
            
            label_name, quoted_name = _unquote_unescape(name_term)
                
            if not quoted_name and not _is_valid_legacy_metric_name(label_name):
                raise ValueError("unquoted UTF-8 metric name")
                
            # Check for missing quotes 
            if not value_term or value_term[0] != '"':
                raise ValueError

            # The first quote is guaranteed to be after the equal.
            # Make sure that the next unescaped quote is the last character.
            i = 1
            while i < len(value_term):
                i = value_term.index('"', i)
                if not _is_character_escaped(value_term[:i], i):
                    break
                i += 1
            # The label value is between the first and last quote
            quote_end = i + 1
            if quote_end != len(value_term):
                raise ValueError("unexpected text after quote: " + labels_string)

            label_value, _ = _unquote_unescape(value_term)
```
