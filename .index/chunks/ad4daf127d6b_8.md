# Chunk: ad4daf127d6b_8

- source: `.venv-lab/Lib/site-packages/tornado/iostream.py`
- lines: 588-655
- chunk: 9/25

```
      self.error = exc_info[1]
            if self._read_until_close:
                self._read_until_close = False
                self._finish_read(self._read_buffer_size)
            elif self._read_future is not None:
                # resolve reads that are pending and ready to complete
                try:
                    pos = self._find_read_pos()
                except UnsatisfiableReadError:
                    pass
                else:
                    if pos is not None:
                        self._read_from_buffer(pos)
            if self._state is not None:
                self.io_loop.remove_handler(self.fileno())
                self._state = None
            self.close_fd()
            self._closed = True
        self._signal_closed()

    def _signal_closed(self) -> None:
        futures = []  # type: List[Future]
        if self._read_future is not None:
            futures.append(self._read_future)
            self._read_future = None
        futures += [future for _, future in self._write_futures]
        self._write_futures.clear()
        if self._connect_future is not None:
            futures.append(self._connect_future)
            self._connect_future = None
        for future in futures:
            if not future.done():
                future.set_exception(StreamClosedError(real_error=self.error))
            # Reference the exception to silence warnings. Annoyingly,
            # this raises if the future was cancelled, but just
            # returns any other error.
            try:
                future.exception()
            except asyncio.CancelledError:
                pass
        if self._ssl_connect_future is not None:
            # _ssl_connect_future expects to see the real exception (typically
            # an ssl.SSLError), not just StreamClosedError.
            if not self._ssl_connect_future.done():
                if self.error is not None:
                    self._ssl_connect_future.set_exception(self.error)
                else:
                    self._ssl_connect_future.set_exception(StreamClosedError())
            self._ssl_connect_future.exception()
            self._ssl_connect_future = None
        if self._close_callback is not None:
            cb = self._close_callback
            self._close_callback = None
            self.io_loop.add_callback(cb)
        # Clear the buffers so they can be cleared immediately even
        # if the IOStream object is kept alive by a reference cycle.
        # TODO: Clear the read buffer too; it currently breaks some tests.
        self._write_buffer = None  # type: ignore

    def reading(self) -> bool:
        """Returns ``True`` if we are currently reading from the stream."""
        return self._read_future is not None

    def writing(self) -> bool:
        """Returns ``True`` if we are currently writing to the stream."""
        return bool(self._write_buffer)

```
