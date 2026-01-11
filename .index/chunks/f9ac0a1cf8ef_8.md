# Chunk: f9ac0a1cf8ef_8

- source: `.venv-lab/Lib/site-packages/tornado/template.py`
- lines: 565-650
- chunk: 9/15

```
s[self.name] = self
        _Node.find_named_blocks(self, loader, named_blocks)


class _ExtendsBlock(_Node):
    def __init__(self, name: str) -> None:
        self.name = name


class _IncludeBlock(_Node):
    def __init__(self, name: str, reader: "_TemplateReader", line: int) -> None:
        self.name = name
        self.template_name = reader.name
        self.line = line

    def find_named_blocks(
        self, loader: Optional[BaseLoader], named_blocks: Dict[str, _NamedBlock]
    ) -> None:
        assert loader is not None
        included = loader.load(self.name, self.template_name)
        included.file.find_named_blocks(loader, named_blocks)

    def generate(self, writer: "_CodeWriter") -> None:
        assert writer.loader is not None
        included = writer.loader.load(self.name, self.template_name)
        with writer.include(included, self.line):
            included.file.body.generate(writer)


class _ApplyBlock(_Node):
    def __init__(self, method: str, line: int, body: _Node) -> None:
        self.method = method
        self.line = line
        self.body = body

    def each_child(self) -> Iterable["_Node"]:
        return (self.body,)

    def generate(self, writer: "_CodeWriter") -> None:
        method_name = "_tt_apply%d" % writer.apply_counter
        writer.apply_counter += 1
        writer.write_line("def %s():" % method_name, self.line)
        with writer.indent():
            writer.write_line("_tt_buffer = []", self.line)
            writer.write_line("_tt_append = _tt_buffer.append", self.line)
            self.body.generate(writer)
            writer.write_line("return _tt_utf8('').join(_tt_buffer)", self.line)
        writer.write_line(
            f"_tt_append(_tt_utf8({self.method}({method_name}())))", self.line
        )


class _ControlBlock(_Node):
    def __init__(self, statement: str, line: int, body: _Node) -> None:
        self.statement = statement
        self.line = line
        self.body = body

    def each_child(self) -> Iterable[_Node]:
        return (self.body,)

    def generate(self, writer: "_CodeWriter") -> None:
        writer.write_line("%s:" % self.statement, self.line)
        with writer.indent():
            self.body.generate(writer)
            # Just in case the body was empty
            writer.write_line("pass", self.line)


class _IntermediateControlBlock(_Node):
    def __init__(self, statement: str, line: int) -> None:
        self.statement = statement
        self.line = line

    def generate(self, writer: "_CodeWriter") -> None:
        # In case the previous block was empty
        writer.write_line("pass", self.line)
        writer.write_line("%s:" % self.statement, self.line, writer.indent_size() - 1)


class _Statement(_Node):
    def __init__(self, statement: str, line: int) -> None:
        self.statement = statement
        self.line = line

```
