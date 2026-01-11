# Chunk: 9b50eecdcafa_9

- source: `.venv-lab/Lib/site-packages/jinja2/nodes.py`
- lines: 805-911
- chunk: 10/13

```
``name`` is the name of the test,
    the other field are the same as :class:`Call`.

    .. versionchanged:: 3.0
        ``as_const`` shares the same logic for filters and tests. Tests
        check for volatile, async, and ``@pass_context`` etc.
        decorators.
    """

    _is_filter = False


class Call(Expr):
    """Calls an expression.  `args` is a list of arguments, `kwargs` a list
    of keyword arguments (list of :class:`Keyword` nodes), and `dyn_args`
    and `dyn_kwargs` has to be either `None` or a node that is used as
    node for dynamic positional (``*args``) or keyword (``**kwargs``)
    arguments.
    """

    fields = ("node", "args", "kwargs", "dyn_args", "dyn_kwargs")
    node: Expr
    args: t.List[Expr]
    kwargs: t.List[Keyword]
    dyn_args: t.Optional[Expr]
    dyn_kwargs: t.Optional[Expr]


class Getitem(Expr):
    """Get an attribute or item from an expression and prefer the item."""

    fields = ("node", "arg", "ctx")
    node: Expr
    arg: Expr
    ctx: str

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Any:
        if self.ctx != "load":
            raise Impossible()

        eval_ctx = get_eval_context(self, eval_ctx)

        try:
            return eval_ctx.environment.getitem(
                self.node.as_const(eval_ctx), self.arg.as_const(eval_ctx)
            )
        except Exception as e:
            raise Impossible() from e


class Getattr(Expr):
    """Get an attribute or item from an expression that is a ascii-only
    bytestring and prefer the attribute.
    """

    fields = ("node", "attr", "ctx")
    node: Expr
    attr: str
    ctx: str

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Any:
        if self.ctx != "load":
            raise Impossible()

        eval_ctx = get_eval_context(self, eval_ctx)

        try:
            return eval_ctx.environment.getattr(self.node.as_const(eval_ctx), self.attr)
        except Exception as e:
            raise Impossible() from e


class Slice(Expr):
    """Represents a slice object.  This must only be used as argument for
    :class:`Subscript`.
    """

    fields = ("start", "stop", "step")
    start: t.Optional[Expr]
    stop: t.Optional[Expr]
    step: t.Optional[Expr]

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> slice:
        eval_ctx = get_eval_context(self, eval_ctx)

        def const(obj: t.Optional[Expr]) -> t.Optional[t.Any]:
            if obj is None:
                return None
            return obj.as_const(eval_ctx)

        return slice(const(self.start), const(self.stop), const(self.step))


class Concat(Expr):
    """Concatenates the list of expressions provided after converting
    them to strings.
    """

    fields = ("nodes",)
    nodes: t.List[Expr]

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> str:
        eval_ctx = get_eval_context(self, eval_ctx)
        return "".join(str(x.as_const(eval_ctx)) for x in self.nodes)
```
