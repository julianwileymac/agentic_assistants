# Chunk: f9ac0a1cf8ef_10

- source: `.venv-lab/Lib/site-packages/tornado/template.py`
- lines: 714-807
- chunk: 11/15

```
nsistency
        # with python SyntaxError.
        self.filename = filename
        self.lineno = lineno

    def __str__(self) -> str:
        return "%s at %s:%d" % (self.message, self.filename, self.lineno)


class _CodeWriter:
    def __init__(
        self,
        file: TextIO,
        named_blocks: Dict[str, _NamedBlock],
        loader: Optional[BaseLoader],
        current_template: Template,
    ) -> None:
        self.file = file
        self.named_blocks = named_blocks
        self.loader = loader
        self.current_template = current_template
        self.apply_counter = 0
        self.include_stack = []  # type: List[Tuple[Template, int]]
        self._indent = 0

    def indent_size(self) -> int:
        return self._indent

    def indent(self) -> "ContextManager":
        class Indenter:
            def __enter__(_) -> "_CodeWriter":
                self._indent += 1
                return self

            def __exit__(_, *args: Any) -> None:
                assert self._indent > 0
                self._indent -= 1

        return Indenter()

    def include(self, template: Template, line: int) -> "ContextManager":
        self.include_stack.append((self.current_template, line))
        self.current_template = template

        class IncludeTemplate:
            def __enter__(_) -> "_CodeWriter":
                return self

            def __exit__(_, *args: Any) -> None:
                self.current_template = self.include_stack.pop()[0]

        return IncludeTemplate()

    def write_line(
        self, line: str, line_number: int, indent: Optional[int] = None
    ) -> None:
        if indent is None:
            indent = self._indent
        line_comment = "  # %s:%d" % (self.current_template.name, line_number)
        if self.include_stack:
            ancestors = [
                "%s:%d" % (tmpl.name, lineno) for (tmpl, lineno) in self.include_stack
            ]
            line_comment += " (via %s)" % ", ".join(reversed(ancestors))
        print("    " * indent + line + line_comment, file=self.file)


class _TemplateReader:
    def __init__(self, name: str, text: str, whitespace: str) -> None:
        self.name = name
        self.text = text
        self.whitespace = whitespace
        self.line = 1
        self.pos = 0

    def find(self, needle: str, start: int = 0, end: Optional[int] = None) -> int:
        assert start >= 0, start
        pos = self.pos
        start += pos
        if end is None:
            index = self.text.find(needle, start)
        else:
            end += pos
            assert end >= start
            index = self.text.find(needle, start, end)
        if index != -1:
            index -= pos
        return index

    def consume(self, count: Optional[int] = None) -> str:
        if count is None:
            count = len(self.text) - self.pos
        newpos = self.pos + count
```
