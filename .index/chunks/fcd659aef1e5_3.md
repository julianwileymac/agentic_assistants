# Chunk: fcd659aef1e5_3

- source: `.venv-lab/Lib/site-packages/tornado/util.py`
- lines: 237-315
- chunk: 4/6

```
igurable subclass T,
    # all the types are subclasses of T, not just Configurable).
    __impl_class = None  # type: Optional[Type[Configurable]]
    __impl_kwargs = None  # type: Dict[str, Any]

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        base = cls.configurable_base()
        init_kwargs = {}  # type: Dict[str, Any]
        if cls is base:
            impl = cls.configured_class()
            if base.__impl_kwargs:
                init_kwargs.update(base.__impl_kwargs)
        else:
            impl = cls
        init_kwargs.update(kwargs)
        if impl.configurable_base() is not base:
            # The impl class is itself configurable, so recurse.
            return impl(*args, **init_kwargs)
        instance = super().__new__(impl)
        # initialize vs __init__ chosen for compatibility with AsyncHTTPClient
        # singleton magic.  If we get rid of that we can switch to __init__
        # here too.
        instance.initialize(*args, **init_kwargs)
        return instance

    @classmethod
    def configurable_base(cls):
        # type: () -> Type[Configurable]
        """Returns the base class of a configurable hierarchy.

        This will normally return the class in which it is defined.
        (which is *not* necessarily the same as the ``cls`` classmethod
        parameter).

        """
        raise NotImplementedError()

    @classmethod
    def configurable_default(cls):
        # type: () -> Type[Configurable]
        """Returns the implementation class to be used if none is configured."""
        raise NotImplementedError()

    def _initialize(self) -> None:
        pass

    initialize = _initialize  # type: Callable[..., None]
    """Initialize a `Configurable` subclass instance.

    Configurable classes should use `initialize` instead of ``__init__``.

    .. versionchanged:: 4.2
       Now accepts positional arguments in addition to keyword arguments.
    """

    @classmethod
    def configure(cls, impl, **kwargs):
        # type: (Union[None, str, Type[Configurable]], Any) -> None
        """Sets the class to use when the base class is instantiated.

        Keyword arguments will be saved and added to the arguments passed
        to the constructor.  This can be used to set global defaults for
        some parameters.
        """
        base = cls.configurable_base()
        if isinstance(impl, str):
            impl = typing.cast(Type[Configurable], import_object(impl))
        if impl is not None and not issubclass(impl, cls):
            raise ValueError("Invalid subclass of %s" % cls)
        base.__impl_class = impl
        base.__impl_kwargs = kwargs

    @classmethod
    def configured_class(cls):
        # type: () -> Type[Configurable]
        """Returns the currently configured class."""
        base = cls.configurable_base()
        # Manually mangle the private name to see whether this base
```
