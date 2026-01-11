# Chunk: 5d66d7cbfc7f_3

- source: `.venv-lab/Lib/site-packages/jedi/inference/__init__.py`
- lines: 189-200
- chunk: 4/4

```
sn't use errors='replace'.
        code = parso.python_bytes_to_unicode(code, encoding='utf-8', errors='replace')

        if len(code) > settings._cropped_file_size:
            code = code[:settings._cropped_file_size]

        grammar = self.latest_grammar if use_latest_grammar else self.grammar
        return grammar.parse(code=code, path=path, file_io=file_io, **kwargs), code

    def parse(self, *args, **kwargs):
        return self.parse_and_get_code(*args, **kwargs)[0]
```
