# Chunk: fcd659aef1e5_1

- source: `.venv-lab/Lib/site-packages/tornado/util.py`
- lines: 88-172
- chunk: 2/6

```
  If ``max_length`` is given, some input data may be left over
        in ``unconsumed_tail``; you must retrieve this value and pass
        it back to a future call to `decompress` if it is not empty.
        """
        return self.decompressobj.decompress(value, max_length)

    @property
    def unconsumed_tail(self) -> bytes:
        """Returns the unconsumed portion left over"""
        return self.decompressobj.unconsumed_tail

    def flush(self) -> bytes:
        """Return any remaining buffered data not yet returned by decompress.

        Also checks for errors such as truncated input.
        No other methods may be called on this object after `flush`.
        """
        return self.decompressobj.flush()


def import_object(name: str) -> Any:
    """Imports an object by name.

    ``import_object('x')`` is equivalent to ``import x``.
    ``import_object('x.y.z')`` is equivalent to ``from x.y import z``.

    >>> import tornado.escape
    >>> import_object('tornado.escape') is tornado.escape
    True
    >>> import_object('tornado.escape.utf8') is tornado.escape.utf8
    True
    >>> import_object('tornado') is tornado
    True
    >>> import_object('tornado.missing_module')
    Traceback (most recent call last):
        ...
    ImportError: No module named missing_module
    """
    if name.count(".") == 0:
        return __import__(name)

    parts = name.split(".")
    obj = __import__(".".join(parts[:-1]), fromlist=[parts[-1]])
    try:
        return getattr(obj, parts[-1])
    except AttributeError:
        raise ImportError("No module named %s" % parts[-1])


def exec_in(
    code: Any, glob: Dict[str, Any], loc: Optional[Optional[Mapping[str, Any]]] = None
) -> None:
    if isinstance(code, str):
        # exec(string) inherits the caller's future imports; compile
        # the string first to prevent that.
        code = compile(code, "<string>", "exec", dont_inherit=True)
    exec(code, glob, loc)


def raise_exc_info(
    exc_info: Tuple[Optional[type], Optional[BaseException], Optional["TracebackType"]]
) -> typing.NoReturn:
    try:
        if exc_info[1] is not None:
            raise exc_info[1].with_traceback(exc_info[2])
        else:
            raise TypeError("raise_exc_info called with no exception")
    finally:
        # Clear the traceback reference from our stack frame to
        # minimize circular references that slow down GC.
        exc_info = (None, None, None)


def errno_from_exception(e: BaseException) -> Optional[int]:
    """Provides the errno from an Exception object.

    There are cases that the errno attribute was not set so we pull
    the errno out of the args but if someone instantiates an Exception
    without any args you will get a tuple error. So this function
    abstracts all that behavior to give you a safe way to get the
    errno.
    """

    if hasattr(e, "errno"):
```
