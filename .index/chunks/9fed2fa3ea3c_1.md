# Chunk: 9fed2fa3ea3c_1

- source: `.venv-lab/Lib/site-packages/pygments/lexers/promql.py`
- lines: 112-177
- chunk: 2/2

```
                "sort",
                "sort_desc",
                "sqrt",
                "stddev_over_time",
                "stdvar_over_time",
                "sum_over_time",
                "time",
                "timestamp",
                "vector",
                "year",
            ),
            suffix=r"\b",
        ),
        Keyword.Reserved,
    )

    tokens = {
        "root": [
            (r"\n", Whitespace),
            (r"\s+", Whitespace),
            (r",", Punctuation),
            # Keywords
            base_keywords,
            aggregator_keywords,
            function_keywords,
            # Offsets
            (r"[1-9][0-9]*[smhdwy]", String),
            # Numbers
            (r"-?[0-9]+\.[0-9]+", Number.Float),
            (r"-?[0-9]+", Number.Integer),
            # Comments
            (r"#.*?$", Comment.Single),
            # Operators
            (r"(\+|\-|\*|\/|\%|\^)", Operator),
            (r"==|!=|>=|<=|<|>", Operator),
            (r"and|or|unless", Operator.Word),
            # Metrics
            (r"[_a-zA-Z][a-zA-Z0-9_]+", Name.Variable),
            # Params
            (r'(["\'])(.*?)(["\'])', bygroups(Punctuation, String, Punctuation)),
            # Other states
            (r"\(", Operator, "function"),
            (r"\)", Operator),
            (r"\{", Punctuation, "labels"),
            (r"\[", Punctuation, "range"),
        ],
        "labels": [
            (r"\}", Punctuation, "#pop"),
            (r"\n", Whitespace),
            (r"\s+", Whitespace),
            (r",", Punctuation),
            (r'([_a-zA-Z][a-zA-Z0-9_]*?)(\s*?)(=~|!=|=|!~)(\s*?)("|\')(.*?)("|\')',
             bygroups(Name.Label, Whitespace, Operator, Whitespace,
                      Punctuation, String, Punctuation)),
        ],
        "range": [
            (r"\]", Punctuation, "#pop"),
            (r"[1-9][0-9]*[smhdwy]", String),
        ],
        "function": [
            (r"\)", Operator, "#pop"),
            (r"\(", Operator, "#push"),
            default("#pop"),
        ],
    }
```
