# Chunk: 9b50eecdcafa_1

- source: `.venv-lab/Lib/site-packages/jinja2/nodes.py`
- lines: 94-169
- chunk: 2/13

```
t.Optional[EvalContext]) -> EvalContext:
    if ctx is None:
        if node.environment is None:
            raise RuntimeError(
                "if no eval context is passed, the node must have an"
                " attached environment."
            )
        return EvalContext(node.environment)
    return ctx


class Node(metaclass=NodeType):
    """Baseclass for all Jinja nodes.  There are a number of nodes available
    of different types.  There are four major types:

    -   :class:`Stmt`: statements
    -   :class:`Expr`: expressions
    -   :class:`Helper`: helper nodes
    -   :class:`Template`: the outermost wrapper node

    All nodes have fields and attributes.  Fields may be other nodes, lists,
    or arbitrary values.  Fields are passed to the constructor as regular
    positional arguments, attributes as keyword arguments.  Each node has
    two attributes: `lineno` (the line number of the node) and `environment`.
    The `environment` attribute is set at the end of the parsing process for
    all nodes automatically.
    """

    fields: t.Tuple[str, ...] = ()
    attributes: t.Tuple[str, ...] = ("lineno", "environment")
    abstract = True

    lineno: int
    environment: t.Optional["Environment"]

    def __init__(self, *fields: t.Any, **attributes: t.Any) -> None:
        if self.abstract:
            raise TypeError("abstract nodes are not instantiable")
        if fields:
            if len(fields) != len(self.fields):
                if not self.fields:
                    raise TypeError(f"{type(self).__name__!r} takes 0 arguments")
                raise TypeError(
                    f"{type(self).__name__!r} takes 0 or {len(self.fields)}"
                    f" argument{'s' if len(self.fields) != 1 else ''}"
                )
            for name, arg in zip(self.fields, fields):
                setattr(self, name, arg)
        for attr in self.attributes:
            setattr(self, attr, attributes.pop(attr, None))
        if attributes:
            raise TypeError(f"unknown attribute {next(iter(attributes))!r}")

    def iter_fields(
        self,
        exclude: t.Optional[t.Container[str]] = None,
        only: t.Optional[t.Container[str]] = None,
    ) -> t.Iterator[t.Tuple[str, t.Any]]:
        """This method iterates over all fields that are defined and yields
        ``(key, value)`` tuples.  Per default all fields are returned, but
        it's possible to limit that to some fields by providing the `only`
        parameter or to exclude some using the `exclude` parameter.  Both
        should be sets or tuples of field names.
        """
        for name in self.fields:
            if (
                (exclude is None and only is None)
                or (exclude is not None and name not in exclude)
                or (only is not None and name in only)
            ):
                try:
                    yield name, getattr(self, name)
                except AttributeError:
                    pass
```
