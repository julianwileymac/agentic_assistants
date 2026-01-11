# Chunk: 9b50eecdcafa_3

- source: `.venv-lab/Lib/site-packages/jinja2/nodes.py`
- lines: 228-334
- chunk: 4/13

```
do.extend(node.iter_child_nodes())
        return self

    def set_environment(self, environment: "Environment") -> "Node":
        """Set the environment for all nodes."""
        todo = deque([self])
        while todo:
            node = todo.popleft()
            node.environment = environment
            todo.extend(node.iter_child_nodes())
        return self

    def __eq__(self, other: t.Any) -> bool:
        if type(self) is not type(other):
            return NotImplemented

        return tuple(self.iter_fields()) == tuple(other.iter_fields())

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        args_str = ", ".join(f"{a}={getattr(self, a, None)!r}" for a in self.fields)
        return f"{type(self).__name__}({args_str})"

    def dump(self) -> str:
        def _dump(node: t.Union[Node, t.Any]) -> None:
            if not isinstance(node, Node):
                buf.append(repr(node))
                return

            buf.append(f"nodes.{type(node).__name__}(")
            if not node.fields:
                buf.append(")")
                return
            for idx, field in enumerate(node.fields):
                if idx:
                    buf.append(", ")
                value = getattr(node, field)
                if isinstance(value, list):
                    buf.append("[")
                    for idx, item in enumerate(value):
                        if idx:
                            buf.append(", ")
                        _dump(item)
                    buf.append("]")
                else:
                    _dump(value)
            buf.append(")")

        buf: t.List[str] = []
        _dump(self)
        return "".join(buf)


class Stmt(Node):
    """Base node for all statements."""

    abstract = True


class Helper(Node):
    """Nodes that exist in a specific context only."""

    abstract = True


class Template(Node):
    """Node that represents a template.  This must be the outermost node that
    is passed to the compiler.
    """

    fields = ("body",)
    body: t.List[Node]


class Output(Stmt):
    """A node that holds multiple expressions which are then printed out.
    This is used both for the `print` statement and the regular template data.
    """

    fields = ("nodes",)
    nodes: t.List["Expr"]


class Extends(Stmt):
    """Represents an extends statement."""

    fields = ("template",)
    template: "Expr"


class For(Stmt):
    """The for loop.  `target` is the target for the iteration (usually a
    :class:`Name` or :class:`Tuple`), `iter` the iterable.  `body` is a list
    of nodes that are used as loop-body, and `else_` a list of nodes for the
    `else` block.  If no else node exists it has to be an empty list.

    For filtered nodes an expression can be stored as `test`, otherwise `None`.
    """

    fields = ("target", "iter", "body", "else_", "test", "recursive")
    target: Node
    iter: Node
    body: t.List[Node]
    else_: t.List[Node]
    test: t.Optional[Node]
```
