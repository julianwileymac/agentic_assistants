# Chunk: ad4daf127d6b_2

- source: `.venv-lab/Lib/site-packages/tornado/iostream.py`
- lines: 167-251
- chunk: 3/25

```

            is_memview, b = self._buffers[0]
        except IndexError:
            return memoryview(b"")

        pos = self._first_pos
        if is_memview:
            return typing.cast(memoryview, b[pos : pos + size])
        else:
            return memoryview(b)[pos : pos + size]

    def advance(self, size: int) -> None:
        """
        Advance the current buffer position by ``size`` bytes.
        """
        assert 0 < size <= self._size
        self._size -= size
        pos = self._first_pos

        buffers = self._buffers
        while buffers and size > 0:
            is_large, b = buffers[0]
            b_remain = len(b) - size - pos
            if b_remain <= 0:
                buffers.popleft()
                size -= len(b) - pos
                pos = 0
            elif is_large:
                pos += size
                size = 0
            else:
                pos += size
                del typing.cast(bytearray, b)[:pos]
                pos = 0
                size = 0

        assert size == 0
        self._first_pos = pos


class BaseIOStream:
    """A utility class to write to and read from a non-blocking file or socket.

    We support a non-blocking ``write()`` and a family of ``read_*()``
    methods. When the operation completes, the ``Awaitable`` will resolve
    with the data read (or ``None`` for ``write()``). All outstanding
    ``Awaitables`` will resolve with a `StreamClosedError` when the
    stream is closed; `.BaseIOStream.set_close_callback` can also be used
    to be notified of a closed stream.

    When a stream is closed due to an error, the IOStream's ``error``
    attribute contains the exception object.

    Subclasses must implement `fileno`, `close_fd`, `write_to_fd`,
    `read_from_fd`, and optionally `get_fd_error`.

    """

    def __init__(
        self,
        max_buffer_size: Optional[int] = None,
        read_chunk_size: Optional[int] = None,
        max_write_buffer_size: Optional[int] = None,
    ) -> None:
        """`BaseIOStream` constructor.

        :arg max_buffer_size: Maximum amount of incoming data to buffer;
            defaults to 100MB.
        :arg read_chunk_size: Amount of data to read at one time from the
            underlying transport; defaults to 64KB.
        :arg max_write_buffer_size: Amount of outgoing data to buffer;
            defaults to unlimited.

        .. versionchanged:: 4.0
           Add the ``max_write_buffer_size`` parameter.  Changed default
           ``read_chunk_size`` to 64KB.
        .. versionchanged:: 5.0
           The ``io_loop`` argument (deprecated since version 4.1) has been
           removed.
        """
        self.io_loop = ioloop.IOLoop.current()
        self.max_buffer_size = max_buffer_size or 104857600
        # A chunk size that is too close to max_buffer_size can cause
        # spurious failures.
```
