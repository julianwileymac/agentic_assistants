# Chunk: 9b50eecdcafa_11

- source: `.venv-lab/Lib/site-packages/jinja2/nodes.py`
- lines: 1026-1129
- chunk: 12/13

```
ator = "+"


# Helpers for extensions


class EnvironmentAttribute(Expr):
    """Loads an attribute from the environment object.  This is useful for
    extensions that want to call a callback stored on the environment.
    """

    fields = ("name",)
    name: str


class ExtensionAttribute(Expr):
    """Returns the attribute of an extension bound to the environment.
    The identifier is the identifier of the :class:`Extension`.

    This node is usually constructed by calling the
    :meth:`~jinja2.ext.Extension.attr` method on an extension.
    """

    fields = ("identifier", "name")
    identifier: str
    name: str


class ImportedName(Expr):
    """If created with an import name the import name is returned on node
    access.  For example ``ImportedName('cgi.escape')`` returns the `escape`
    function from the cgi module on evaluation.  Imports are optimized by the
    compiler so there is no need to assign them to local variables.
    """

    fields = ("importname",)
    importname: str


class InternalName(Expr):
    """An internal name in the compiler.  You cannot create these nodes
    yourself but the parser provides a
    :meth:`~jinja2.parser.Parser.free_identifier` method that creates
    a new identifier for you.  This identifier is not available from the
    template and is not treated specially by the compiler.
    """

    fields = ("name",)
    name: str

    def __init__(self) -> None:
        raise TypeError(
            "Can't create internal names.  Use the "
            "`free_identifier` method on a parser."
        )


class MarkSafe(Expr):
    """Mark the wrapped expression as safe (wrap it as `Markup`)."""

    fields = ("expr",)
    expr: Expr

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> Markup:
        eval_ctx = get_eval_context(self, eval_ctx)
        return Markup(self.expr.as_const(eval_ctx))


class MarkSafeIfAutoescape(Expr):
    """Mark the wrapped expression as safe (wrap it as `Markup`) but
    only if autoescaping is active.

    .. versionadded:: 2.5
    """

    fields = ("expr",)
    expr: Expr

    def as_const(
        self, eval_ctx: t.Optional[EvalContext] = None
    ) -> t.Union[Markup, t.Any]:
        eval_ctx = get_eval_context(self, eval_ctx)
        if eval_ctx.volatile:
            raise Impossible()
        expr = self.expr.as_const(eval_ctx)
        if eval_ctx.autoescape:
            return Markup(expr)
        return expr


class ContextReference(Expr):
    """Returns the current template context.  It can be used like a
    :class:`Name` node, with a ``'load'`` ctx and will return the
    current :class:`~jinja2.runtime.Context` object.

    Here an example that assigns the current template name to a
    variable named `foo`::

        Assign(Name('foo', ctx='store'),
               Getattr(ContextReference(), 'name'))

    This is basically equivalent to using the
    :func:`~jinja2.pass_context` decorator when using the high-level
```
