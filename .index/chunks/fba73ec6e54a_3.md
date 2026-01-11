# Chunk: fba73ec6e54a_3

- source: `.venv-lab/Lib/site-packages/prometheus_client/parser.py`
- lines: 253-330
- chunk: 4/5

```
aise ValueError("invalid metric name:" + text)
        # Parse the remaining text after the name
        remaining_text = text[name_end + 1:]
        value, timestamp = _parse_value_and_timestamp(remaining_text)
        return Sample(name, {}, value, timestamp)
    name = text[:label_start].strip()
    label_end = _next_unquoted_char(text[label_start:], '}') + label_start
    labels = parse_labels(text[label_start + 1:label_end], False)
    if not name:
        # Name might be in the labels
        if '__name__' not in labels:
            raise ValueError
        name = labels['__name__']
        del labels['__name__']
    elif '__name__' in labels:
        raise ValueError("metric name specified more than once")
    # Parsing labels succeeded, continue parsing the remaining text
    remaining_text = text[label_end + 1:]
    value, timestamp = _parse_value_and_timestamp(remaining_text)
    return Sample(name, labels, value, timestamp)


def text_fd_to_metric_families(fd: TextIO) -> Iterable[Metric]:
    """Parse Prometheus text format from a file descriptor.

    This is a laxer parser than the main Go parser,
    so successful parsing does not imply that the parsed
    text meets the specification.

    Yields Metric's.
    """
    name = ''
    documentation = ''
    typ = 'untyped'
    samples: List[Sample] = []
    allowed_names = []

    def build_metric(name: str, documentation: str, typ: str, samples: List[Sample]) -> Metric:
        # Munge counters into OpenMetrics representation
        # used internally.
        if typ == 'counter':
            if name.endswith('_total'):
                name = name[:-6]
            else:
                new_samples = []
                for s in samples:
                    new_samples.append(Sample(s[0] + '_total', *s[1:]))
                    samples = new_samples
        metric = Metric(name, documentation, typ)
        metric.samples = samples
        return metric

    for line in fd:
        line = line.strip()

        if line.startswith('#'):
            parts = _split_quoted(line, None, 3)
            if len(parts) < 2:
                continue
            candidate_name, quoted = '', False
            if len(parts) > 2:
                # Ignore comment tokens
                if parts[1] != 'TYPE' and parts[1] != 'HELP':
                    continue
                candidate_name, quoted = _unquote_unescape(parts[2])
                if not quoted and not _is_valid_legacy_metric_name(candidate_name):
                    raise ValueError
            if parts[1] == 'HELP':
                if candidate_name != name:
                    if name != '':
                        yield build_metric(name, documentation, typ, samples)
                    # New metric
                    name = candidate_name
                    typ = 'untyped'
                    samples = []
                    allowed_names = [candidate_name]
                if len(parts) == 4:
```
