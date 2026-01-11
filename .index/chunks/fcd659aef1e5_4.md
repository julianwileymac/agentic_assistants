# Chunk: fcd659aef1e5_4

- source: `.venv-lab/Lib/site-packages/tornado/util.py`
- lines: 306-383
- chunk: 5/6

```
mpl
        base.__impl_kwargs = kwargs

    @classmethod
    def configured_class(cls):
        # type: () -> Type[Configurable]
        """Returns the currently configured class."""
        base = cls.configurable_base()
        # Manually mangle the private name to see whether this base
        # has been configured (and not another base higher in the
        # hierarchy).
        if base.__dict__.get("_Configurable__impl_class") is None:
            base.__impl_class = cls.configurable_default()
        if base.__impl_class is not None:
            return base.__impl_class
        else:
            # Should be impossible, but mypy wants an explicit check.
            raise ValueError("configured class not found")

    @classmethod
    def _save_configuration(cls):
        # type: () -> Tuple[Optional[Type[Configurable]], Dict[str, Any]]
        base = cls.configurable_base()
        return (base.__impl_class, base.__impl_kwargs)

    @classmethod
    def _restore_configuration(cls, saved):
        # type: (Tuple[Optional[Type[Configurable]], Dict[str, Any]]) -> None
        base = cls.configurable_base()
        base.__impl_class = saved[0]
        base.__impl_kwargs = saved[1]


class ArgReplacer:
    """Replaces one value in an ``args, kwargs`` pair.

    Inspects the function signature to find an argument by name
    whether it is passed by position or keyword.  For use in decorators
    and similar wrappers.
    """

    def __init__(self, func: Callable, name: str) -> None:
        self.name = name
        try:
            self.arg_pos = self._getargnames(func).index(name)  # type: Optional[int]
        except ValueError:
            # Not a positional parameter
            self.arg_pos = None

    def _getargnames(self, func: Callable) -> List[str]:
        try:
            return getfullargspec(func).args
        except TypeError:
            if hasattr(func, "func_code"):
                # Cython-generated code has all the attributes needed
                # by inspect.getfullargspec, but the inspect module only
                # works with ordinary functions. Inline the portion of
                # getfullargspec that we need here. Note that for static
                # functions the @cython.binding(True) decorator must
                # be used (for methods it works out of the box).
                code = func.func_code  # type: ignore
                return code.co_varnames[: code.co_argcount]
            raise

    def get_old_value(
        self, args: Sequence[Any], kwargs: Dict[str, Any], default: Any = None
    ) -> Any:
        """Returns the old value of the named argument without replacing it.

        Returns ``default`` if the argument is not present.
        """
        if self.arg_pos is not None and len(args) > self.arg_pos:
            return args[self.arg_pos]
        else:
            return kwargs.get(self.name, default)

    def replace(
```
