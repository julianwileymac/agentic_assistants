# Chunk: 34eaefdb481d_1

- source: `.venv-lab/Lib/site-packages/pygments/lexers/nix.py`
- lines: 93-145
- chunk: 2/2

```
r'[a-zA-Z_][\w\'-]*', Text),

            (r"\$\{", String.Interpol, 'antiquote'),
        ],
        'comment': [
            (r'[^/*]+', Comment.Multiline),
            (r'/\*', Comment.Multiline, '#push'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline),
        ],
        'multiline': [
            (r"''(\$|'|\\n|\\r|\\t|\\)", String.Escape),
            (r"''", String.Multiline, '#pop'),
            (r'\$\{', String.Interpol, 'antiquote'),
            (r"[^'\$]+", String.Multiline),
            (r"\$[^\{']", String.Multiline),
            (r"'[^']", String.Multiline),
            (r"\$(?=')", String.Multiline),
        ],
        'doublequote': [
            (r'\\(\\|"|\$|n)', String.Escape),
            (r'"', String.Double, '#pop'),
            (r'\$\{', String.Interpol, 'antiquote'),
            (r'[^"\\\$]+', String.Double),
            (r'\$[^\{"]', String.Double),
            (r'\$(?=")', String.Double),
            (r'\\', String.Double),
        ],
        'antiquote': [
            (r"\}", String.Interpol, '#pop'),
            # TODO: we should probably escape also here ''${ \${
            (r"\$\{", String.Interpol, '#push'),
            include('root'),
        ],
        'block': [
            (r"\}", Punctuation, '#pop'),
            include('root'),
        ],
    }

    def analyse_text(text):
        rv = 0.0
        # TODO: let/in
        if re.search(r'import.+?<[^>]+>', text):
            rv += 0.4
        if re.search(r'mkDerivation\s+(\(|\{|rec)', text):
            rv += 0.4
        if re.search(r'=\s+mkIf\s+', text):
            rv += 0.4
        if re.search(r'\{[a-zA-Z,\s]+\}:', text):
            rv += 0.1
        return rv
```
