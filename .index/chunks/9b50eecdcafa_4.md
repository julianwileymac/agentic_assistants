# Chunk: 9b50eecdcafa_4

- source: `.venv-lab/Lib/site-packages/jinja2/nodes.py`
- lines: 323-439
- chunk: 5/13

```
xists it has to be an empty list.

    For filtered nodes an expression can be stored as `test`, otherwise `None`.
    """

    fields = ("target", "iter", "body", "else_", "test", "recursive")
    target: Node
    iter: Node
    body: t.List[Node]
    else_: t.List[Node]
    test: t.Optional[Node]
    recursive: bool


class If(Stmt):
    """If `test` is true, `body` is rendered, else `else_`."""

    fields = ("test", "body", "elif_", "else_")
    test: Node
    body: t.List[Node]
    elif_: t.List["If"]
    else_: t.List[Node]


class Macro(Stmt):
    """A macro definition.  `name` is the name of the macro, `args` a list of
    arguments and `defaults` a list of defaults if there are any.  `body` is
    a list of nodes for the macro body.
    """

    fields = ("name", "args", "defaults", "body")
    name: str
    args: t.List["Name"]
    defaults: t.List["Expr"]
    body: t.List[Node]


class CallBlock(Stmt):
    """Like a macro without a name but a call instead.  `call` is called with
    the unnamed macro as `caller` argument this node holds.
    """

    fields = ("call", "args", "defaults", "body")
    call: "Call"
    args: t.List["Name"]
    defaults: t.List["Expr"]
    body: t.List[Node]


class FilterBlock(Stmt):
    """Node for filter sections."""

    fields = ("body", "filter")
    body: t.List[Node]
    filter: "Filter"


class With(Stmt):
    """Specific node for with statements.  In older versions of Jinja the
    with statement was implemented on the base of the `Scope` node instead.

    .. versionadded:: 2.9.3
    """

    fields = ("targets", "values", "body")
    targets: t.List["Expr"]
    values: t.List["Expr"]
    body: t.List[Node]


class Block(Stmt):
    """A node that represents a block.

    .. versionchanged:: 3.0.0
        the `required` field was added.
    """

    fields = ("name", "body", "scoped", "required")
    name: str
    body: t.List[Node]
    scoped: bool
    required: bool


class Include(Stmt):
    """A node that represents the include tag."""

    fields = ("template", "with_context", "ignore_missing")
    template: "Expr"
    with_context: bool
    ignore_missing: bool


class Import(Stmt):
    """A node that represents the import tag."""

    fields = ("template", "target", "with_context")
    template: "Expr"
    target: str
    with_context: bool


class FromImport(Stmt):
    """A node that represents the from import tag.  It's important to not
    pass unsafe names to the name attribute.  The compiler translates the
    attribute lookups directly into getattr calls and does *not* use the
    subscript callback of the interface.  As exported variables may not
    start with double underscores (which the parser asserts) this is not a
    problem for regular Jinja code, but if this node is used in an extension
    extra care must be taken.

    The list of names may contain tuples if aliases are wanted.
    """

    fields = ("template", "names", "with_context")
    template: "Expr"
```
