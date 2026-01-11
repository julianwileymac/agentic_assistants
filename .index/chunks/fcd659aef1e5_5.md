# Chunk: fcd659aef1e5_5

- source: `.venv-lab/Lib/site-packages/tornado/util.py`
- lines: 373-446
- chunk: 6/6

```
argument without replacing it.

        Returns ``default`` if the argument is not present.
        """
        if self.arg_pos is not None and len(args) > self.arg_pos:
            return args[self.arg_pos]
        else:
            return kwargs.get(self.name, default)

    def replace(
        self, new_value: Any, args: Sequence[Any], kwargs: Dict[str, Any]
    ) -> Tuple[Any, Sequence[Any], Dict[str, Any]]:
        """Replace the named argument in ``args, kwargs`` with ``new_value``.

        Returns ``(old_value, args, kwargs)``.  The returned ``args`` and
        ``kwargs`` objects may not be the same as the input objects, or
        the input objects may be mutated.

        If the named argument was not found, ``new_value`` will be added
        to ``kwargs`` and None will be returned as ``old_value``.
        """
        if self.arg_pos is not None and len(args) > self.arg_pos:
            # The arg to replace is passed positionally
            old_value = args[self.arg_pos]
            args = list(args)  # *args is normally a tuple
            args[self.arg_pos] = new_value
        else:
            # The arg to replace is either omitted or passed by keyword.
            old_value = kwargs.get(self.name)
            kwargs[self.name] = new_value
        return old_value, args, kwargs


def timedelta_to_seconds(td):
    # type: (datetime.timedelta) -> float
    """Equivalent to ``td.total_seconds()`` (introduced in Python 2.7)."""
    return td.total_seconds()


def _websocket_mask_python(mask: bytes, data: bytes) -> bytes:
    """Websocket masking function.

    `mask` is a `bytes` object of length 4; `data` is a `bytes` object of any length.
    Returns a `bytes` object of the same length as `data` with the mask applied
    as specified in section 5.3 of RFC 6455.

    This pure-python implementation may be replaced by an optimized version when available.
    """
    mask_arr = array.array("B", mask)
    unmasked_arr = array.array("B", data)
    for i in range(len(data)):
        unmasked_arr[i] = unmasked_arr[i] ^ mask_arr[i % 4]
    return unmasked_arr.tobytes()


if os.environ.get("TORNADO_NO_EXTENSION") or os.environ.get("TORNADO_EXTENSION") == "0":
    # These environment variables exist to make it easier to do performance
    # comparisons; they are not guaranteed to remain supported in the future.
    _websocket_mask = _websocket_mask_python
else:
    try:
        from tornado.speedups import websocket_mask as _websocket_mask
    except ImportError:
        if os.environ.get("TORNADO_EXTENSION") == "1":
            raise
        _websocket_mask = _websocket_mask_python


def doctests():
    # type: () -> unittest.TestSuite
    import doctest

    return doctest.DocTestSuite()
```
