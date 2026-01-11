# Chunk: ad4daf127d6b_3

- source: `.venv-lab/Lib/site-packages/tornado/iostream.py`
- lines: 244-311
- chunk: 4/25

```
oop`` argument (deprecated since version 4.1) has been
           removed.
        """
        self.io_loop = ioloop.IOLoop.current()
        self.max_buffer_size = max_buffer_size or 104857600
        # A chunk size that is too close to max_buffer_size can cause
        # spurious failures.
        self.read_chunk_size = min(read_chunk_size or 65536, self.max_buffer_size // 2)
        self.max_write_buffer_size = max_write_buffer_size
        self.error = None  # type: Optional[BaseException]
        self._read_buffer = bytearray()
        self._read_buffer_size = 0
        self._user_read_buffer = False
        self._after_user_read_buffer = None  # type: Optional[bytearray]
        self._write_buffer = _StreamBuffer()
        self._total_write_index = 0
        self._total_write_done_index = 0
        self._read_delimiter = None  # type: Optional[bytes]
        self._read_regex = None  # type: Optional[Pattern]
        self._read_max_bytes = None  # type: Optional[int]
        self._read_bytes = None  # type: Optional[int]
        self._read_partial = False
        self._read_until_close = False
        self._read_future = None  # type: Optional[Future]
        self._write_futures = (
            collections.deque()
        )  # type: Deque[Tuple[int, Future[None]]]
        self._close_callback = None  # type: Optional[Callable[[], None]]
        self._connect_future = None  # type: Optional[Future[IOStream]]
        # _ssl_connect_future should be defined in SSLIOStream
        # but it's here so we can clean it up in _signal_closed
        # TODO: refactor that so subclasses can add additional futures
        # to be cancelled.
        self._ssl_connect_future = None  # type: Optional[Future[SSLIOStream]]
        self._connecting = False
        self._state = None  # type: Optional[int]
        self._closed = False

    def fileno(self) -> Union[int, ioloop._Selectable]:
        """Returns the file descriptor for this stream."""
        raise NotImplementedError()

    def close_fd(self) -> None:
        """Closes the file underlying this stream.

        ``close_fd`` is called by `BaseIOStream` and should not be called
        elsewhere; other users should call `close` instead.
        """
        raise NotImplementedError()

    def write_to_fd(self, data: memoryview) -> int:
        """Attempts to write ``data`` to the underlying file.

        Returns the number of bytes written.
        """
        raise NotImplementedError()

    def read_from_fd(self, buf: Union[bytearray, memoryview]) -> Optional[int]:
        """Attempts to read from the underlying file.

        Reads up to ``len(buf)`` bytes, storing them in the buffer.
        Returns the number of bytes read. Returns None if there was
        nothing to read (the socket returned `~errno.EWOULDBLOCK` or
        equivalent), and zero on EOF.

        .. versionchanged:: 5.0

```
