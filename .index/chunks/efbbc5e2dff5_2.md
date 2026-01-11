# Chunk: efbbc5e2dff5_2

- source: `.venv-lab/Lib/site-packages/pygments/lexers/ldap.py`
- lines: 132-156
- chunk: 3/3

```
+)',
             bygroups(Keyword, Whitespace, Number.Integer)),
            (r'(VERSION)(\s+)(2|3)', bygroups(Keyword, Whitespace, Number.Integer)),
            # Constants
            (r'(DEREF)(\s+)(never|searching|finding|always)',
             bygroups(Keyword, Whitespace, Keyword.Constant)),
            (rf'(SASL_SECPROPS)(\s+)((?:{_secprops})(?:,{_secprops})*)',
             bygroups(Keyword, Whitespace, Keyword.Constant)),
            (r'(SASL_CBINDING)(\s+)(none|tls-unique|tls-endpoint)',
             bygroups(Keyword, Whitespace, Keyword.Constant)),
            (r'(TLS_REQ(?:CERT|SAN))(\s+)(allow|demand|hard|never|try)',
             bygroups(Keyword, Whitespace, Keyword.Constant)),
            (r'(TLS_CRLCHECK)(\s+)(none|peer|all)',
             bygroups(Keyword, Whitespace, Keyword.Constant)),
            # Literals
            (r'(BASE|BINDDN)(\s+)(\S+)$',
             bygroups(Keyword, Whitespace, Literal)),
            # Accepts hostname with or without port.
            (r'(HOST)(\s+)([a-z0-9]+)((?::(\d+))?)',
             bygroups(Keyword, Whitespace, Literal, Number.Integer)),
            (rf'({_literal_keywords})(\s+)(\S+)$',
             bygroups(Keyword, Whitespace, Literal)),
        ],
    }
```
