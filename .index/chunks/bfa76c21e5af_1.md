# Chunk: bfa76c21e5af_1

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/typeguard/_decorators.py`
- lines: 76-152
- chunk: 2/4

```
arget_lineno is None:
        return "instrumentor did not find the target function"

    module_code = compile(module_ast, f.__code__.co_filename, "exec", dont_inherit=True)
    new_code = find_target_function(
        module_code, target_path, instrumentor.target_lineno
    )
    if not new_code:
        return "cannot find the target function in the AST"

    if global_config.debug_instrumentation and sys.version_info >= (3, 9):
        # Find the matching AST node, then unparse it to source and print to stdout
        print(
            f"Source code of {f.__qualname__}() after instrumentation:"
            "\n----------------------------------------------",
            file=sys.stderr,
        )
        print(ast.unparse(instrumentor.target_node), file=sys.stderr)
        print(
            "----------------------------------------------",
            file=sys.stderr,
        )

    closure = f.__closure__
    if new_code.co_freevars != f.__code__.co_freevars:
        # Create a new closure and find values for the new free variables
        frame = cast(FrameType, inspect.currentframe())
        frame = cast(FrameType, frame.f_back)
        frame_locals = cast(FrameType, frame.f_back).f_locals
        cells: list[_Cell] = []
        for key in new_code.co_freevars:
            if key in instrumentor.names_used_in_annotations:
                # Find the value and make a new cell from it
                value = frame_locals.get(key) or ForwardRef(key)
                cells.append(make_cell(value))
            else:
                # Reuse the cell from the existing closure
                assert f.__closure__
                cells.append(f.__closure__[f.__code__.co_freevars.index(key)])

        closure = tuple(cells)

    new_function = FunctionType(new_code, f.__globals__, f.__name__, closure=closure)
    new_function.__module__ = f.__module__
    new_function.__name__ = f.__name__
    new_function.__qualname__ = f.__qualname__
    new_function.__annotations__ = f.__annotations__
    new_function.__doc__ = f.__doc__
    new_function.__defaults__ = f.__defaults__
    new_function.__kwdefaults__ = f.__kwdefaults__
    return new_function


@overload
def typechecked(
    *,
    forward_ref_policy: ForwardRefPolicy | Unset = unset,
    typecheck_fail_callback: TypeCheckFailCallback | Unset = unset,
    collection_check_strategy: CollectionCheckStrategy | Unset = unset,
    debug_instrumentation: bool | Unset = unset,
) -> Callable[[T_CallableOrType], T_CallableOrType]: ...


@overload
def typechecked(target: T_CallableOrType) -> T_CallableOrType: ...


def typechecked(
    target: T_CallableOrType | None = None,
    *,
    forward_ref_policy: ForwardRefPolicy | Unset = unset,
    typecheck_fail_callback: TypeCheckFailCallback | Unset = unset,
    collection_check_strategy: CollectionCheckStrategy | Unset = unset,
    debug_instrumentation: bool | Unset = unset,
) -> Any:
    """
```
