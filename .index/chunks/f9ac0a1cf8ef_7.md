# Chunk: f9ac0a1cf8ef_7

- source: `.venv-lab/Lib/site-packages/tornado/template.py`
- lines: 484-576
- chunk: 8/15

```
: Any) -> None:
        super().__init__(**kwargs)
        self.dict = dict

    def resolve_path(self, name: str, parent_path: Optional[str] = None) -> str:
        if (
            parent_path
            and not parent_path.startswith("<")
            and not parent_path.startswith("/")
            and not name.startswith("/")
        ):
            file_dir = posixpath.dirname(parent_path)
            name = posixpath.normpath(posixpath.join(file_dir, name))
        return name

    def _create_template(self, name: str) -> Template:
        return Template(self.dict[name], name=name, loader=self)


class _Node:
    def each_child(self) -> Iterable["_Node"]:
        return ()

    def generate(self, writer: "_CodeWriter") -> None:
        raise NotImplementedError()

    def find_named_blocks(
        self, loader: Optional[BaseLoader], named_blocks: Dict[str, "_NamedBlock"]
    ) -> None:
        for child in self.each_child():
            child.find_named_blocks(loader, named_blocks)


class _File(_Node):
    def __init__(self, template: Template, body: "_ChunkList") -> None:
        self.template = template
        self.body = body
        self.line = 0

    def generate(self, writer: "_CodeWriter") -> None:
        writer.write_line("def _tt_execute():", self.line)
        with writer.indent():
            writer.write_line("_tt_buffer = []", self.line)
            writer.write_line("_tt_append = _tt_buffer.append", self.line)
            self.body.generate(writer)
            writer.write_line("return _tt_utf8('').join(_tt_buffer)", self.line)

    def each_child(self) -> Iterable["_Node"]:
        return (self.body,)


class _ChunkList(_Node):
    def __init__(self, chunks: List[_Node]) -> None:
        self.chunks = chunks

    def generate(self, writer: "_CodeWriter") -> None:
        for chunk in self.chunks:
            chunk.generate(writer)

    def each_child(self) -> Iterable["_Node"]:
        return self.chunks


class _NamedBlock(_Node):
    def __init__(self, name: str, body: _Node, template: Template, line: int) -> None:
        self.name = name
        self.body = body
        self.template = template
        self.line = line

    def each_child(self) -> Iterable["_Node"]:
        return (self.body,)

    def generate(self, writer: "_CodeWriter") -> None:
        block = writer.named_blocks[self.name]
        with writer.include(block.template, self.line):
            block.body.generate(writer)

    def find_named_blocks(
        self, loader: Optional[BaseLoader], named_blocks: Dict[str, "_NamedBlock"]
    ) -> None:
        named_blocks[self.name] = self
        _Node.find_named_blocks(self, loader, named_blocks)


class _ExtendsBlock(_Node):
    def __init__(self, name: str) -> None:
        self.name = name


class _IncludeBlock(_Node):
    def __init__(self, name: str, reader: "_TemplateReader", line: int) -> None:
```
