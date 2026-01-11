# Chunk: 9b50eecdcafa_6

- source: `.venv-lab/Lib/site-packages/jinja2/nodes.py`
- lines: 529-633
- chunk: 7/13

```
      and self.operator in eval_ctx.environment.intercepted_unops  # type: ignore
        ):
            raise Impossible()
        f = _uaop_to_func[self.operator]
        try:
            return f(self.node.as_const(eval_ctx))
        except Exception as e:
            raise Impossible() from e


class Name(Expr):
    """Looks up a name or stores a value in a name.
    The `ctx` of the node can be one of the following values:

    -   `store`: store a value in the name
    -   `load`: load that name
    -   `param`: like `store` but if the name was defined as function parameter.
    """

    fields = ("name", "ctx")
    name: str
    ctx: str

    def can_assign(self) -> bool:
        return self.name not in {"true", "false", "none", "True", "False", "None"}


class NSRef(Expr):
    """Reference to a namespace value assignment"""

    fields = ("name", "attr")
    name: str
    attr: str

    def can_assign(self) -> bool:
        # We don't need any special checks here; NSRef assignments have a
        # runtime check to ensure the target is a namespace object which will
        # have been checked already as it is created using a normal assignment
        # which goes through a `Name` node.
        return True


class Literal(Expr):
    """Baseclass for literals."""

    abstract = True


class Const(Literal):
    """All constant values.  The parser will return this node for simple
    constants such as ``42`` or ``"foo"`` but it can be used to store more
    complex values such as lists too.  Only constants with a safe
    representation (objects where ``eval(repr(x)) == x`` is true).
    """

    fields = ("value",)
    value: t.Any

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Any:
        return self.value

    @classmethod
    def from_untrusted(
        cls,
        value: t.Any,
        lineno: t.Optional[int] = None,
        environment: "t.Optional[Environment]" = None,
    ) -> "Const":
        """Return a const object if the value is representable as
        constant value in the generated code, otherwise it will raise
        an `Impossible` exception.
        """
        from .compiler import has_safe_repr

        if not has_safe_repr(value):
            raise Impossible()
        return cls(value, lineno=lineno, environment=environment)


class TemplateData(Literal):
    """A constant template string."""

    fields = ("data",)
    data: str

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> str:
        eval_ctx = get_eval_context(self, eval_ctx)
        if eval_ctx.volatile:
            raise Impossible()
        if eval_ctx.autoescape:
            return Markup(self.data)
        return self.data


class Tuple(Literal):
    """For loop unpacking and some other things like multiple arguments
    for subscripts.  Like for :class:`Name` `ctx` specifies if the tuple
    is used for loading the names or storing.
    """

    fields = ("items", "ctx")
    items: t.List[Expr]
    ctx: str
```
