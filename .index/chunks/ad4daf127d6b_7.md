# Chunk: ad4daf127d6b_7

- source: `.venv-lab/Lib/site-packages/tornado/iostream.py`
- lines: 519-594
- chunk: 8/25

```
 removed. Use the returned
           `.Future` instead.

        """
        self._check_closed()
        if data:
            if isinstance(data, memoryview):
                # Make sure that ``len(data) == data.nbytes``
                data = memoryview(data).cast("B")
            if (
                self.max_write_buffer_size is not None
                and len(self._write_buffer) + len(data) > self.max_write_buffer_size
            ):
                raise StreamBufferFullError("Reached maximum write buffer size")
            self._write_buffer.append(data)
            self._total_write_index += len(data)
        future = Future()  # type: Future[None]
        future.add_done_callback(lambda f: f.exception())
        self._write_futures.append((self._total_write_index, future))
        if not self._connecting:
            self._handle_write()
            if self._write_buffer:
                self._add_io_state(self.io_loop.WRITE)
            self._maybe_add_error_listener()
        return future

    def set_close_callback(self, callback: Optional[Callable[[], None]]) -> None:
        """Call the given callback when the stream is closed.

        This mostly is not necessary for applications that use the
        `.Future` interface; all outstanding ``Futures`` will resolve
        with a `StreamClosedError` when the stream is closed. However,
        it is still useful as a way to signal that the stream has been
        closed while no other read or write is in progress.

        Unlike other callback-based interfaces, ``set_close_callback``
        was not removed in Tornado 6.0.
        """
        self._close_callback = callback
        self._maybe_add_error_listener()

    def close(
        self,
        exc_info: Union[
            None,
            bool,
            BaseException,
            Tuple[
                "Optional[Type[BaseException]]",
                Optional[BaseException],
                Optional[TracebackType],
            ],
        ] = False,
    ) -> None:
        """Close this stream.

        If ``exc_info`` is true, set the ``error`` attribute to the current
        exception from `sys.exc_info` (or if ``exc_info`` is a tuple,
        use that instead of `sys.exc_info`).
        """
        if not self.closed():
            if exc_info:
                if isinstance(exc_info, tuple):
                    self.error = exc_info[1]
                elif isinstance(exc_info, BaseException):
                    self.error = exc_info
                else:
                    exc_info = sys.exc_info()
                    if any(exc_info):
                        self.error = exc_info[1]
            if self._read_until_close:
                self._read_until_close = False
                self._finish_read(self._read_buffer_size)
            elif self._read_future is not None:
                # resolve reads that are pending and ready to complete
```
