# Chunk: f9ac0a1cf8ef_9

- source: `.venv-lab/Lib/site-packages/tornado/template.py`
- lines: 640-727
- chunk: 10/15

```
 was empty
        writer.write_line("pass", self.line)
        writer.write_line("%s:" % self.statement, self.line, writer.indent_size() - 1)


class _Statement(_Node):
    def __init__(self, statement: str, line: int) -> None:
        self.statement = statement
        self.line = line

    def generate(self, writer: "_CodeWriter") -> None:
        writer.write_line(self.statement, self.line)


class _Expression(_Node):
    def __init__(self, expression: str, line: int, raw: bool = False) -> None:
        self.expression = expression
        self.line = line
        self.raw = raw

    def generate(self, writer: "_CodeWriter") -> None:
        writer.write_line("_tt_tmp = %s" % self.expression, self.line)
        writer.write_line(
            "if isinstance(_tt_tmp, _tt_string_types):" " _tt_tmp = _tt_utf8(_tt_tmp)",
            self.line,
        )
        writer.write_line("else: _tt_tmp = _tt_utf8(str(_tt_tmp))", self.line)
        if not self.raw and writer.current_template.autoescape is not None:
            # In python3 functions like xhtml_escape return unicode,
            # so we have to convert to utf8 again.
            writer.write_line(
                "_tt_tmp = _tt_utf8(%s(_tt_tmp))" % writer.current_template.autoescape,
                self.line,
            )
        writer.write_line("_tt_append(_tt_tmp)", self.line)


class _Module(_Expression):
    def __init__(self, expression: str, line: int) -> None:
        super().__init__("_tt_modules." + expression, line, raw=True)


class _Text(_Node):
    def __init__(self, value: str, line: int, whitespace: str) -> None:
        self.value = value
        self.line = line
        self.whitespace = whitespace

    def generate(self, writer: "_CodeWriter") -> None:
        value = self.value

        # Compress whitespace if requested, with a crude heuristic to avoid
        # altering preformatted whitespace.
        if "<pre>" not in value:
            value = filter_whitespace(self.whitespace, value)

        if value:
            writer.write_line("_tt_append(%r)" % escape.utf8(value), self.line)


class ParseError(Exception):
    """Raised for template syntax errors.

    ``ParseError`` instances have ``filename`` and ``lineno`` attributes
    indicating the position of the error.

    .. versionchanged:: 4.3
       Added ``filename`` and ``lineno`` attributes.
    """

    def __init__(
        self, message: str, filename: Optional[str] = None, lineno: int = 0
    ) -> None:
        self.message = message
        # The names "filename" and "lineno" are chosen for consistency
        # with python SyntaxError.
        self.filename = filename
        self.lineno = lineno

    def __str__(self) -> str:
        return "%s at %s:%d" % (self.message, self.filename, self.lineno)


class _CodeWriter:
    def __init__(
        self,
        file: TextIO,
```
