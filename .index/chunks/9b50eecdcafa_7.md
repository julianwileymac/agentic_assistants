# Chunk: 9b50eecdcafa_7

- source: `.venv-lab/Lib/site-packages/jinja2/nodes.py`
- lines: 620-724
- chunk: 8/13

```
lf.data


class Tuple(Literal):
    """For loop unpacking and some other things like multiple arguments
    for subscripts.  Like for :class:`Name` `ctx` specifies if the tuple
    is used for loading the names or storing.
    """

    fields = ("items", "ctx")
    items: t.List[Expr]
    ctx: str

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Tuple[t.Any, ...]:
        eval_ctx = get_eval_context(self, eval_ctx)
        return tuple(x.as_const(eval_ctx) for x in self.items)

    def can_assign(self) -> bool:
        for item in self.items:
            if not item.can_assign():
                return False
        return True


class List(Literal):
    """Any list literal such as ``[1, 2, 3]``"""

    fields = ("items",)
    items: t.List[Expr]

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.List[t.Any]:
        eval_ctx = get_eval_context(self, eval_ctx)
        return [x.as_const(eval_ctx) for x in self.items]


class Dict(Literal):
    """Any dict literal such as ``{1: 2, 3: 4}``.  The items must be a list of
    :class:`Pair` nodes.
    """

    fields = ("items",)
    items: t.List["Pair"]

    def as_const(
        self, eval_ctx: t.Optional[EvalContext] = None
    ) -> t.Dict[t.Any, t.Any]:
        eval_ctx = get_eval_context(self, eval_ctx)
        return dict(x.as_const(eval_ctx) for x in self.items)


class Pair(Helper):
    """A key, value pair for dicts."""

    fields = ("key", "value")
    key: Expr
    value: Expr

    def as_const(
        self, eval_ctx: t.Optional[EvalContext] = None
    ) -> t.Tuple[t.Any, t.Any]:
        eval_ctx = get_eval_context(self, eval_ctx)
        return self.key.as_const(eval_ctx), self.value.as_const(eval_ctx)


class Keyword(Helper):
    """A key, value pair for keyword arguments where key is a string."""

    fields = ("key", "value")
    key: str
    value: Expr

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Tuple[str, t.Any]:
        eval_ctx = get_eval_context(self, eval_ctx)
        return self.key, self.value.as_const(eval_ctx)


class CondExpr(Expr):
    """A conditional expression (inline if expression).  (``{{
    foo if bar else baz }}``)
    """

    fields = ("test", "expr1", "expr2")
    test: Expr
    expr1: Expr
    expr2: t.Optional[Expr]

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Any:
        eval_ctx = get_eval_context(self, eval_ctx)
        if self.test.as_const(eval_ctx):
            return self.expr1.as_const(eval_ctx)

        # if we evaluate to an undefined object, we better do that at runtime
        if self.expr2 is None:
            raise Impossible()

        return self.expr2.as_const(eval_ctx)


def args_as_const(
    node: t.Union["_FilterTestCommon", "Call"], eval_ctx: t.Optional[EvalContext]
) -> t.Tuple[t.List[t.Any], t.Dict[t.Any, t.Any]]:
    args = [x.as_const(eval_ctx) for x in node.args]
    kwargs = dict(x.as_const(eval_ctx) for x in node.kwargs)
```
