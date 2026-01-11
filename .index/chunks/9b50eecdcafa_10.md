# Chunk: 9b50eecdcafa_10

- source: `.venv-lab/Lib/site-packages/jinja2/nodes.py`
- lines: 899-1042
- chunk: 11/13

```
ovided after converting
    them to strings.
    """

    fields = ("nodes",)
    nodes: t.List[Expr]

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> str:
        eval_ctx = get_eval_context(self, eval_ctx)
        return "".join(str(x.as_const(eval_ctx)) for x in self.nodes)


class Compare(Expr):
    """Compares an expression with some other expressions.  `ops` must be a
    list of :class:`Operand`\\s.
    """

    fields = ("expr", "ops")
    expr: Expr
    ops: t.List["Operand"]

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Any:
        eval_ctx = get_eval_context(self, eval_ctx)
        result = value = self.expr.as_const(eval_ctx)

        try:
            for op in self.ops:
                new_value = op.expr.as_const(eval_ctx)
                result = _cmpop_to_func[op.op](value, new_value)

                if not result:
                    return False

                value = new_value
        except Exception as e:
            raise Impossible() from e

        return result


class Operand(Helper):
    """Holds an operator and an expression."""

    fields = ("op", "expr")
    op: str
    expr: Expr


class Mul(BinExpr):
    """Multiplies the left with the right node."""

    operator = "*"


class Div(BinExpr):
    """Divides the left by the right node."""

    operator = "/"


class FloorDiv(BinExpr):
    """Divides the left by the right node and converts the
    result into an integer by truncating.
    """

    operator = "//"


class Add(BinExpr):
    """Add the left to the right node."""

    operator = "+"


class Sub(BinExpr):
    """Subtract the right from the left node."""

    operator = "-"


class Mod(BinExpr):
    """Left modulo right."""

    operator = "%"


class Pow(BinExpr):
    """Left to the power of right."""

    operator = "**"


class And(BinExpr):
    """Short circuited AND."""

    operator = "and"

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Any:
        eval_ctx = get_eval_context(self, eval_ctx)
        return self.left.as_const(eval_ctx) and self.right.as_const(eval_ctx)


class Or(BinExpr):
    """Short circuited OR."""

    operator = "or"

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Any:
        eval_ctx = get_eval_context(self, eval_ctx)
        return self.left.as_const(eval_ctx) or self.right.as_const(eval_ctx)


class Not(UnaryExpr):
    """Negate the expression."""

    operator = "not"


class Neg(UnaryExpr):
    """Make the expression negative."""

    operator = "-"


class Pos(UnaryExpr):
    """Make the expression positive (noop for most expressions)"""

    operator = "+"


# Helpers for extensions


class EnvironmentAttribute(Expr):
    """Loads an attribute from the environment object.  This is useful for
    extensions that want to call a callback stored on the environment.
    """

    fields = ("name",)
    name: str


class ExtensionAttribute(Expr):
```
