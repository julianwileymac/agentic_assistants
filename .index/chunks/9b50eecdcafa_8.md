# Chunk: 9b50eecdcafa_8

- source: `.venv-lab/Lib/site-packages/jinja2/nodes.py`
- lines: 715-815
- chunk: 9/13

```
 self.expr2.as_const(eval_ctx)


def args_as_const(
    node: t.Union["_FilterTestCommon", "Call"], eval_ctx: t.Optional[EvalContext]
) -> t.Tuple[t.List[t.Any], t.Dict[t.Any, t.Any]]:
    args = [x.as_const(eval_ctx) for x in node.args]
    kwargs = dict(x.as_const(eval_ctx) for x in node.kwargs)

    if node.dyn_args is not None:
        try:
            args.extend(node.dyn_args.as_const(eval_ctx))
        except Exception as e:
            raise Impossible() from e

    if node.dyn_kwargs is not None:
        try:
            kwargs.update(node.dyn_kwargs.as_const(eval_ctx))
        except Exception as e:
            raise Impossible() from e

    return args, kwargs


class _FilterTestCommon(Expr):
    fields = ("node", "name", "args", "kwargs", "dyn_args", "dyn_kwargs")
    node: Expr
    name: str
    args: t.List[Expr]
    kwargs: t.List[Pair]
    dyn_args: t.Optional[Expr]
    dyn_kwargs: t.Optional[Expr]
    abstract = True
    _is_filter = True

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Any:
        eval_ctx = get_eval_context(self, eval_ctx)

        if eval_ctx.volatile:
            raise Impossible()

        if self._is_filter:
            env_map = eval_ctx.environment.filters
        else:
            env_map = eval_ctx.environment.tests

        func = env_map.get(self.name)
        pass_arg = _PassArg.from_obj(func)  # type: ignore

        if func is None or pass_arg is _PassArg.context:
            raise Impossible()

        if eval_ctx.environment.is_async and (
            getattr(func, "jinja_async_variant", False) is True
            or inspect.iscoroutinefunction(func)
        ):
            raise Impossible()

        args, kwargs = args_as_const(self, eval_ctx)
        args.insert(0, self.node.as_const(eval_ctx))

        if pass_arg is _PassArg.eval_context:
            args.insert(0, eval_ctx)
        elif pass_arg is _PassArg.environment:
            args.insert(0, eval_ctx.environment)

        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise Impossible() from e


class Filter(_FilterTestCommon):
    """Apply a filter to an expression. ``name`` is the name of the
    filter, the other fields are the same as :class:`Call`.

    If ``node`` is ``None``, the filter is being used in a filter block
    and is applied to the content of the block.
    """

    node: t.Optional[Expr]  # type: ignore

    def as_const(self, eval_ctx: t.Optional[EvalContext] = None) -> t.Any:
        if self.node is None:
            raise Impossible()

        return super().as_const(eval_ctx=eval_ctx)


class Test(_FilterTestCommon):
    """Apply a test to an expression. ``name`` is the name of the test,
    the other field are the same as :class:`Call`.

    .. versionchanged:: 3.0
        ``as_const`` shares the same logic for filters and tests. Tests
        check for volatile, async, and ``@pass_context`` etc.
        decorators.
    """

    _is_filter = False
```
