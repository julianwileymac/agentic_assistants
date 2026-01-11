# Chunk: ce070ca2eccb_2

- source: `.venv-lab/Lib/site-packages/pygments/lexers/webassembly.py`
- lines: 113-120
- chunk: 3/3

```
word, Operator, Number.Hex)),
            (r'(offset)(=)(\d(_?\d)*)', bygroups(Keyword, Operator, Number.Integer)),
            (r'(align)(=)(0x[\dA-Fa-f](_?[\dA-Fa-f])*)', bygroups(Keyword, Operator, Number.Hex)),
            (r'(align)(=)(\d(_?\d)*)', bygroups(Keyword, Operator, Number.Integer)),
            default('#pop'),
        ]
    }
```
