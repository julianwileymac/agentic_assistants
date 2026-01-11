# Chunk: 9b50eecdcafa_5

- source: `.venv-lab/Lib/site-packages/jinja2/nodes.py`
- lines: 430-539
- chunk: 6/13

```
cores (which the parser asserts) this is not a
    problem for regular Jinja code, but if this node is used in an extension
    extra care must be taken.

    The list of names may contain tuples if aliases are wanted.
    """

    fields = ("template", "names", "with_context")
    template: "Expr"
    names: t.List[t.Union[str, t.Tuple[str, str]]]
    with_context: bool


class ExprStmt(Stmt):
    """A statement that evaluates an expression and discards the result."""

    fields = ("node",)
    node: Node


class Assign(Stmt):
    """Assigns an expression to a target."""

    fields = ("target", "node")
    target: "Expr"
    node: Node


class AssignBlock(Stmt):
    """Assigns a block to a target."""

    fields = ("target", "filter", "body")
    target: "Expr"
    filter: t.Optional["Filter"]
    body: t.List[Node]


class Expr(Node):
    """Baseclass for all expressions."""

    abstract = True

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Any:
        """Return the value of the expression as constant or raise
        :exc:`Impossible` if this was not possible.

        An :class:`EvalContext` can be provided, if none is given
        a default context is created which requires the nodes to have
        an attached environment.

        .. versionchanged:: 2.4
           the `eval_ctx` parameter was added.
        """
        raise Impossible()

    def can_assign(self) -> bool:
        """Check if it's possible to assign something to this node."""
        return False


class BinExpr(Expr):
    """Baseclass for all binary expressions."""

    fields = ("left", "right")
    left: Expr
    right: Expr
    operator: str
    abstract = True

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Any:
        eval_ctx = get_eval_context(self, eval_ctx)

        # intercepted operators cannot be folded at compile time
        if (
            eval_ctx.environment.sandboxed
            and self.operator in eval_ctx.environment.intercepted_binops  # type: ignore
        ):
            raise Impossible()
        f = _binop_to_func[self.operator]
        try:
            return f(self.left.as_const(eval_ctx), self.right.as_const(eval_ctx))
        except Exception as e:
            raise Impossible() from e


class UnaryExpr(Expr):
    """Baseclass for all unary expressions."""

    fields = ("node",)
    node: Expr
    operator: str
    abstract = True

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Any:
        eval_ctx = get_eval_context(self, eval_ctx)

        # intercepted operators cannot be folded at compile time
        if (
            eval_ctx.environment.sandboxed
            and self.operator in eval_ctx.environment.intercepted_unops  # type: ignore
        ):
            raise Impossible()
        f = _uaop_to_func[self.operator]
        try:
            return f(self.node.as_const(eval_ctx))
        except Exception as e:
            raise Impossible() from e
```
