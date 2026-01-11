# Chunk: ad4daf127d6b_1

- source: `.venv-lab/Lib/site-packages/tornado/iostream.py`
- lines: 84-177
- chunk: 2/25

```
r(IOError):
    """Exception raised by `IOStream` methods when the stream is closed.

    Note that the close callback is scheduled to run *after* other
    callbacks on the stream (to allow for buffered data to be processed),
    so you may see this error before you see the close callback.

    The ``real_error`` attribute contains the underlying error that caused
    the stream to close (if any).

    .. versionchanged:: 4.3
       Added the ``real_error`` attribute.
    """

    def __init__(self, real_error: Optional[BaseException] = None) -> None:
        super().__init__("Stream is closed")
        self.real_error = real_error


class UnsatisfiableReadError(Exception):
    """Exception raised when a read cannot be satisfied.

    Raised by ``read_until`` and ``read_until_regex`` with a ``max_bytes``
    argument.
    """

    pass


class StreamBufferFullError(Exception):
    """Exception raised by `IOStream` methods when the buffer is full."""


class _StreamBuffer:
    """
    A specialized buffer that tries to avoid copies when large pieces
    of data are encountered.
    """

    def __init__(self) -> None:
        # A sequence of (False, bytearray) and (True, memoryview) objects
        self._buffers = (
            collections.deque()
        )  # type: Deque[Tuple[bool, Union[bytearray, memoryview]]]
        # Position in the first buffer
        self._first_pos = 0
        self._size = 0

    def __len__(self) -> int:
        return self._size

    # Data above this size will be appended separately instead
    # of extending an existing bytearray
    _large_buf_threshold = 2048

    def append(self, data: Union[bytes, bytearray, memoryview]) -> None:
        """
        Append the given piece of data (should be a buffer-compatible object).
        """
        size = len(data)
        if size > self._large_buf_threshold:
            if not isinstance(data, memoryview):
                data = memoryview(data)
            self._buffers.append((True, data))
        elif size > 0:
            if self._buffers:
                is_memview, b = self._buffers[-1]
                new_buf = is_memview or len(b) >= self._large_buf_threshold
            else:
                new_buf = True
            if new_buf:
                self._buffers.append((False, bytearray(data)))
            else:
                b += data  # type: ignore

        self._size += size

    def peek(self, size: int) -> memoryview:
        """
        Get a view over at most ``size`` bytes (possibly fewer) at the
        current buffer position.
        """
        assert size > 0
        try:
            is_memview, b = self._buffers[0]
        except IndexError:
            return memoryview(b"")

        pos = self._first_pos
        if is_memview:
            return typing.cast(memoryview, b[pos : pos + size])
        else:
            return memoryview(b)[pos : pos + size]
```
